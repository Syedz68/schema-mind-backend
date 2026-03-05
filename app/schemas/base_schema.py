from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None

class EmptyData(BaseModel):
    pass