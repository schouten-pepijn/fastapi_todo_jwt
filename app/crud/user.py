from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    pass


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    pass


async def create_user(
    session: AsyncSession, *, email: str, hashed_password: str
) -> User:
    pass
