from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth_schema import *
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=AuthResponse)
async def register_user(
        request: RegistrationRequest,
        db: Session = Depends(get_db)
):
    service = AuthService(db)
    reg_response = await service.user_creation(request)
    return reg_response

@router.post("/login", response_model=AuthResponse)
def login_user(
        request: LoginRequest,
        db: Session = Depends(get_db)
):
    service = AuthService(db)
    login_response = service.user_login(request)
    return login_response