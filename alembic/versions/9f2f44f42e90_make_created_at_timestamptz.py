"""make created_at timestamptz

Revision ID: 9f2f44f42e90
Revises: 4f5e1ac6d2d1
Create Date: 2026-03-01 22:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f2f44f42e90"
down_revision: Union[str, Sequence[str], None] = "4f5e1ac6d2d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        sa.text(
            """
            ALTER TABLE "user"
            ALTER COLUMN created_at
            TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
            """
        )
    )
    op.execute(
        sa.text(
            """
            ALTER TABLE todo
            ALTER COLUMN created_at
            TYPE TIMESTAMP WITH TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text(
            """
            ALTER TABLE "user"
            ALTER COLUMN created_at
            TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
            """
        )
    )
    op.execute(
        sa.text(
            """
            ALTER TABLE todo
            ALTER COLUMN created_at
            TYPE TIMESTAMP WITHOUT TIME ZONE
            USING created_at AT TIME ZONE 'UTC'
            """
        )
    )
