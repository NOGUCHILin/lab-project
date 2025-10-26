"""Initial schema - All tables

Revision ID: 001
Revises:
Create Date: 2025-10-26

Consolidated schema including:
- tasks (Personal Tasks context)
- conversations (Conversations context)
- employees, business_skills, employee_skills (Workforce Management context)
- handoffs (deprecated, will be removed in Phase 2)
- slack_users (Infrastructure)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create task_status enum (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create skill_category enum (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE skill_category AS ENUM ('顧客対応', '物流', '査定・修理', '販売', '管理', '店舗');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assignee_user_id", sa.String(length=100), nullable=False),
        sa.Column("creator_user_id", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", "cancelled", name="task_status", create_type=False),
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tasks_assignee_due", "tasks", ["assignee_user_id", "due_at"])
    op.create_index("idx_tasks_assignee_status", "tasks", ["assignee_user_id", "status"])
    op.create_index(op.f("ix_tasks_assignee_user_id"), "tasks", ["assignee_user_id"])
    op.create_index(op.f("ix_tasks_due_at"), "tasks", ["due_at"])
    op.create_index(op.f("ix_tasks_status"), "tasks", ["status"])

    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("channel_id", sa.String(length=100), nullable=False),
        sa.Column("messages", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("conversation_id"),
        sa.UniqueConstraint("user_id", "channel_id", name="uq_conversations_user_channel"),
    )
    op.create_index("idx_conversations_last_message", "conversations", ["last_message_at"])
    op.create_index("idx_conversations_user_channel", "conversations", ["user_id", "channel_id"])
    op.create_index(op.f("ix_conversations_channel_id"), "conversations", ["channel_id"])
    op.create_index(op.f("ix_conversations_user_id"), "conversations", ["user_id"])

    # Create employees table
    op.create_table(
        "employees",
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("employee_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("idx_employees_active", "employees", ["is_active"])

    # Create business_skills table
    op.create_table(
        "business_skills",
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column(
            "category",
            sa.Enum("顧客対応", "物流", "査定・修理", "販売", "管理", "店舗", name="skill_category", create_type=False),
            nullable=False,
        ),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("skill_id"),
        sa.UniqueConstraint("skill_name"),
    )
    op.create_index("idx_skills_active", "business_skills", ["is_active"])
    op.create_index("idx_skills_category", "business_skills", ["category"])

    # Create employee_skills association table
    op.create_table(
        "employee_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("acquired_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["business_skills.skill_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )
    op.create_index("idx_employee_skills_employee", "employee_skills", ["employee_id"])
    op.create_index("idx_employee_skills_skill", "employee_skills", ["skill_id"])

    # Create handoffs table (deprecated, will be removed in Phase 2)
    op.create_table(
        "handoffs",
        sa.Column("handoff_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("from_user_id", sa.String(length=100), nullable=False),
        sa.Column("to_user_id", sa.String(length=100), nullable=False),
        sa.Column("progress_note", sa.Text(), nullable=False),
        sa.Column("next_steps", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("handoff_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("handoff_id"),
    )
    op.create_index("idx_handoffs_from_user", "handoffs", ["from_user_id"])
    op.create_index("idx_handoffs_status", "handoffs", ["status"])
    op.create_index("idx_handoffs_to_user", "handoffs", ["to_user_id"])

    # Create slack_users table
    op.create_table(
        "slack_users",
        sa.Column("user_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("real_name", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("is_bot", sa.Boolean(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("slack_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("slack_users")
    op.drop_table("handoffs")
    op.drop_table("employee_skills")
    op.drop_table("business_skills")
    op.drop_table("employees")
    op.drop_table("conversations")
    op.drop_table("tasks")
    op.execute("DROP TYPE IF EXISTS skill_category")
    op.execute("DROP TYPE IF EXISTS task_status")
