from fastapi import Depends, HTTPException

from app.core.config import Settings, settings
from .base_service import BaseLLMService
from .gemini_service import GeminiService
from .openai_service import OpenAIService


def get_llm_service(config: Settings = Depends(lambda: settings)) -> BaseLLMService:
    """
    FastAPI 의존성 주입용 팩토리 함수.
    설정(LLM_PROVIDER)에 따라 적절한 LLM 서비스 인스턴스를 반환합니다.
    """
    provider = config.LLM_PROVIDER.lower()

    if provider == "gemini":
        return GeminiService()
    elif provider == "openai":
        return OpenAIService()
    else:
        raise HTTPException(
            status_code=501, detail=f"LLM provider '{provider}' is not implemented."
        )