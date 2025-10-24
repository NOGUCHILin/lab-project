"""Drop unused tables (handoffs, notes, sessions)

Revision ID: b0bbf866ebc2
Revises: 001
Create Date: 2025-10-16 14:05:01.264264

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b0bbf866ebc2"
down_revision: str | Sequence[str] | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop unused tables
    op.drop_table("handoffs")
    op.drop_table("notes")
    op.drop_table("sessions")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate tables in reverse order (not implemented - data loss expected)
    pass
