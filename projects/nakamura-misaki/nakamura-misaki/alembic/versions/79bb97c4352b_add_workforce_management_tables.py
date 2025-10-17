"""Add workforce management tables

Revision ID: 79bb97c4352b
Revises: 002_add_tasks_table
Create Date: 2025-10-17 11:57:09.000263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79bb97c4352b'
down_revision: Union[str, Sequence[str], None] = '002_add_tasks_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create skill_category enum
    op.execute(
        """
        CREATE TYPE skill_category AS ENUM (
            '顧客対応',
            '物流',
            '査定・修理',
            '販売',
            '管理',
            '店舗'
        )
        """
    )

    # Create employees table
    op.create_table(
        "employees",
        sa.Column("employee_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_employees_active", "employees", ["is_active"])

    # Create business_skills table
    op.create_table(
        "business_skills",
        sa.Column("skill_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_name", sa.String(100), nullable=False, unique=True),
        sa.Column("category", sa.Enum(name="skill_category"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_skills_active", "business_skills", ["is_active"])
    op.create_index("idx_skills_category", "business_skills", ["category"])

    # Create employee_skills association table
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("employee_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("acquired_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["business_skills.skill_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )
    op.create_index("idx_employee_skills_employee", "employee_skills", ["employee_id"])
    op.create_index("idx_employee_skills_skill", "employee_skills", ["skill_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_employee_skills_skill", table_name="employee_skills")
    op.drop_index("idx_employee_skills_employee", table_name="employee_skills")
    op.drop_table("employee_skills")

    op.drop_index("idx_skills_category", table_name="business_skills")
    op.drop_index("idx_skills_active", table_name="business_skills")
    op.drop_table("business_skills")

    op.drop_index("idx_employees_active", table_name="employees")
    op.drop_table("employees")

    op.execute("DROP TYPE skill_category")
