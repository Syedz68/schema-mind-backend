from sqlalchemy.orm import Session
from fastapi import status
from fastapi import HTTPException
from app.models.user import User
from app.schemas.auth_schema import RegistrationRequest, LoginRequest
from app.core.hashing import Hash
from app.utils.enums import UserRole
from datetime import datetime, timezone

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    # ========== User Query Methods ==========

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_email_and_role(self, email: str, role: UserRole):
        return self.db.query(User).filter(User.email == email, User.user_role == role).first()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    # ========== User Creation Methods ==========

    def create_user(self, registration_data: RegistrationRequest):
        existing_user = self.get_user_by_email_and_role(
            registration_data.email,
            registration_data.role
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with this email already exists for {registration_data.role.value} role"
            )

        hashed_password = Hash.bcrypt(registration_data.password)

        new_user = User(
            email=registration_data.email,
            hashed_password=hashed_password,
            full_name=registration_data.full_name,
            user_role=registration_data.role,
            user_permission=registration_data.permission
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    # ========== Authentication Methods ==========

    def authenticate_user(self, request: LoginRequest):
        user = self.get_user_by_email(request.email)
        if not user:
            return None

        if not Hash.verify(request.password, user.hashed_password):
            return None

        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        return user