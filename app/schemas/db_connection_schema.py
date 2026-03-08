from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.utils.enums import DataBaseType
from datetime import datetime

class DbConnectionCreate(BaseModel):
    user_id: int
    name: Optional[str] = None
    db_type: DataBaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: str
    db_username: Optional[str] = None
    password: Optional[str] = None


class DbConnectionUpdate(BaseModel):
    connection_id: int
    name: Optional[str] = None
    db_type: Optional[DataBaseType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    db_username: Optional[str] = None
    password: Optional[str] = None


class DbConnectEngineRequest(BaseModel):
    conn_id: Optional[int] = None
    db_type: DataBaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: str
    db_username: Optional[str] = None
    encrypted_password: Optional[str] = None


class DbConnectionResponse(BaseModel):
    id: int
    user_id: int
    name: str
    db_type: DataBaseType
    host: str
    port: int
    database_name: str
    db_username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DbConnectionListResponse(BaseModel):
    connections: list[DbConnectionResponse]