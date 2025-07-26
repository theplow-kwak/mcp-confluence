import google.generativeai as genai
import json
from fastapi import HTTPException

from app.core.config import settings
from app.services.confluence_service import confluence_service
from app.services.tool_definitions import confluence_tools
from app.models.confluence_models import PageCreate, PageUpdate


class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[confluence_tools]
        )
        # 실제 함수와 도구 이름을 매핑
        self.tool_function_map = {
            "search_pages": self.execute_search,
            "create_page": self.execute_create,
            "update_page": self.execute_update,
            "create_summary_report": self.execute_create_summary_report,
        }

    async def process_query(self, query: str) -> str:
        """사용자 쿼리를 받아 LLM과 상호작용하며 작업을 처리합니다."""
        chat = self.model.start_chat()
        response = chat.send_message(query)

        while response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls
            
            api_responses = []
            for call in function_calls:
                func_name = call.name
                func_args = call.args
                
                if func_name in self.tool_function_map:
                    # 매핑된 함수를 비동기로 실행
                    result = await self.tool_function_map[func_name](**func_args)
                    api_responses.append(
                        {"function_name": func_name, "response": {"content": result}}
                    )
            
            # 함수의 실행 결과를 다시 LLM에게 보냄
            response = chat.send_message(
                part=genai.protos.Part(function_response=genai.protos.FunctionResponse(name=func_name, response={"content": json.dumps(api_responses, ensure_ascii=False)})),
            )

        return response.text

    async def execute_search(self, cql: str) -> dict:
        """search_pages 도구를 실행합니다."""
        # 업데이트 및 요약을 위해 항상 본문과 버전 정보를 함께 가져옵니다.
        return await confluence_service.search_pages(cql, expand="body.storage,version")

    async def execute_create(self, space_key: str, title: str, content: str, parent_id: str = None) -> dict:
        """create_page 도구를 실행합니다."""
        page_data = PageCreate(space_key=space_key, title=title, content=content, parent_id=parent_id)
        return await confluence_service.create_page(page_data)

    async def execute_update(self, page_id: str, title: str, content: str, version: int) -> dict:
        """update_page 도구를 실행합니다."""
        page_data = PageUpdate(title=title, content=content, version=version)
        return await confluence_service.update_page(page_id, page_data)

    async def execute_create_summary_report(self, cql: str, space_key: str, report_title: str, summary_prompt: str) -> dict:
        """요약 보고서 생성 도구를 실행합니다 (검색 -> 요약 -> 생성)."""
        # 1. 페이지 검색
        print(f"보고서 생성을 위해 페이지 검색 중... (CQL: {cql})")
        search_result = await self.execute_search(cql)
        pages = search_result.get("results", [])

        if not pages:
            return {"status": "failed", "message": "요약할 페이지를 찾지 못했습니다."}

        # 2. 내용 취합
        content_to_summarize = ""
        for page in pages:
            title = page.get("title", "제목 없음")
            content = page.get("body", {}).get("storage", {}).get("value", "")
            content_to_summarize += f"<h2>{title}</h2>\n{content}\n\n<hr/>\n\n"

        # 3. LLM을 통한 요약 생성 (별도의 LLM 호출)
        print("검색된 내용을 바탕으로 요약 생성 중...")
        summarizer_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        full_prompt = f"""
        다음은 여러 Confluence 페이지의 내용입니다.
        ---
        {content_to_summarize}
        ---
        위 내용을 바탕으로 다음 요구사항에 맞춰 요약 보고서를 작성해주세요: "{summary_prompt}"
        """
        summary_response = await summarizer_model.generate_content_async(full_prompt)

        # 4. 요약된 내용으로 새 페이지 생성
        print(f"'{report_title}' 제목으로 최종 보고서 페이지 생성 중...")
        return await self.execute_create(space_key=space_key, title=report_title, content=summary_response.text)

llm_service = LLMService()