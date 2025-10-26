"""extend tasks table with priority and progress

Revision ID: 006
Revises: 005
Create Date: 2025-10-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add priority, progress_percent, estimated_hours to tasks table"""
    # Add priority column with default value 5 (medium priority)
    op.add_column(
        "tasks",
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
    )

    # Add progress_percent column with default value 0 and CHECK constraint (0-100)
    op.add_column(
        "tasks",
        sa.Column(
            "progress_percent", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.create_check_constraint(
        "ck_tasks_progress_percent_range",
        "tasks",
        sa.text("progress_percent >= 0 AND progress_percent <= 100"),
    )

    # Add estimated_hours column (nullable, no default)
    op.add_column(
        "tasks",
        sa.Column("estimated_hours", sa.Float(), nullable=True),
    )

    # Create index on priority for efficient sorting
    op.create_index(op.f("idx_tasks_priority"), "tasks", ["priority"], unique=False)


def downgrade() -> None:
    """Remove priority, progress_percent, estimated_hours from tasks table"""
    op.drop_index(op.f("idx_tasks_priority"), table_name="tasks")
    op.drop_column("tasks", "estimated_hours")
    op.drop_constraint("ck_tasks_progress_percent_range", "tasks", type_="check")
    op.drop_column("tasks", "progress_percent")
    op.drop_column("tasks", "priority")
