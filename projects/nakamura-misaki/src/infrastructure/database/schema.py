"""Database schema definitions using SQLAlchemy"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
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


# Handoffs table - temporarily kept for backward compatibility
# TODO: Remove handoffs feature entirely in Phase 2
class HandoffTable(Base):
    """Handoffs table for task handoff management (deprecated)"""

    __tablename__ = "handoffs"

    handoff_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), nullable=True)
    from_user_id = Column(String(100), nullable=False)
    to_user_id = Column(String(100), nullable=False)
    progress_note = Column(Text, nullable=False)
    next_steps = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    handoff_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        Index("idx_handoffs_from_user", "from_user_id"),
        Index("idx_handoffs_to_user", "to_user_id"),
        Index("idx_handoffs_status", "status"),
    )


# Alias for backward compatibility
HandoffModel = HandoffTable


class ProjectTable(Base):
    """Projects table for project management"""

    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    owner_user_id = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_projects_owner", "owner_user_id"),
        Index("idx_projects_status", "status"),
        Index("idx_projects_deadline", "deadline"),
    )


class ProjectTaskTable(Base):
    """Project-Task association table"""

    __tablename__ = "project_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("project_id", "task_id", name="uq_project_task"),
        Index("idx_project_tasks_project", "project_id"),
        Index("idx_project_tasks_task", "task_id"),
    )


class TaskDependencyTable(Base):
    """Task Dependencies table for managing task dependency relationships"""

    __tablename__ = "task_dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    blocking_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    blocked_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    dependency_type = Column(String(20), nullable=False, default="blocks")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("blocking_task_id", "blocked_task_id", name="uq_task_dependency"),
        Index("idx_dependencies_blocking", "blocking_task_id"),
        Index("idx_dependencies_blocked", "blocked_task_id"),
    )


class DailySummaryTable(Base):
    """Daily Summaries table for team analytics"""

    __tablename__ = "daily_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date = Column(Date, nullable=False)
    user_id = Column(String(100), nullable=True)
    tasks_completed = Column(Integer, nullable=False, default=0)
    tasks_pending = Column(Integer, nullable=False, default=0)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("date", "user_id", name="uq_daily_summaries_date_user"),
        Index("idx_daily_summaries_date", "date"),
        Index("idx_daily_summaries_user", "user_id"),
    )


class TeamMetricTable(Base):
    """Team Metrics table for team analytics"""

    __tablename__ = "team_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date = Column(Date, nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        Index("idx_team_metrics_date", "date"),
        Index("idx_team_metrics_type", "metric_type"),
    )
