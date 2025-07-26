import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.models.confluence_models import PageCreate, PageUpdate


class ConfluenceService:
    def __init__(self):
        self.api_url = f"{settings.CONFLUENCE_URL}/rest/api"
        self.auth = (settings.CONFLUENCE_USER, settings.CONFLUENCE_API_TOKEN)

    async def create_page(self, page_data: PageCreate) -> dict:
        """Confluence에 새 페이지를 생성합니다."""
        url = f"{self.api_url}/content"
        
        payload = {
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
            payload["ancestors"] = [{"id": page_data.parent_id}]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, auth=self.auth)
                response.raise_for_status()  # 2xx가 아니면 예외 발생
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Confluence API 오류: {e.response.text}"
                )

    async def get_page(self, page_id: str) -> dict:
        """ID로 특정 Confluence 페이지 정보를 가져옵니다 (버전 정보 포함)."""
        url = f"{self.api_url}/content/{page_id}?expand=version"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, auth=self.auth)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Page with ID '{page_id}' not found.")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Confluence API 오류: {e.response.text}"
                )

    async def update_page(self, page_id: str, page_data: PageUpdate) -> dict:
        """Confluence 페이지를 업데이트합니다."""
        if page_data.version:
            # 클라이언트에서 버전 정보를 제공한 경우
            next_version = page_data.version + 1
        else:
            # 버전 정보가 없으면 API를 통해 현재 버전을 조회합니다. (기존 방식 유지)
            current_page = await self.get_page(page_id)
            current_version = current_page["version"]["number"]
            next_version = current_version + 1

        url = f"{self.api_url}/content/{page_id}"
        
        payload = {
            "version": {"number": next_version},
            "type": "page",
            "title": page_data.title,
            "body": {"storage": {"value": page_data.content, "representation": "storage"}},
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, json=payload, auth=self.auth)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=f"Confluence API 오류: {e.response.text}")

    async def delete_page(self, page_id: str):
        """Confluence 페이지를 삭제합니다."""
        url = f"{self.api_url}/content/{page_id}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(url, auth=self.auth)
                response.raise_for_status()  # 성공 시 204 No Content 반환
                return
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Page with ID '{page_id}' not found.")
                raise HTTPException(status_code=e.response.status_code, detail=f"Confluence API 오류: {e.response.text}")

    async def search_pages(self, cql: str, expand: str | None = None) -> dict:
        """CQL을 사용하여 Confluence 페이지를 검색합니다."""
        url = f"{self.api_url}/content/search"
        params = {"cql": cql}
        if expand:
            params["expand"] = expand
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, auth=self.auth)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=f"Confluence API 오류: {e.response.text}")

confluence_service = ConfluenceService()
