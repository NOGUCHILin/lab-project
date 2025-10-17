"""Add tasks table for Personal Tasks context

Revision ID: 002_add_tasks_table
Revises: b0bbf866ebc2
Create Date: 2025-10-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_tasks_table'
down_revision = 'b0bbf866ebc2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tasks table for Personal Tasks bounded context"""
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assignee_user_id', sa.String(50), nullable=False),
        sa.Column('creator_user_id', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create indexes for common queries
    op.create_index(
        'ix_tasks_assignee_user_id',
        'tasks',
        ['assignee_user_id']
    )
    op.create_index(
        'ix_tasks_status',
        'tasks',
        ['status']
    )
    op.create_index(
        'ix_tasks_due_at',
        'tasks',
        ['due_at']
    )
    op.create_index(
        'ix_tasks_assignee_status',
        'tasks',
        ['assignee_user_id', 'status']
    )


def downgrade() -> None:
    """Drop tasks table"""
    op.drop_index('ix_tasks_assignee_status', table_name='tasks')
    op.drop_index('ix_tasks_due_at', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_assignee_user_id', table_name='tasks')
    op.drop_table('tasks')
