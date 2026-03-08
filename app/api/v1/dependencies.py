from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, HTTPException, status
from app.utils.enums import UserRole
from app.core.jwt import verify_access_token

oauth_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="JWT Bearer Token Authentication. Login first, then paste your access_token here.",
    auto_error=True
)

def role_required(*required_roles: UserRole):
    def wrapper(
            credentials: HTTPAuthorizationCredentials = Security(oauth_scheme)
    ):
        token = credentials.credentials

        validated_token = verify_access_token(token)

        if not validated_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found"
            )
        role = validated_token.get("role", None)

        if role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "title": "Permission denied",
                    "message": "You have not any permission."
                }
            )
        return validated_token

    return wrapper