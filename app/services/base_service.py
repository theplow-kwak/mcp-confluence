from abc import ABC, abstractmethod


class BaseLLMService(ABC):
    """
    모든 LLM 서비스가 따라야 하는 공통 인터페이스를 정의하는 추상 기본 클래스입니다.
    """
    @abstractmethod
    async def process_query(self, query: str, session_id: str | None = None) -> dict:
        pass