from fastapi import APIRouter, Depends, HTTPException, Response, status
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps.authentication import get_current_user
from app.crud.user import get_user_by_email, create_user, get_user_by_id
from app.db.database import get_session
from app.schemas.authentication import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    TokenPair,
)
from app.schemas.user import UserRead, UserCreate
from app.services.authentication import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def to_user_read(user) -> UserRead:
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID was not generated",
        )
    return UserRead(id=user.id, email=user.email, is_active=user.is_active)


async def _get_active_user_from_refresh_token(
    refresh_token: str,
    session: AsyncSession,
):
    try:
        payload = decode_token(refresh_token, token_type="refresh")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await get_user_by_id(session, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return to_user_read(user)


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
    return to_user_read(user)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    user_read = to_user_read(user)

    return TokenPair(
        access_token=create_access_token(str(user_read.id)),
        refresh_token=create_refresh_token(str(user_read.id)),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> AccessTokenResponse:
    user_read = await _get_active_user_from_refresh_token(
        payload.refresh_token, session
    )
    return AccessTokenResponse(access_token=create_access_token(str(user_read.id)))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> Response:
    await _get_active_user_from_refresh_token(payload.refresh_token, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_user)):
    return to_user_read(current_user)
