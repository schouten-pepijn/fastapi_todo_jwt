from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps.authentication import get_current_user
from app.crud.user import get_user_by_email, create_user
from app.db.database import get_session
from app.schemas.user import UserCreate, UserRead
from app.schemas.authentication import LoginRequest, TokenPair
from app.schemas.user import UserRead, UserCreate
from app.services.authentication import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserRead:
    existing = await get_user_by_email(session, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = await create_user(
        session,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    return UserRead(id=user.id, email=user.email, is_active=user.is_active)
