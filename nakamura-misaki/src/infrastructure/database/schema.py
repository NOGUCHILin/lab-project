"""Database schema definitions using SQLAlchemy"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from src.contexts.workforce_management.domain.value_objects.skill_category import SkillCategory
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


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


class EmployeeTable(Base):
    """Employees table for workforce management"""

    __tablename__ = "employees"

    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (Index("idx_employees_active", "is_active"),)


class BusinessSkillTable(Base):
    """Business skills table for workforce management"""

    __tablename__ = "business_skills"

    skill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    skill_name = Column(String(100), nullable=False, unique=True)
    category = Column(
        Enum(SkillCategory, name="skill_category"),
        nullable=False,
    )
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_skills_active", "is_active"),
        Index("idx_skills_category", "category"),
    )


class EmployeeSkillTable(Base):
    """Employee skills association table"""

    __tablename__ = "employee_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id = Column(
        UUID(as_uuid=True),
        ForeignKey("business_skills.skill_id", ondelete="CASCADE"),
        nullable=False,
    )
    acquired_at = Column(DateTime, nullable=False, default=datetime.now)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
        Index("idx_employee_skills_employee", "employee_id"),
        Index("idx_employee_skills_skill", "skill_id"),
    )
