from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.exec(select(User).where(User.email == email))
    return result.one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.exec(select(User).where(User.id == user_id))
    return result.one_or_none()


async def create_user(
    session: AsyncSession,
    *,
    email: str,
    hashed_password: str,
) -> User:
    user = User(email=email, hashed_password=hashed_password, is_active=True)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
