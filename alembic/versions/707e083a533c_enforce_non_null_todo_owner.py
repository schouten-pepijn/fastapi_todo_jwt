"""enforce non-null todo owner

Revision ID: 707e083a533c
Revises: 98adc08e9d01
Create Date: 2026-03-01 18:32:46.038009

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "707e083a533c"
down_revision: Union[str, Sequence[str], None] = "98adc08e9d01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    null_owner_count = connection.execute(
        sa.text("SELECT COUNT(1) FROM todo WHERE owner_id IS NULL")
    ).scalar_one()

    if null_owner_count > 0:
        raise RuntimeError(
            "Cannot enforce NOT NULL on todo.owner_id while NULL values exist. "
            "Backfill or delete orphan todo rows first."
        )

    with op.batch_alter_table("todo") as batch_op:
        batch_op.alter_column(
            "owner_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("todo") as batch_op:
        batch_op.alter_column(
            "owner_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
