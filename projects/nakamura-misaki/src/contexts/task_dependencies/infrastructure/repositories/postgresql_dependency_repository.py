"""PostgreSQL Dependency Repository Implementation"""

from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import TaskDependencyTable

from ...domain.entities.task_dependency import TaskDependency
from ...domain.repositories.dependency_repository import DependencyRepository
from ...domain.value_objects.dependency_type import DependencyType


class PostgreSQLDependencyRepository(DependencyRepository):
    """PostgreSQL implementation of DependencyRepository"""

    def __init__(self, session: AsyncSession):
        """Initialize repository

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, dependency: TaskDependency) -> TaskDependency:
        """Save a task dependency"""
        # Check if dependency exists
        stmt = select(TaskDependencyTable).where(TaskDependencyTable.id == dependency.id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing (unlikely for immutable dependencies, but included for completeness)
            existing.blocking_task_id = dependency.blocking_task_id
            existing.blocked_task_id = dependency.blocked_task_id
            existing.dependency_type = dependency.dependency_type.value
        else:
            # Create new dependency
            dependency_row = TaskDependencyTable(
                id=dependency.id,
                blocking_task_id=dependency.blocking_task_id,
                blocked_task_id=dependency.blocked_task_id,
                dependency_type=dependency.dependency_type.value,
                created_at=dependency.created_at,
            )
            self._session.add(dependency_row)

        await self._session.commit()
        return dependency

    async def find_by_id(self, dependency_id: UUID) -> TaskDependency | None:
        """Find a dependency by ID"""
        stmt = select(TaskDependencyTable).where(TaskDependencyTable.id == dependency_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            return None

        return TaskDependency.reconstruct(
            id=row.id,
            blocking_task_id=row.blocking_task_id,
            blocked_task_id=row.blocked_task_id,
            dependency_type=DependencyType.from_string(row.dependency_type),
            created_at=row.created_at,
        )

    async def delete(self, dependency_id: UUID) -> None:
        """Delete a dependency"""
        stmt = delete(TaskDependencyTable).where(TaskDependencyTable.id == dependency_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def delete_by_tasks(
        self,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
    ) -> None:
        """Delete a dependency by task IDs"""
        stmt = delete(TaskDependencyTable).where(
            and_(
                TaskDependencyTable.blocking_task_id == blocking_task_id,
                TaskDependencyTable.blocked_task_id == blocked_task_id,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def find_blocking_dependencies(
        self,
        task_id: UUID,
    ) -> list[TaskDependency]:
        """Find dependencies that are blocking a task"""
        stmt = select(TaskDependencyTable).where(TaskDependencyTable.blocked_task_id == task_id)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        return [
            TaskDependency.reconstruct(
                id=row.id,
                blocking_task_id=row.blocking_task_id,
                blocked_task_id=row.blocked_task_id,
                dependency_type=DependencyType.from_string(row.dependency_type),
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def find_blocked_dependencies(
        self,
        task_id: UUID,
    ) -> list[TaskDependency]:
        """Find dependencies that a task is blocking"""
        stmt = select(TaskDependencyTable).where(TaskDependencyTable.blocking_task_id == task_id)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        return [
            TaskDependency.reconstruct(
                id=row.id,
                blocking_task_id=row.blocking_task_id,
                blocked_task_id=row.blocked_task_id,
                dependency_type=DependencyType.from_string(row.dependency_type),
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def exists(
        self,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
    ) -> bool:
        """Check if a dependency already exists"""
        stmt = select(TaskDependencyTable).where(
            and_(
                TaskDependencyTable.blocking_task_id == blocking_task_id,
                TaskDependencyTable.blocked_task_id == blocked_task_id,
            )
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        return row is not None

    async def find_all_blocking_task_ids(
        self,
        task_id: UUID,
    ) -> list[UUID]:
        """Find all task IDs that are blocking a task (for dependency chain)

        This is a simplified implementation that returns direct blockers.
        For full recursive dependency chain, a recursive CTE query would be needed.
        """
        stmt = select(TaskDependencyTable.blocking_task_id).where(TaskDependencyTable.blocked_task_id == task_id)
        result = await self._session.execute(stmt)
        blocking_ids = result.scalars().all()

        return list(blocking_ids)
