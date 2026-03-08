from sqlalchemy.orm import Session
from fastapi import status
from fastapi import HTTPException
from app.models.db_connection import DbConnection, SchemaCache
from app.schemas.db_connection_schema import DbConnectionCreate, DbConnectionUpdate
from app.core.encryption import encrypt_password
from app.utils.enums import DataBaseType
from datetime import datetime, timezone
import hashlib
import json

class DbConnectionRepository:
    def __init__(self, db: Session):
        self.db = db

    # DB Connection Related Tasks

    def get_connection_by_database_name_and_type(self, user_id: int, db_name: str, db_type: DataBaseType):
        return (
            self.db.query(DbConnection)
            .filter(
                DbConnection.database_name == db_name,
                DbConnection.db_type == db_type,
                DbConnection.user_id == user_id
            )
            .first()
        )

    def get_connection_by_id(self, connection_id: int):
        return self.db.query(DbConnection).filter(DbConnection.id == connection_id).first()

    def get_all_connections_by_user(self, user_id: int):
        return self.db.query(DbConnection).filter(DbConnection.user_id == user_id).all()

    def create_new_db(self, request: DbConnectionCreate):
        existing_db = self.get_connection_by_database_name_and_type(
            request.user_id, request.database_name, request.db_type
        )
        if existing_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{request.database_name} is already enrolled in your chat for {request.db_type.value.upper()}"
            )

        password = encrypt_password(request.password) if request.password else None

        new_connection = DbConnection(
            user_id=request.user_id,
            name=request.name or request.database_name,
            db_type=request.db_type,
            host=request.host,
            port=request.port,
            database_name=request.database_name,
            db_username=request.db_username,
            encrypted_password=password
        )
        self.db.add(new_connection)
        self.db.commit()
        self.db.refresh(new_connection)
        return new_connection

    def update_connection(self, request: DbConnectionUpdate):
        conn = self.get_connection_by_id(request.connection_id)
        if not conn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DB connection not found")

        if request.name:
            conn.name = request.name
        if request.db_type:
            conn.db_type = request.db_type
        if request.host:
            conn.host = request.host
        if request.port:
            conn.port = request.port
        if request.database_name:
            conn.database_name = request.database_name
        if request.db_username:
            conn.db_username = request.db_username
        if request.password:
            conn.encrypted_password = encrypt_password(request.password)

        self.db.commit()
        self.db.refresh(conn)
        return conn

    def delete_connection(self, connection_id: int):
        conn = self.get_connection_by_id(connection_id)
        if not conn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DB connection not found")

        self.db.delete(conn)
        self.db.commit()
        return {"detail": "DB connection deleted successfully"}

    # Schema related tasks

    def create_or_update_schema_cache(self, db_connection_id: int, schema_snapshot: dict):
        schema_str = json.dumps(schema_snapshot, sort_keys=True)
        schema_hash = hashlib.sha256(schema_str.encode()).hexdigest()

        existing_schema = (
            self.db.query(SchemaCache)
            .filter(SchemaCache.db_connection_id == db_connection_id)
            .first()
        )

        if existing_schema:
            if existing_schema.schema_hash != schema_hash:
                existing_schema.schema_snapshot = schema_snapshot
                existing_schema.schema_hash = schema_hash
                existing_schema.version += 1
                self.db.commit()
                self.db.refresh(existing_schema)
            return existing_schema
        else:
            new_schema = SchemaCache(
                db_connection_id=db_connection_id,
                schema_snapshot=schema_snapshot,
                schema_hash=schema_hash,
                version=1
            )
            self.db.add(new_schema)
            self.db.commit()
            self.db.refresh(new_schema)
            return new_schema

    def get_schema_cache(self, db_connection_id: int):
        return (
            self.db.query(SchemaCache)
            .filter(SchemaCache.db_connection_id == db_connection_id)
            .first()
        )