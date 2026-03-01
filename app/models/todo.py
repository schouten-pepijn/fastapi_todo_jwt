from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
