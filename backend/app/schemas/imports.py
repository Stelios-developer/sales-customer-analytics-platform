from pydantic import BaseModel
from typing import List, Optional


class ImportResponse(BaseModel):
    status: str
    filename: str
    rows_processed: int
    rows_inserted: int
    rows_failed: int
    warnings: List[str]
    errors: List[str] = []
