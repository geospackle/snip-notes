from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .jwt_handler import JWTHandler


security = HTTPBearer()


def create_auth_dependency(jwt_handler: JWTHandler):
    """Create an authentication dependency function"""

    async def verify_token(
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> str:
        """
        Verify JWT token from request header.
        Returns the user's email if valid, raises HTTPException otherwise.
        """
        token = credentials.credentials
        email = jwt_handler.verify_token(token)

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return email

    return verify_token


def create_optional_auth_dependency(jwt_handler: JWTHandler):
    """Create an optional authentication dependency (returns None if no token)"""

    async def verify_optional_token(
        credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
    ) -> Optional[str]:
        """
        Verify JWT token if provided.
        Returns email if valid token, None if no token or invalid.
        """
        if credentials is None:
            return None

        token = credentials.credentials
        return jwt_handler.verify_token(token)

    return verify_optional_token
