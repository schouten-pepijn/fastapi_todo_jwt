import hmac
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps.authentication import get_current_user
from app.crud.refresh_session import (
    create_refresh_session,
    get_refresh_session_for_update,
    revoke_family,
)
from app.crud.user import create_user, get_user_by_email, get_user_by_id
from app.db.database import get_session
from app.schemas.authentication import (
    LoginRequest,
    RefreshRequest,
    TokenPair,
)
from app.schemas.user import UserCreate, UserRead
from app.services.authentication import (
    RefreshTokenBundle,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _invalid_refresh_token(detail: str = "Invalid refresh token") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_refresh_claims(refresh_token: str) -> tuple[int, str, UUID]:
    try:
        payload = decode_token(refresh_token, token_type="refresh")
    except JWTError as exc:
        raise _invalid_refresh_token() from exc

    if payload.get("type") != "refresh":
        raise _invalid_refresh_token("Invalid token type")

    sub = payload.get("sub")
    jti = payload.get("jti")
    fid = payload.get("fid")
    if not sub or not jti or not fid:
        raise _invalid_refresh_token("Invalid token payload")

    try:
        return int(sub), str(jti), UUID(str(fid))

    except (TypeError, ValueError) as exc:
        raise _invalid_refresh_token("Invalid token payload") from exc


def to_user_read(user) -> UserRead:
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID was not generated",
        )
    return UserRead(id=user.id, email=user.email, is_active=user.is_active)


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
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    user = await get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user_read = to_user_read(user)
    family_id = uuid4()
    refresh_bundle = create_refresh_token(str(user_read.id), family_id=str(family_id))

    await create_refresh_session(
        session,
        user_id=user_read.id,
        family_id=family_id,
        jti=refresh_bundle["jti"],
        token_hash=hash_refresh_token(refresh_bundle["token"]),
        expires_at=refresh_bundle["expires_at"],
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    await session.commit()

    return TokenPair(
        access_token=create_access_token(str(user_read.id)),
        refresh_token=refresh_bundle["token"],
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    now = datetime.now(timezone.utc)
    user_id, jti, family_id = _parse_refresh_claims(payload.refresh_token)
    incoming_hash = hash_refresh_token(payload.refresh_token)

    refresh_bundle: RefreshTokenBundle | None = None
    refresh_error_detail: str | None = None

    async with session.begin():
        user = await get_user_by_id(session, user_id=user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        current = await get_refresh_session_for_update(session, user_id=user_id, jti=jti)
        if (
            current is None
            or current.family_id != family_id
            or current.revoked_at is not None
            or _as_utc(current.expires_at) <= now
        ):
            raise _invalid_refresh_token()

        if not hmac.compare_digest(current.token_hash, incoming_hash):
            await revoke_family(
                session,
                family_id=current.family_id,
                now=now,
                mark_reuse=True,
            )
            refresh_error_detail = "Invalid refresh token"
        elif current.consumed_at is not None:
            await revoke_family(
                session,
                family_id=current.family_id,
                now=now,
                mark_reuse=True,
            )
            refresh_error_detail = "Refresh token reuse detected"
        else:
            refresh_bundle = create_refresh_token(
                str(user_id), family_id=str(current.family_id)
            )
            replacement = await create_refresh_session(
                session,
                user_id=user_id,
                family_id=current.family_id,
                jti=refresh_bundle["jti"],
                token_hash=hash_refresh_token(refresh_bundle["token"]),
                expires_at=refresh_bundle["expires_at"],
                user_agent=request.headers.get("user-agent"),
                ip_address=request.client.host if request.client else None,
            )

            current.consumed_at = now
            current.replaced_by_id = replacement.id

    if refresh_error_detail is not None:
        raise _invalid_refresh_token(refresh_error_detail)

    if refresh_bundle is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to issue refresh token",
        )

    return TokenPair(
        access_token=create_access_token(str(user_id)),
        refresh_token=str(refresh_bundle["token"]),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> Response:
    now = datetime.now(timezone.utc)
    user_id, jti, family_id = _parse_refresh_claims(payload.refresh_token)
    incoming_hash = hash_refresh_token(payload.refresh_token)

    async with session.begin():
        current = await get_refresh_session_for_update(session, user_id=user_id, jti=jti)
        if (
            current is None
            or current.family_id != family_id
            or not hmac.compare_digest(current.token_hash, incoming_hash)
        ):
            raise _invalid_refresh_token()

        await revoke_family(session, family_id=current.family_id, now=now)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_user)):
    return to_user_read(current_user)
