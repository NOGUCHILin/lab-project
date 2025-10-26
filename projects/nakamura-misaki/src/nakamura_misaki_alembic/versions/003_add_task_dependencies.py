"""Add Task Dependencies table

Revision ID: 003
Revises: 002
Create Date: 2025-10-26

Phase 2: Task Dependencies Context
- task_dependencies table
- Supports dependency tracking and blocker detection
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create task_dependencies table
    op.create_table(
        "task_dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocking_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocked_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dependency_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["blocking_task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["blocked_task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("blocking_task_id", "blocked_task_id", name="uq_task_dependency"),
        sa.CheckConstraint("blocking_task_id != blocked_task_id", name="ck_no_self_dependency"),
    )
    op.create_index("idx_dependencies_blocking", "task_dependencies", ["blocking_task_id"])
    op.create_index("idx_dependencies_blocked", "task_dependencies", ["blocked_task_id"])


def downgrade() -> None:
    op.drop_table("task_dependencies")
