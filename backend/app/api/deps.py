from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.security import decode_access_token
from app.models.enums import UserRole
from app.schemas.auth import TokenData

bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, auto-closing on exit."""
    async with async_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenData:
    """Extract and validate the JWT from the Authorization header."""
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        return TokenData(
            user_id=UUID(payload["sub"]),
            email=payload["email"],
            role=UserRole(payload["role"]),
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token payload")


async def require_admin(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Verify the current user has admin role. Use as a dependency on protected routes."""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
