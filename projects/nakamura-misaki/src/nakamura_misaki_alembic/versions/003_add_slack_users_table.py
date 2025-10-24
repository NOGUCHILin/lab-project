"""Add slack_users table for caching Slack user data

Revision ID: 003_add_slack_users_table
Revises: ca1f08e0bc8a
Create Date: 2025-10-24

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "003_add_slack_users_table"
down_revision = "ca1f08e0bc8a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create slack_users table for caching Slack API user data"""
    op.create_table(
        "slack_users",
        sa.Column("user_id", sa.String(50), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("real_name", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_bot", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("slack_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Create indexes for common queries
    op.create_index("ix_slack_users_name", "slack_users", ["name"])
    op.create_index("ix_slack_users_email", "slack_users", ["email"])
    op.create_index("ix_slack_users_deleted", "slack_users", ["deleted"])
    op.create_index("ix_slack_users_synced_at", "slack_users", ["synced_at"])


def downgrade() -> None:
    """Drop slack_users table"""
    op.drop_index("ix_slack_users_synced_at", table_name="slack_users")
    op.drop_index("ix_slack_users_deleted", table_name="slack_users")
    op.drop_index("ix_slack_users_email", table_name="slack_users")
    op.drop_index("ix_slack_users_name", table_name="slack_users")
    op.drop_table("slack_users")
