from datetime import datetime
from uuid import UUID
from sqlmodel import col, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.refresh_session import RefreshSession


async def create_refresh_session(
    session: AsyncSession,
    *,
    user_id: int,
    family_id: UUID,
    jti: str,
    token_hash: str,
    expires_at: datetime,
    user_agent: str | None,
    ip_address: str | None,
) -> RefreshSession:
    row = RefreshSession(
        user_id=user_id,
        family_id=family_id,
        jti=jti,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    session.add(row)
    await session.flush()
    return row


async def get_refresh_session_for_update(
    session: AsyncSession, user_id: int, jti: str
) -> RefreshSession | None:
    stmt = (
        select(RefreshSession)
        .where(col(RefreshSession.user_id) == user_id, col(RefreshSession.jti) == jti)
        .with_for_update()
    )
    result = await session.exec(stmt)
    return result.one_or_none()


async def revoke_family(
    session: AsyncSession, *, family_id: UUID, now: datetime, mark_reuse: bool = False
) -> None:
    values = {"revoked_at": now}
    if mark_reuse:
        values["reuse_detected_at"] = now

    stmt = (
        update(RefreshSession)
        .where(
            col(RefreshSession.family_id) == family_id,
            col(RefreshSession.revoked_at).is_(None),
        )
        .values(**values)
    )
    await session.exec(stmt)
