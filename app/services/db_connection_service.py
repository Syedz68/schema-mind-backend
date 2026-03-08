from sqlalchemy.orm import Session
from app.utils.schema_extractor import extract_schema
from app.db.engine_creator import get_engine
from app.repositories.db_connection_repository import DbConnectionRepository
from app.schemas.db_connection_schema import *

class DbConnectionService:
    def __init__(self, db: Session):
        self.repo = DbConnectionRepository(db)

    def get_all_db_list(self, user_id: int):
        conn = self.repo.get_all_connections_by_user(user_id)

        db_list = [
            DbConnectionResponse(
                id=item.id,
                user_id=item.user_id,
                name=item.name,
                db_type=item.db_type,
                host=item.host or "",
                port=item.port or 0,
                database_name=item.database_name,
                db_username=item.db_username or "",
                is_active=item.is_active,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            for item in conn
        ]

        return DbConnectionListResponse(connections=db_list)

    def add_new_connection(self, request: DbConnectionCreate):
        conn = self.repo.create_new_db(request)

        engine_request = DbConnectEngineRequest(
            db_type=conn.db_type,
            host=conn.host,
            port=conn.port,
            database_name=conn.database_name,
            db_username=conn.db_username,
            encrypted_password=conn.encrypted_password
        )

        engine = get_engine(engine_request)

        schema_design = extract_schema(engine)

        schema_snapshot = self.repo.create_or_update_schema_cache(conn.id, schema_design)

        return DbConnectionResponse(
            id=conn.id,
            user_id=conn.user_id,
            name=conn.name,
            db_type=conn.db_type,
            host=conn.host or "",
            port=conn.port or 0,
            database_name=conn.database_name,
            db_username=conn.db_username or "",
            is_active=conn.is_active,
            created_at=conn.created_at,
            updated_at=conn.updated_at
        )

    def update_connection(self, request: DbConnectionUpdate):
        conn = self.repo.update_connection(request)

        return DbConnectionResponse(
            id=conn.id,
            user_id=conn.user_id,
            name=conn.name,
            db_type=conn.db_type,
            host=conn.host or "",
            port=conn.port or 0,
            database_name=conn.database_name,
            db_username=conn.db_username or "",
            is_active=conn.is_active,
            created_at=conn.created_at,
            updated_at=conn.updated_at
        )

    def delete_connection(self, connection_id: int):
        self.repo.delete_connection(connection_id)
        return {"detail": "DB connection deleted successfully"}

    def refresh_the_schema(self, request: DbConnectEngineRequest):
        engine = get_engine(request)
        schema_design = extract_schema(engine)
        self.repo.create_or_update_schema_cache(request.conn_id, schema_design)

        return {"detail": "Schema refreshed successfully"}

    def get_the_schema(self, conn_id: int):
        return self.repo.get_schema_cache(conn_id)