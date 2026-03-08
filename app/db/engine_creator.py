import sqlalchemy
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.engine import URL
from app.core.encryption import decrypt_password
from app.utils.enums import DataBaseType
from app.schemas.db_connection_schema import DbConnectEngineRequest

def get_engine(request: DbConnectEngineRequest):
    if request.db_type == DataBaseType.postgres:
        if request.encrypted_password:
            password = decrypt_password(request.encrypted_password)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required for connecting DB."
            )

        url = URL.create(
            "postgresql+psycopg2",
            username=request.db_username,
            password=password,
            host=request.host,
            port=request.port,
            database=request.database_name
        )
    elif request.db_type == DataBaseType.mysql:
        if request.encrypted_password:
            password = decrypt_password(request.encrypted_password)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required for connecting DB."
            )
        url = URL.create(
            "mysql+pymysql",
            username=request.db_username,
            password=password,
            host=request.host,
            port=request.port,
            database=request.database_name
        )
    elif request.db_type == DataBaseType.sqlite:
        url = f"sqlite:///{request.database_name}"
    else:
        raise ValueError(f"Unsupported DB type: {request.db_type}")

    engine = sqlalchemy.create_engine(url)
    return engine