from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.models.confluence_models import PageCreate, PageUpdate

class BaseConfluenceService(ABC):
    """Confluence 서비스의 기본 인터페이스를 정의하는 추상 클래스."""

    @abstractmethod
    async def get_page(self, page_id: str, expand: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def create_page(self, page_data: PageCreate) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def update_page(self, page_id: str, page_data: PageUpdate) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def delete_page(self, page_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search_pages(self, cql: str, expand: Optional[str] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError


class BaseLLMService(ABC):
    """LLM 서비스의 기본 인터페이스를 정의하는 추상 클래스."""

    @abstractmethod
    async def process_query(self, prompt: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        사용자의 쿼리를 처리하고, 적절한 Confluence 작업을 수행하거나 텍스트 응답을 반환합니다.
        세션 ID를 사용하여 대화의 연속성을 관리할 수 있습니다.
        """
        raise NotImplementedError
