from fastapi import HTTPException
from app.utils.enums import Permission
from app.core.sql_permissions import PERMISSION_SQL_MAP
from app.utils.sql_validator import get_sql_operation


def validate_query_permission(query: str, permission: Permission):

    operation = get_sql_operation(query)

    allowed_operations = PERMISSION_SQL_MAP.get(permission, [])

    if operation not in allowed_operations:
        raise HTTPException(
            status_code=403,
            detail=f"{operation} queries are not allowed for your role"
        )