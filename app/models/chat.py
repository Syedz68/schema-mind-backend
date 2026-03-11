from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.utils.enums import ChatRole, LlmMode

class ChatSession(Base):
    __tablename__ = "chat_session"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    db_connection_id = Column(Integer, ForeignKey("db_connection.id", ondelete="CASCADE"), nullable=False)
    llm_mode = Column(Enum(LlmMode, native_enum=False), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="sessions")
    db_connection = relationship("DbConnection", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(ChatRole, native_enum=False, length=20), nullable=False)
    content = Column(Text)
    generated_sql = Column(Text)
    query_result = Column(JSONB)
    execution_time = Column(Float)
    success = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("ChatSession", back_populates="messages")