"""Database schema definitions using SQLAlchemy"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
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
