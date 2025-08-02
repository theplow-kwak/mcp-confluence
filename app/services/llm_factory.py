from fastapi import Depends, HTTPException

from app.core.config import Settings, settings
from .base_service import BaseLLMService
from .gemini_service import GeminiService
from .openai_service import OpenAIService
from .base_service import BaseLLMService
from app.core.config import settings

def get_llm_service() -> BaseLLMService:
    """
    설정에 따라 적절한 LLM 서비스 인스턴스를 반환합니다.
    """
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return GeminiService()
    elif provider == "openai":
        return OpenAIService()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
