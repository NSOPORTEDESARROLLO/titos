"""
Authentication dependency for API Token verification.
All protected routes use `Depends(verify_token)` to validate
the Bearer token sent in the Authorization header.
"""
from typing import Optional

from fastapi import Header, HTTPException, status

from src.core.config import settings


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verifies the Bearer token from the Authorization header
    against the configured AUTH_TOKEN.

    Args:
        authorization: The full Authorization header value
                       (e.g., "Bearer my-secret-token").

    Returns:
        The validated token string.

    Raises:
        HTTPException 401: If token is missing, malformed, or invalid.
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
        )
    token = authorization.removeprefix("Bearer ")
    if token != settings.auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
    return token
