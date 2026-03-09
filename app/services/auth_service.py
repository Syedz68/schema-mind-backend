from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import status
from app.utils.enums import UserRole, Permission
from app.repositories.auth_repository import AuthRepository
from app.core.jwt import create_access_token
from app.schemas.auth_schema import *

class AuthService:

    def __init__(self, db: Session):
        self.auth_repo = AuthRepository(db)
        self.db = db

    async def user_creation(self, request: RegistrationRequest):
        if request.role:
            if request.role.value == UserRole.admin:
                request.permission = Permission.ADMIN_ACCESS
            elif request.role.value == UserRole.analyst:
                request.permission = Permission.READ_WRITE
            elif request.role.value == UserRole.viewer:
                request.permission = Permission.SELECT_ONLY

        user = self.auth_repo.create_user(request)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Something went wrong. Please try again later."
            )

        data = {
            "user_id": user.id,
            "user_name": user.full_name,
            "role": user.user_role.value,
            "permission": user.user_permission.value
        }
        token = create_access_token(data)
        return token

    def user_login(self, request: LoginRequest):
        user = self.auth_repo.authenticate_user(request)
        data = {
            "user_id": user.id,
            "user_name": user.full_name,
            "role": user.user_role.value,
            "permission": user.user_permission.value
        }
        token = create_access_token(data)
        return token