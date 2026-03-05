from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.utils.enums import UserRole, Permission
from datetime import datetime

class RegistrationRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole
    permission: Optional[Permission] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    access_token_type: str
    access_token_expires_at: datetime

    model_config = ConfigDict(from_attributes=True)