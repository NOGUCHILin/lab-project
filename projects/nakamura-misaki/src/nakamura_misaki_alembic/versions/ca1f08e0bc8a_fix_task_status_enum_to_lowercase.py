"""Fix task_status ENUM to use lowercase values

Revision ID: ca1f08e0bc8a
Revises: 79bb97c4352b
Create Date: 2025-10-21

This migration fixes the task_status ENUM type to use lowercase values
(pending, in_progress, completed, cancelled) to match Python code conventions
and improve consistency with the codebase.

Since the tasks table has no data, this migration is safe to run.
"""

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ca1f08e0bc8a"
down_revision = "79bb97c4352b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Convert task_status ENUM from uppercase to lowercase values"""

    # Step 1: Create new ENUM type with lowercase values
    new_task_status = postgresql.ENUM("pending", "in_progress", "completed", "cancelled", name="task_status_new")
    new_task_status.create(op.get_bind())

    # Step 2: Alter column to use new ENUM type
    # Using CAST to convert existing uppercase values to lowercase
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN status TYPE task_status_new
        USING LOWER(status::text)::task_status_new
    """)

    # Step 3: Drop old ENUM type
    op.execute("DROP TYPE task_status")

    # Step 4: Rename new ENUM type to original name
    op.execute("ALTER TYPE task_status_new RENAME TO task_status")


def downgrade() -> None:
    """Revert task_status ENUM back to uppercase values"""

    # Step 1: Create ENUM type with uppercase values
    old_task_status = postgresql.ENUM("PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="task_status_old")
    old_task_status.create(op.get_bind())

    # Step 2: Alter column to use old ENUM type
    # Using CAST to convert lowercase values back to uppercase
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN status TYPE task_status_old
        USING UPPER(status::text)::task_status_old
    """)

    # Step 3: Drop new ENUM type
    op.execute("DROP TYPE task_status")

    # Step 4: Rename old ENUM type to original name
    op.execute("ALTER TYPE task_status_old RENAME TO task_status")
