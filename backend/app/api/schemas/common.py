from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
