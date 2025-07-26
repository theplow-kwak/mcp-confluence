from fastapi import FastAPI, Depends, Response, status
from typing import Optional

from app.models.confluence_models import PageCreate, PageUpdate, LLMQuery, PagePublish
from app.services.confluence_service import confluence_service, ConfluenceService
from app.services.base_service import BaseLLMService
from app.services.llm_factory import get_llm_service

app = FastAPI(
    title="MCP Server for Confluence",
    description="Confluence 자동화 및 통합을 위한 미들웨어 서버",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to MCP Server for Confluence"}


@app.post("/pages", status_code=201)
async def create_confluence_page(page: PageCreate, service: ConfluenceService = Depends(lambda: confluence_service)):
    """새로운 Confluence 페이지를 생성합니다."""
    created_page = await service.create_page(page)
    return created_page


@app.post("/pages/publish", status_code=201, summary="Publish Draft Page")
async def publish_confluence_page(page_data: PagePublish, service: ConfluenceService = Depends(lambda: confluence_service)):
    """
    게시할 페이지 데이터를 받아 Confluence 페이지를 생성합니다.
    (LLM이 생성한 초안을 사용자가 확인 후 게시할 때 사용)
    """
    page = PageCreate(space_key=page_data.space_key, title=page_data.title, content=page_data.content)
    created_page = await service.create_page(page)
    return created_page


@app.get("/pages/search")
async def search_confluence_pages(cql: str, expand: Optional[str] = None, service: ConfluenceService = Depends(lambda: confluence_service)):
    """
    CQL(Confluence Query Language)을 사용하여 페이지를 검색합니다.

    **예시 CQL:**
    - `space = "DEV" and title ~ "회의록"`
    - `label = "release-note" and ancestor = 12345`

    **확장(expand):**
    - `version,body.storage` 와 같이 추가 정보를 요청할 수 있습니다.
    """
    search_results = await service.search_pages(cql, expand)
    return search_results


@app.put("/pages/{page_id}")
async def update_confluence_page(page_id: str, page: PageUpdate, service: ConfluenceService = Depends(lambda: confluence_service)):
    """ID로 특정 Confluence 페이지를 업데이트합니다."""
    updated_page = await service.update_page(page_id, page)
    return updated_page


@app.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_confluence_page(page_id: str, service: ConfluenceService = Depends(lambda: confluence_service)):
    """ID로 특정 Confluence 페이지를 삭제합니다."""
    await service.delete_page(page_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/llm/execute")
async def execute_llm_task(query: LLMQuery, service: BaseLLMService = Depends(get_llm_service)):
    """
    LLM을 사용하여 자연어 명령을 처리합니다.
    
    - 일반적인 질문에는 텍스트로 답변합니다.
    - 보고서 생성 요청 시에는, 검토를 위한 'report_draft' 객체를 반환할 수 있습니다.
    - `session_id`를 포함하여 연속적인 대화를 할 수 있습니다. 첫 요청 시 `session_id`는 생략합니다.
    """
    result = await service.process_query(query.prompt, query.session_id)
    return result
