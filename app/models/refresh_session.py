from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class RefreshSession(SQLModel, table=True):
    __tablename__ = "refresh_session"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True, nullable=False),
    )
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    family_id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PGUUID(as_uuid=True), nullable=False, index=True),
    )

    jti: str = Field(
        sa_column=Column(String(36), nullable=False, unique=True, index=True),
    )

    token_hash: str = Field(
        sa_column=Column(String(64), nullable=False, unique=True, index=True),
    )

    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    consumed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    reuse_detected_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    replaced_by_id: UUID | None = Field(
        default=None,
        sa_column=Column(PGUUID(as_uuid=True), nullable=True),
    )

    user_agent: str | None = Field(default=None, max_length=512)
    ip_address: str | None = Field(default=None, max_length=64)

    user: "User" = Relationship(back_populates="refresh_sessions")
