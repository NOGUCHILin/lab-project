"""add notifications table

Revision ID: 005
Revises: 004
Create Date: 2025-10-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create notifications table for Phase 4"""
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_notifications_task_id_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )

    # Create indexes
    op.create_index(
        op.f("idx_notifications_user"), "notifications", ["user_id"], unique=False
    )
    op.create_index(
        op.f("idx_notifications_sent"), "notifications", ["sent_at"], unique=False
    )
    # Partial index for unread notifications
    op.create_index(
        op.f("idx_notifications_unread"),
        "notifications",
        ["user_id", "read_at"],
        unique=False,
        postgresql_where=sa.text("read_at IS NULL"),
    )


def downgrade() -> None:
    """Drop notifications table"""
    op.drop_index(
        op.f("idx_notifications_unread"),
        table_name="notifications",
        postgresql_where=sa.text("read_at IS NULL"),
    )
    op.drop_index(op.f("idx_notifications_sent"), table_name="notifications")
    op.drop_index(op.f("idx_notifications_user"), table_name="notifications")
    op.drop_table("notifications")
