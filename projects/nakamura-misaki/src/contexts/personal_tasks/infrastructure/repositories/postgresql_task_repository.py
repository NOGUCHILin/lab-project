"""PostgreSQL Task Repository implementation"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, String, select
from sqlalchemy import delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .....shared_kernel.domain.value_objects.task_status import TaskStatus
from ...domain.models.task import Task
from ...domain.repositories.task_repository import TaskRepository


class Base(DeclarativeBase):
    """SQLAlchemy declarative base"""

    pass


class TaskModel(Base):
    """SQLAlchemy model for Task"""

    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    assignee_user_id: Mapped[str] = mapped_column(String(50))
    creator_user_id: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        Enum("pending", "in_progress", "completed", "cancelled", name="task_status", create_type=False)
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PostgreSQLTaskRepository(TaskRepository):
    """PostgreSQL implementation of TaskRepository"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save(self, task: Task) -> None:
        """Save a task to database

        Args:
            task: Task domain entity to save
        """
        # Check if task exists
        stmt = select(TaskModel).where(TaskModel.id == task.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.title = task.title
            existing.description = task.description
            existing.assignee_user_id = task.assignee_user_id
            existing.creator_user_id = task.creator_user_id
            existing.status = task.status.value
            existing.due_at = task.due_at
            existing.completed_at = task.completed_at
            existing.updated_at = task.updated_at
        else:
            # Create new
            model = TaskModel(
                id=task.id,
                title=task.title,
                description=task.description,
                assignee_user_id=task.assignee_user_id,
                creator_user_id=task.creator_user_id,
                status=task.status.value,
                due_at=task.due_at,
                completed_at=task.completed_at,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
            self.session.add(model)

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get task by ID

        Args:
            task_id: Task UUID

        Returns:
            Task domain entity or None if not found
        """
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_all(self) -> list[Task]:
        """Find all tasks

        Returns:
            List of all Task domain entities
        """
        stmt = select(TaskModel).order_by(TaskModel.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def list_by_user(self, user_id: str, status: TaskStatus | None = None) -> list[Task]:
        """List tasks by user ID

        Args:
            user_id: User ID to filter by
            status: Optional status filter

        Returns:
            List of Task domain entities
        """
        stmt = select(TaskModel).where(TaskModel.assignee_user_id == user_id)

        if status:
            stmt = stmt.where(TaskModel.status == status.value)

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def list_due_today(self, user_id: str) -> list[Task]:
        """List tasks due today

        Args:
            user_id: User ID to filter by

        Returns:
            List of Task domain entities due today
        """
        today = datetime.now(UTC).date()

        stmt = select(TaskModel).where(
            TaskModel.assignee_user_id == user_id,
            TaskModel.due_at.isnot(None),
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        # Filter by date (SQLite doesn't support date() function)
        return [self._to_domain(model) for model in models if model.due_at and model.due_at.date() == today]

    async def list_overdue(self, user_id: str) -> list[Task]:
        """List overdue tasks

        Args:
            user_id: User ID to filter by

        Returns:
            List of overdue Task domain entities
        """
        now = datetime.now(UTC)

        stmt = select(TaskModel).where(
            TaskModel.assignee_user_id == user_id,
            TaskModel.due_at.isnot(None),
            TaskModel.due_at < now,
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def delete(self, task_id: UUID) -> None:
        """Delete a task

        Args:
            task_id: Task UUID to delete
        """
        stmt = sql_delete(TaskModel).where(TaskModel.id == task_id)
        await self.session.execute(stmt)

    def _to_domain(self, model: TaskModel) -> Task:
        """Convert database model to domain entity

        Args:
            model: SQLAlchemy TaskModel

        Returns:
            Task domain entity
        """
        # Reconstruct task using dataclass constructor
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            assignee_user_id=model.assignee_user_id,
            creator_user_id=model.creator_user_id,
            status=TaskStatus(model.status),
            due_at=model.due_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
