"""Add team analytics tables

Revision ID: 004
Revises: 003
Create Date: 2025-10-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema - Add team analytics tables"""
    # Create daily_summaries table
    op.create_table(
        "daily_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("tasks_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tasks_pending", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_summaries")),
        sa.UniqueConstraint("date", "user_id", name=op.f("uq_daily_summaries_date_user")),
    )
    op.create_index(
        op.f("idx_daily_summaries_date"),
        "daily_summaries",
        ["date"],
        unique=False,
    )
    op.create_index(
        op.f("idx_daily_summaries_user"),
        "daily_summaries",
        ["user_id"],
        unique=False,
    )

    # Create team_metrics table
    op.create_table(
        "team_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("metric_type", sa.String(length=50), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_team_metrics")),
    )
    op.create_index(
        op.f("idx_team_metrics_date"),
        "team_metrics",
        ["date"],
        unique=False,
    )
    op.create_index(
        op.f("idx_team_metrics_type"),
        "team_metrics",
        ["metric_type"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema - Remove team analytics tables"""
    op.drop_index(op.f("idx_team_metrics_type"), table_name="team_metrics")
    op.drop_index(op.f("idx_team_metrics_date"), table_name="team_metrics")
    op.drop_table("team_metrics")

    op.drop_index(op.f("idx_daily_summaries_user"), table_name="daily_summaries")
    op.drop_index(op.f("idx_daily_summaries_date"), table_name="daily_summaries")
    op.drop_table("daily_summaries")
