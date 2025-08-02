from app.core.config import settings
from .base_service import BaseLLMService
from .gemini_service import GeminiService
from .openai_service import OpenAIService

def get_llm_service() -> BaseLLMService:
    """
    설정에 따라 적절한 LLM 서비스 인스턴스를 반환합니다.
    """
    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini":
        return GeminiService()
    elif provider == "openai":
        return OpenAIService()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
