"""Database schema definitions using SQLAlchemy"""

from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from ...domain.models.task import TaskStatus


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""

    pass


class TaskTable(Base):
    """Tasks table"""

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assignee_user_id = Column(String(100), nullable=False, index=True)
    creator_user_id = Column(String(100), nullable=False)
    status = Column(
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
    )
    due_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_tasks_assignee_status", "assignee_user_id", "status"),
        Index("idx_tasks_assignee_due", "assignee_user_id", "due_at"),
    )


class HandoffTable(Base):
    """Handoffs table"""

    __tablename__ = "handoffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    from_user_id = Column(String(100), nullable=False)
    to_user_id = Column(String(100), nullable=False, index=True)
    progress_note = Column(Text, nullable=False)
    next_steps = Column(Text, nullable=False)
    handoff_at = Column(DateTime, nullable=False, index=True)
    reminded_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        Index("idx_handoffs_to_user_pending", "to_user_id", "completed_at"),
        Index("idx_handoffs_reminder", "handoff_at", "reminded_at", "completed_at"),
    )


class NoteTable(Base):
    """Notes table with vector embedding support"""

    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="general")
    embedding = Column(Vector(1024), nullable=True)  # Claude API: 1024-dim
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        Index("idx_notes_user_created", "user_id", "created_at"),
        # Vector similarity search index (ivfflat)
        Index(
            "idx_notes_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class SessionTable(Base):
    """Sessions table"""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    workspace_path = Column(String(500), nullable=False)
    message_count = Column(Text, nullable=False, default="0")
    is_active = Column(Text, nullable=False, default="true")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_active = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class ConversationTable(Base):
    """Conversations table for managing chat history with Claude.

    Stores conversation history with 24-hour TTL.
    Messages are stored in JSONB format compatible with Claude Messages API.
    """

    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(100), nullable=False, index=True)
    channel_id = Column(String(100), nullable=False, index=True)
    # Use JSON type (compatible with both PostgreSQL JSONB and SQLite JSON)
    messages = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now())
    last_message_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(), index=True)

    __table_args__ = (
        Index("idx_conversations_user_channel", "user_id", "channel_id"),
        Index("idx_conversations_last_message", "last_message_at"),
    )
