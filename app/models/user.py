from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.utils.enums import UserRole, Permission

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_role = Column(Enum(UserRole, native_enum=False), nullable=False)
    user_permission = Column(Enum(Permission, native_enum=False), default=Permission.SELECT_ONLY, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    db_connections = relationship("DbConnection", back_populates="users", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="users", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="users")