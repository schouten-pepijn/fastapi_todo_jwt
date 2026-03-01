from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.refresh_session import RefreshSession


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    refresh_sessions: List["RefreshSession"] = Relationship(back_populates="user")
    todos: List["Todo"] = Relationship(back_populates="owner")
