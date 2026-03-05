from sqlalchemy.orm import Session
from fastapi import status
from fastapi import HTTPException
from app.models.db_connection import DbConnection, SchemaCache
from app.schemas.db_connection_schema import DbConnectionCreate, DbConnectionUpdate
from app.core.hashing import Hash
from app.utils.enums import DataBaseType
from datetime import datetime, timezone