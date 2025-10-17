"""Initial schema (tasks, handoffs, conversations, notes, sessions)

Revision ID: 001
Revises:
Create Date: 2025-10-16 12:23:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create task_status enum
    op.execute("CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled')")

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assignee_user_id', sa.String(length=100), nullable=False),
        sa.Column('creator_user_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='task_status'), nullable=False),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_assignee_due', 'tasks', ['assignee_user_id', 'due_at'])
    op.create_index('idx_tasks_assignee_status', 'tasks', ['assignee_user_id', 'status'])
    op.create_index(op.f('ix_tasks_assignee_user_id'), 'tasks', ['assignee_user_id'])
    op.create_index(op.f('ix_tasks_due_at'), 'tasks', ['due_at'])
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'])

    # Create handoffs table
    op.create_table(
        'handoffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('from_user_id', sa.String(length=100), nullable=False),
        sa.Column('to_user_id', sa.String(length=100), nullable=False),
        sa.Column('progress_note', sa.Text(), nullable=False),
        sa.Column('next_steps', sa.Text(), nullable=False),
        sa.Column('handoff_at', sa.DateTime(), nullable=False),
        sa.Column('reminded_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_handoffs_reminder', 'handoffs', ['handoff_at', 'reminded_at', 'completed_at'])
    op.create_index('idx_handoffs_to_user_pending', 'handoffs', ['to_user_id', 'completed_at'])
    op.create_index(op.f('ix_handoffs_handoff_at'), 'handoffs', ['handoff_at'])
    op.create_index(op.f('ix_handoffs_to_user_id'), 'handoffs', ['to_user_id'])

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('channel_id', sa.String(length=100), nullable=False),
        sa.Column('messages', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('conversation_id')
    )
    op.create_index('idx_conversations_last_message', 'conversations', ['last_message_at'])
    op.create_index('idx_conversations_user_channel', 'conversations', ['user_id', 'channel_id'])
    op.create_index(op.f('ix_conversations_channel_id'), 'conversations', ['channel_id'])
    op.create_index(op.f('ix_conversations_last_message_at'), 'conversations', ['last_message_at'])
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'])

    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notes_user_created', 'notes', ['user_id', 'created_at'])
    op.create_index(op.f('ix_notes_session_id'), 'notes', ['session_id'])
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'])
    # Vector index (ivfflat for cosine similarity)
    op.execute('CREATE INDEX idx_notes_embedding ON notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('workspace_path', sa.String(length=500), nullable=False),
        sa.Column('message_count', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_active', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_sessions_session_id'), 'sessions', ['session_id'], unique=True)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_session_id'), table_name='sessions')
    op.drop_table('sessions')

    op.execute('DROP INDEX IF EXISTS idx_notes_embedding')
    op.drop_index(op.f('ix_notes_user_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_session_id'), table_name='notes')
    op.drop_index('idx_notes_user_created', table_name='notes')
    op.drop_table('notes')

    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_last_message_at'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_channel_id'), table_name='conversations')
    op.drop_index('idx_conversations_user_channel', table_name='conversations')
    op.drop_index('idx_conversations_last_message', table_name='conversations')
    op.drop_table('conversations')

    op.drop_index(op.f('ix_handoffs_to_user_id'), table_name='handoffs')
    op.drop_index(op.f('ix_handoffs_handoff_at'), table_name='handoffs')
    op.drop_index('idx_handoffs_to_user_pending', table_name='handoffs')
    op.drop_index('idx_handoffs_reminder', table_name='handoffs')
    op.drop_table('handoffs')

    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_due_at'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_assignee_user_id'), table_name='tasks')
    op.drop_index('idx_tasks_assignee_status', table_name='tasks')
    op.drop_index('idx_tasks_assignee_due', table_name='tasks')
    op.drop_table('tasks')

    op.execute('DROP TYPE task_status')
