"""Add Project Management tables

Revision ID: 002
Revises: 001
Create Date: 2025-10-26

Phase 1: Project Management Context
- projects table
- project_tasks table (many-to-many with tasks)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        "projects",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_user_id", sa.String(length=100), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("project_id"),
    )
    op.create_index("idx_projects_owner", "projects", ["owner_user_id"])
    op.create_index("idx_projects_status", "projects", ["status"])
    op.create_index("idx_projects_deadline", "projects", ["deadline"])

    # Create project_tasks table (many-to-many relationship)
    op.create_table(
        "project_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "task_id", name="uq_project_task"),
    )
    op.create_index("idx_project_tasks_project", "project_tasks", ["project_id"])
    op.create_index("idx_project_tasks_task", "project_tasks", ["task_id"])


def downgrade() -> None:
    op.drop_table("project_tasks")
    op.drop_table("projects")
