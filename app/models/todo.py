from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

from app.models.user import User


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    owner_id: int = Field(foreign_key="user.id", index=True, nullable=False)
    owner: User = Relationship(back_populates="todos")
