from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class FECPagination(BaseModel):
    page: int
    pages: int
    per_page: int
    count: int

class FECResponse(BaseModel):
    api_version: str
    pagination: Optional[FECPagination] = None
    results: List[Dict[str, Any]]
