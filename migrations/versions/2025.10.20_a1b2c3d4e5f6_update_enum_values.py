"""update enum values

Revision ID: a1b2c3d4e5f6
Revises: f487b66bcfc3
Create Date: 2025-10-20 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f487b66bcfc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE tickets SET status = 'IN_PROGRESS' WHERE status = 'OPEN'")

    op.execute("ALTER TYPE ticketstatus RENAME TO ticketstatus_old")
    op.execute("CREATE TYPE ticketstatus AS ENUM ('NEW', 'IN_PROGRESS', 'COMPLETED', 'CLOSED')")
    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN status TYPE ticketstatus
        USING status::text::ticketstatus
    """)
    op.execute("DROP TYPE ticketstatus_old")


def downgrade() -> None:
    op.execute("UPDATE tickets SET status = 'CLOSED' WHERE status = 'COMPLETED'")
    op.execute("UPDATE tickets SET status = 'CLOSED' WHERE status = 'NEW'")

    op.execute("ALTER TYPE ticketstatus RENAME TO ticketstatus_old")
    op.execute("CREATE TYPE ticketstatus AS ENUM ('OPEN', 'IN_PROGRESS', 'CLOSED')")
    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN status TYPE ticketstatus
        USING status::text::ticketstatus
    """)
    op.execute("DROP TYPE ticketstatus_old")
