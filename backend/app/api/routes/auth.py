from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token, verify_password
from app.models import User
from app.models.enums import UserRole
from app.schemas.auth import LoginRequest, TokenData, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email and password. Returns a JWT token if valid. Only admin users can log in."""
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin users can access this platform")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(user_id=user.id, email=user.email, role=user.role.value)

    return TokenResponse(access_token=token, role=user.role)


@router.get("/me", response_model=TokenData)
async def get_me(
    current_user: TokenData = Depends(get_current_user),
):
    """Return the currently authenticated user's info from the JWT token."""
    return current_user
