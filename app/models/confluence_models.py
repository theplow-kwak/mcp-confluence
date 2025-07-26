from pydantic import BaseModel
from typing import Optional


class PageCreate(BaseModel):
    space_key: str
    title: str
    content: str
    parent_id: Optional[str] = None


class PageUpdate(BaseModel):
    title: str
    content: str
    version: Optional[int] = None
