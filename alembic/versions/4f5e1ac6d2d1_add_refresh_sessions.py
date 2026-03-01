"""add refresh sessions

Revision ID: 4f5e1ac6d2d1
Revises: 707e083a533c
Create Date: 2026-03-01 22:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "4f5e1ac6d2d1"
down_revision: Union[str, Sequence[str], None] = "707e083a533c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "refresh_session",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reuse_detected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refresh_session_user_id"),
        "refresh_session",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_refresh_session_family_id"),
        "refresh_session",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_refresh_session_jti"),
        "refresh_session",
        ["jti"],
        unique=True,
    )
    op.create_index(
        op.f("ix_refresh_session_token_hash"),
        "refresh_session",
        ["token_hash"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_refresh_session_token_hash"), table_name="refresh_session")
    op.drop_index(op.f("ix_refresh_session_jti"), table_name="refresh_session")
    op.drop_index(op.f("ix_refresh_session_family_id"), table_name="refresh_session")
    op.drop_index(op.f("ix_refresh_session_user_id"), table_name="refresh_session")
    op.drop_table("refresh_session")
