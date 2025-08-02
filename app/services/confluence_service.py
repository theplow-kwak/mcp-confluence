import httpx
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.models.confluence_models import PageCreate, PageUpdate
from .base_service import BaseConfluenceService

class ConfluenceService(BaseConfluenceService):
    """
    Confluence API와 비동기적으로 통신하는 서비스 클래스.
    """
    def __init__(self):
        self.base_url = f"{settings.confluence_url}/rest/api"
        self.auth = (settings.confluence_user, settings.confluence_api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Atlassian-Token": "no-check" # For PUT/POST requests
        }

    async def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, auth=self.auth, headers=self.headers, **kwargs)
            response.raise_for_status()
            # DELETE와 같이 내용이 없는 응답 처리
            if response.status_code == 204:
                return {}
            return response.json()

    async def get_page(self, page_id: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """ID로 특정 Confluence 페이지의 정보를 비동기적으로 조회합니다."""
        url = f"{self.base_url}/content/{page_id}"
        params = {}
        if expand:
            params['expand'] = expand
        return await self._request("GET", url, params=params)

    async def create_page(self, page_data: PageCreate) -> Dict[str, Any]:
        """새로운 Confluence 페이지를 비동기적으로 생성합니다."""
        url = f"{self.base_url}/content"
        json_data = {
            "type": "page",
            "title": page_data.title,
            "space": {"key": page_data.space_key},
            "body": {
                "storage": {
                    "value": page_data.content,
                    "representation": "storage"
                }
            }
        }
        if page_data.parent_id:
            json_data["ancestors"] = [{"id": page_data.parent_id}]
        
        return await self._request("POST", url, json=json_data)

    async def update_page(self, page_id: str, page_data: PageUpdate) -> Dict[str, Any]:
        """ID로 특정 Confluence 페이지를 비동기적으로 업데이트합니다."""
        # 최신 버전 정보를 얻기 위해 먼저 페이지 정보를 조회합니다.
        current_page = await self.get_page(page_id, expand="version")
        current_version = current_page['version']['number']

        url = f"{self.base_url}/content/{page_id}"
        json_data = {
            "version": {"number": current_version + 1},
            "title": page_data.title,
            "type": "page",
            "body": {
                "storage": {
                    "value": page_data.content,
                    "representation": "storage"
                }
            }
        }
        return await self._request("PUT", url, json=json_data)

    async def delete_page(self, page_id: str) -> None:
        """ID로 특정 Confluence 페이지를 비동기적으로 삭제합니다."""
        url = f"{self.base_url}/content/{page_id}"
        await self._request("DELETE", url)

    async def search_pages(self, cql: str, expand: Optional[str] = None) -> List[Dict[str, Any]]:
        """CQL을 사용하여 페이지를 비동기적으로 검색합니다."""
        url = f"{self.base_url}/content/search"
        params = {"cql": cql}
        if expand:
            params['expand'] = expand
        
        results = await self._request("GET", url, params=params)
        return results.get("results", [])

# FastAPI의 Depends에서 사용할 수 있도록 서비스 인스턴스 생성
confluence_service = ConfluenceService()