from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class APIResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
