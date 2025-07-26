import openai
import json
import uuid
from typing import List, Dict

from app.core.config import settings
from app.services.confluence_service import confluence_service
from app.services.openai_tool_definitions import confluence_tools_openai
from app.models.confluence_models import PageCreate, PageUpdate
from .base_service import BaseLLMService


class OpenAIService(BaseLLMService):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = "gpt-4-turbo-preview"  # 함수 호출을 지원하는 모델
        self.chats: Dict[str, List[Dict[str, str]]] = {}  # 메모리 기반 채팅 세션 저장소

        self.tool_function_map = {
            "search_pages": self.execute_search,
            "create_page": self.execute_create,
            "update_page": self.execute_update,
            "draft_summary_report": self.execute_draft_summary_report,
        }

    async def process_query(self, query: str, session_id: str | None = None) -> dict:
        if session_id and session_id in self.chats:
            messages = self.chats[session_id]
            messages.append({"role": "user", "content": query})
        else:
            session_id = str(uuid.uuid4())
            system_prompt = "You are a helpful assistant that can interact with Confluence. Use the provided tools to answer user requests."
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=confluence_tools_openai,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name in self.tool_function_map:
                    function_response = await self.tool_function_map[function_name](**function_args)

                    if function_name == "draft_summary_report":
                        return {"session_id": session_id, "response": function_response}

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response, ensure_ascii=False),
                    })
            
            second_response = await self.client.chat.completions.create(model=self.model_name, messages=messages)
            final_response = second_response.choices[0].message.content
            messages.append({"role": "assistant", "content": final_response})
            self.chats[session_id] = messages
            return {"session_id": session_id, "response": final_response}
        else:
            final_response = response_message.content
            messages.append({"role": "assistant", "content": final_response})
            self.chats[session_id] = messages
            return {"session_id": session_id, "response": final_response}

    async def execute_search(self, cql: str) -> dict:
        return await confluence_service.search_pages(cql, expand="body.storage,version")

    async def execute_create(self, space_key: str, title: str, content: str, parent_id: str = None) -> dict:
        page_data = PageCreate(space_key=space_key, title=title, content=content, parent_id=parent_id)
        return await confluence_service.create_page(page_data)

    async def execute_update(self, page_id: str, title: str, content: str, version: int) -> dict:
        page_data = PageUpdate(title=title, content=content, version=version)
        return await confluence_service.update_page(page_id, page_data)

    async def execute_draft_summary_report(self, cql: str, space_key: str, report_title: str, summary_prompt: str) -> dict:
        search_result = await self.execute_search(cql)
        pages = search_result.get("results", [])

        if not pages:
            return {"status": "failed", "message": "요약할 페이지를 찾지 못했습니다."}

        content_to_summarize = ""
        for page in pages:
            title = page.get("title", "제목 없음")
            content = page.get("body", {}).get("storage", {}).get("value", "")
            content_to_summarize += f"<h2>{title}</h2>\n{content}\n\n<hr/>\n\n"

        full_prompt = f"""
        다음은 여러 Confluence 페이지의 내용입니다.
        ---
        {content_to_summarize}
        ---
        위 내용을 바탕으로 다음 요구사항에 맞춰 요약 보고서를 작성해주세요: "{summary_prompt}"
        """
        summary_response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}]
        )
        summary_text = summary_response.choices[0].message.content

        return {
            "type": "report_draft",
            "space_key": space_key,
            "title": report_title,
            "content": summary_text,
        }