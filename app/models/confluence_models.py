from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# --- Confluence API 관련 모델 ---

class PageCreate(BaseModel):
    """페이지 생성을 위한 모델"""
    space_key: str = Field(..., description="Confluence 스페이스 키", examples=["DEV"])
    title: str = Field(..., description="페이지 제목", examples=["새로운 기능 회의록"])
    content: str = Field(..., description="페이지 내용 (HTML 또는 Storage 포맷)", examples=["<p>회의 내용을 기록합니다.</p>"])
    parent_id: Optional[str] = Field(None, description="부모 페이지 ID", examples=["12345"])

class PageUpdate(BaseModel):
    """페이지 업데이트를 위한 모델"""
    title: str = Field(..., description="새로운 페이지 제목")
    content: str = Field(..., description="새로운 페이지 내용 (HTML 또는 Storage 포맷)")

class PagePublish(BaseModel):
    """LLM이 생성한 초안을 게시하기 위한 모델"""
    space_key: str = Field(..., description="Confluence 스페이스 키")
    title: str = Field(..., description="페이지 제목")
    content: str = Field(..., description="게시할 페이지 내용")

# --- LLM 상호작용 관련 모델 ---

class LLMQuery(BaseModel):
    """LLM에 작업을 요청하는 모델"""
    prompt: str = Field(..., description="LLM에게 전달할 자연어 프롬프트", examples=["어제자 QA팀 주간 보고서를 요약해서 초안을 작성해줘."])
    session_id: Optional[str] = Field(None, description="연속적인 대화를 위한 세션 ID")

class ReportDraft(BaseModel):
    """LLM이 생성한 보고서 초안 모델"""
    title: str
    content: str
    space_key: Optional[str] = None
    parent_id: Optional[str] = None

class LLMResponse(BaseModel):
    """LLM의 처리 결과를 담는 모델"""
    response_type: str = Field(..., description="응답 유형 (e.g., 'text', 'report_draft')")
    data: Dict[str, Any] | ReportDraft | str
    session_id: Optional[str] = None