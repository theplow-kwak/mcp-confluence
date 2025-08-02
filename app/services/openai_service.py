from openai import AsyncOpenAI
from typing import Optional, Dict, Any

from app.core.config import settings
from .base_service import BaseLLMService

class OpenAIService(BaseLLMService):
    """
    OpenAI 모델을 사용하여 LLM 기능을 제공하는 서비스.
    """
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is not set in the environment.")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"  # 최신 모델 사용

    async def process_query(self, prompt: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        OpenAI 모델을 사용하여 사용자의 프롬프트를 처리하고 응답을 생성합니다.
        (현재는 간단한 텍스트 생성만 구현)
        """
        # TODO: 실제로는 여기서 프롬프트를 분석하여 Confluence API 호출 등
        #       더 복잡한 작업을 수행해야 함 (예: Function Calling)
        
        # 대화 기록을 포함하여 요청 (세션 관리 필요 시)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2000
        )
        
        return {"response": response.choices[0].message.content.strip()}
