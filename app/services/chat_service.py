from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.engine_creator import get_engine
from app.core.query_guard import validate_query_permission
from app.llm.llm_factory import LLMFactory
from app.llm.prompt_builder import build_sql_prompt, build_answer_prompt, build_chat_title_prompt
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat_schema import *
from app.schemas.db_connection_schema import DbConnectEngineRequest
from app.utils.enums import Permission
from app.utils.sql_cleaner import clean_sql_response
from datetime import datetime, date
from decimal import Decimal
import time


class ChatService:
    def __init__(self, db: Session):
        self.repo = ChatRepository(db)

    def get_chat(self, session_id: int):
        chat = self.repo.get_session_by_id(session_id)

        return SessionResponse(
            id=chat.id,
            db_connection_id=chat.db_connection_id,
            llm_mode=chat.llm_mode,
            title=chat.title
        )

    def get_all_chats(self, user_id: int, db_connection_id: int):
        chats = self.repo.get_sessions_by_user(user_id, db_connection_id)

        chat_list = [
            SessionResponse(
                id=chat.id,
                db_connection_id=chat.db_connection_id,
                llm_mode=chat.llm_mode,
                title=chat.title
            )
            for chat in chats
        ]

        return SessionResponseList(session_list=chat_list)

    def create_chat(self, user_id: int, request: SessionCreate):
        chat = self.repo.create_session(user_id, request)

        return SessionResponse(
            id=chat.id,
            db_connection_id=chat.db_connection_id,
            llm_mode=chat.llm_mode,
            title=chat.title
        )

    def update_chat(self, request: SessionUpdate):
        chat = self.repo.update_session(request)

        return SessionResponse(
            id=chat.id,
            db_connection_id=chat.db_connection_id,
            llm_mode=chat.llm_mode,
            title=chat.title
        )

    def update_chat_title(self, request: MessageCreate):
        chat_session = self.repo.get_session_by_id(request.session_id)
        llm = LLMFactory.get_llm(chat_session.llm_mode)
        chat_title_prompt = build_chat_title_prompt(request.user_question)
        chat_title = llm.generate_title(chat_title_prompt)

        chat_update_payload = SessionUpdate(
            session_id=request.session_id,
            title=chat_title
        )

        updated_chat = self.repo.update_session(chat_update_payload)

        return SessionResponse(
            id=updated_chat.id,
            db_connection_id=updated_chat.db_connection_id,
            llm_mode=updated_chat.llm_mode,
            title=updated_chat.title
        )

    def delete_chat(self, session_id: int):
        self.repo.delete_session(session_id)
        return {"detail": "Chat session deleted successfully"}

    # Chat Messages

    def get_all_messages_for_chat(self, session_id: int):
        messages = self.repo.get_messages_by_session(session_id)

        message_list = [
            MessageResponse(
                id=mssg.id,
                session_id=mssg.session_id,
                role=mssg.role,
                content=mssg.content,
                generated_sql=mssg.generated_sql,
                query_result=mssg.query_result,
                execution_time=mssg.execution_time,
                success=mssg.success,
                created_at=mssg.created_at
            )
            for mssg in messages
        ]

        return MessageListResponse(messages=message_list)

    def serialize_row(self, row: dict) -> dict:
        return {
            key: value.isoformat() if isinstance(value, (datetime, date))
            else float(value) if isinstance(value, Decimal)
            else value
            for key, value in row.items()
        }

    def send_message(self, request: MessageCreate, permission: Permission):
        self.repo.create_message(session_id=request.session_id, role=ChatRole.user, content=request.user_question)

        chat_session = self.repo.get_session_by_id(request.session_id)

        db_conn = chat_session.db_connection

        schema = db_conn.schema.schema_snapshot

        message_histories = self.repo.get_last_messages(session_id=request.session_id)

        message_history = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in message_histories if msg.content]
        )

        sql_prompt = build_sql_prompt(schema, message_history, request.user_question)

        llm = LLMFactory.get_llm(chat_session.llm_mode)

        generated_sql = llm.generate_sql(sql_prompt)

        clean_sql = clean_sql_response(generated_sql)

        validate_query_permission(clean_sql, permission)

        engine_payload = DbConnectEngineRequest(
            db_type=db_conn.db_type,
            host=db_conn.host,
            port=db_conn.port,
            database_name=db_conn.database_name,
            db_username=db_conn.db_username,
            encrypted_password=db_conn.encrypted_password
        )

        engine = get_engine(engine_payload)

        start_time = time.time()

        with engine.connect() as conn:
            result = conn.execute(text(clean_sql))
            rows = result.mappings().all()
            rows = [self.serialize_row(dict(row)) for row in rows]

        execution_time = time.time() - start_time

        answer_prompt = build_answer_prompt(request.user_question, rows)

        answer = llm.generate_answer(answer_prompt)


        message_response = self.repo.create_message(
            session_id=request.session_id,
            role=ChatRole.assistant,
            content=answer,
            generated_sql=clean_sql,
            query_result={"rows": rows},
            execution_time=execution_time,
            success=True
        )

        return MessageResponse(
            id=message_response.id,
            session_id=message_response.session_id,
            role=message_response.role,
            content=message_response.content,
            generated_sql=message_response.generated_sql,
            query_result=message_response.query_result,
            execution_time=message_response.execution_time,
            success=message_response.success,
            created_at=message_response.created_at
        )