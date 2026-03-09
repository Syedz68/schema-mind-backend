from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict
from app.utils.enums import LlmMode, ChatRole
from datetime import datetime

class SessionCreate(BaseModel):
    db_connection_id: int
    llm_mode: LlmMode
    title: Optional[str] = None


class SessionUpdate(BaseModel):
    session_id: int
    llm_mode: Optional[LlmMode] = None
    title: Optional[str] = None


class SessionResponse(SessionCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SessionResponseList(BaseModel):
    session_list: list[SessionResponse]


class MessageCreate(BaseModel):
    session_id: int
    user_question: str


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: ChatRole
    content: Optional[str] = None
    generated_sql: Optional[str] = None
    query_result: Optional[Dict] = None
    execution_time: Optional[float] = None
    success: Optional[bool] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]