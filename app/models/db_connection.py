from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.utils.enums import DataBaseType

class DbConnection(Base):
    __tablename__ = "db_connection"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    db_type = Column(Enum(DataBaseType, native_enum=False), nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    database_name = Column(String, nullable=False)
    db_username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="db_connections")
    sessions = relationship("ChatSession", back_populates="db_connection", cascade="all, delete-orphan")
    schemas = relationship("SchemaCache", back_populates="db_connection", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="db_connection")


class SchemaCache(Base):
    __tablename__ = "schema_cache"

    id = Column(Integer, primary_key=True, index=True)
    db_connection_id = Column(Integer, ForeignKey("db_connection.id", ondelete="CASCADE"), nullable=False)
    schema_snapshot = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    db_connection = relationship("DbConnection", back_populates="schemas")