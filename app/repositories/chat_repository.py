from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat_schema import SessionCreate, SessionUpdate, MessageCreate
from app.utils.enums import ChatRole

class ChatRepository:

    def __init__(self, db: Session):
        self.db = db

    # SESSION OPERATIONS

    def create_session(self, user_id: int, request: SessionCreate):
        new_session = ChatSession(
            user_id=user_id,
            db_connection_id=request.db_connection_id,
            llm_mode=request.llm_mode,
            title=request.title or "New Chat"
        )

        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)

        return new_session

    def get_session_by_id(self, session_id: int):
        session = (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return session

    def get_sessions_by_user(self, user_id: int, db_connection_id: int):
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id, ChatSession.db_connection_id == db_connection_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    def update_session(self, request: SessionUpdate):
        session = self.get_session_by_id(request.session_id)

        if request.llm_mode:
            session.llm_mode = request.llm_mode

        if request.title:
            session.title = request.title

        self.db.commit()
        self.db.refresh(session)

        return session

    def delete_session(self, session_id: int):
        session = self.get_session_by_id(session_id)

        self.db.delete(session)
        self.db.commit()

        return {"detail": "Session deleted successfully"}

    # MESSAGE OPERATIONS

    def create_message(
            self,
            session_id: int,
            role: ChatRole,
            content: str,
            generated_sql: str | None = None,
            query_result: dict | None = None,
            execution_time: float | None = None,
            success: bool | None = None
    ):
        new_message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            generated_sql=generated_sql,
            query_result=query_result,
            execution_time=execution_time,
            success=success
        )

        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)

        return new_message

    def get_messages_by_session(self, session_id: int):
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def get_last_messages(self, session_id: int, limit: int = 10):
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )