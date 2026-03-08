from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.base_schema import BaseResponse, EmptyData
from app.schemas.db_connection_schema import *
from app.utils.enums import UserRole
from app.services.db_connection_service import DbConnectionService
from app.api.v1.dependencies import role_required


router = APIRouter(prefix="/db-connect", tags=["DB Connection"])

@router.get("/connections", response_model=BaseResponse[DbConnectionListResponse])
def get_all_connections(
    user_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = DbConnectionService(db)
    db_list = service.get_all_db_list(user_id)
    return BaseResponse(
        status_code=200,
        message="DB connection list fetched successfully",
        data=db_list
    )

@router.post("/add-db", response_model=BaseResponse[DbConnectionResponse])
def add_new_db_connection(
    request: DbConnectionCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = DbConnectionService(db)
    new_connection = service.add_new_connection(request)
    return BaseResponse(
        status_code=201,
        message="DB connection created successfully.",
        data=new_connection
    )

@router.patch("/update-db-credentials", response_model=BaseResponse[DbConnectionResponse])
def update_db_connection_credential(
    request: DbConnectionUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = DbConnectionService(db)
    updated_connection = service.update_connection(request)
    return BaseResponse(
        status_code=200,
        message="DB connection updated successfully.",
        data=updated_connection
    )

@router.delete("/{connection_id}", response_model=BaseResponse[EmptyData])
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = DbConnectionService(db)
    service.delete_connection(connection_id)

    return BaseResponse(
        status_code=200,
        message="DB connection deleted successfully.",
        data=None
    )

@router.post("/refresh-schema", response_model=BaseResponse[EmptyData])
def refresh_db_schema(
    request: DbConnectEngineRequest,
    db: Session = Depends(get_db),
    auth: dict = Depends(role_required(UserRole.analyst, UserRole.viewer, UserRole.admin))
):
    service = DbConnectionService(db)
    service.refresh_the_schema(request)

    return BaseResponse(
        status_code=200,
        message="Schema refreshed successfully.",
        data=None
    )