from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.base_schema import BaseResponse, EmptyData
from app.schemas.chat_schema import *
from app.utils.enums import UserRole
from app.services.chat_service import ChatService
from app.api.v1.dependencies import role_required


router = APIRouter(prefix="/chat", tags=["Chats"])

@router.get("/chat-session", response_model=BaseResponse[SessionResponseList])
def get_chat_lists(
    db_connection_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    user_id = auth.get("sub")
    session_list = service.get_all_chats(user_id, db_connection_id)
    return BaseResponse(
        status_code=200,
        message="Chat list fetched successfully",
        data=session_list
    )

@router.post("/chat-session", response_model=BaseResponse[SessionResponse])
def add_new_chat(
    request: SessionCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    user_id = auth.get("sub")
    new_chat = service.create_chat(user_id, request)
    return BaseResponse(
        status_code=201,
        message="New chat created successfully.",
        data=new_chat
    )

@router.patch("/chat-session/mode", response_model=BaseResponse[SessionResponse])
def update_chat_mode(
    request: SessionUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    updated_chat = service.update_chat(request)
    return BaseResponse(
        status_code=200,
        message="Chat updated successfully.",
        data=updated_chat
    )

@router.patch("/chat-session/title", response_model=BaseResponse[SessionResponse])
def update_chat_title(
    request: MessageCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    updated_chat = service.update_chat_title(request)
    return BaseResponse(
        status_code=200,
        message="Chat updated successfully.",
        data=updated_chat
    )

@router.delete("/chat-session/{session_id}", response_model=BaseResponse[EmptyData])
def delete_chat(
    session_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    service.delete_chat(session_id)

    return BaseResponse(
        status_code=200,
        message="Chat deleted successfully.",
        data=None
    )

@router.get("/chat-session/{session_id}/message", response_model=BaseResponse[MessageListResponse])
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    messages = service.get_all_messages_for_chat(session_id)
    return BaseResponse(
        status_code=200,
        message="Messages fetched successfully",
        data=messages
    )

@router.post("/chat-session/{session_id}/message", response_model=BaseResponse[MessageResponse])
def ask_question(
    request: MessageCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = ChatService(db)
    permission = auth.get("permission")
    message = service.send_message(request, permission)
    return BaseResponse(
        status_code=201,
        message="Answer fetched successfully",
        data=message
    )