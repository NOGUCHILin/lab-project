"""Dependency Repository Interface"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.task_dependency import TaskDependency


class DependencyRepository(ABC):
    """Dependency Repository Interface (Port)

    Defines the contract for task dependency persistence operations.
    """

    @abstractmethod
    async def save(self, dependency: TaskDependency) -> TaskDependency:
        """Save a task dependency

        Args:
            dependency: TaskDependency entity to save

        Returns:
            Saved TaskDependency entity
        """
        pass

    @abstractmethod
    async def find_by_id(self, dependency_id: UUID) -> TaskDependency | None:
        """Find a dependency by ID

        Args:
            dependency_id: UUID of the dependency

        Returns:
            TaskDependency entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, dependency_id: UUID) -> None:
        """Delete a dependency

        Args:
            dependency_id: UUID of the dependency to delete
        """
        pass

    @abstractmethod
    async def delete_by_tasks(
        self,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
    ) -> None:
        """Delete a dependency by task IDs

        Args:
            blocking_task_id: UUID of the blocking task
            blocked_task_id: UUID of the blocked task
        """
        pass

    @abstractmethod
    async def find_blocking_dependencies(
        self,
        task_id: UUID,
    ) -> list[TaskDependency]:
        """Find dependencies that are blocking a task

        Args:
            task_id: UUID of the task that is being blocked

        Returns:
            List of TaskDependency entities where task_id is the blocked_task_id
        """
        pass

    @abstractmethod
    async def find_blocked_dependencies(
        self,
        task_id: UUID,
    ) -> list[TaskDependency]:
        """Find dependencies that a task is blocking

        Args:
            task_id: UUID of the task that is blocking

        Returns:
            List of TaskDependency entities where task_id is the blocking_task_id
        """
        pass

    @abstractmethod
    async def exists(
        self,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
    ) -> bool:
        """Check if a dependency already exists

        Args:
            blocking_task_id: UUID of the blocking task
            blocked_task_id: UUID of the blocked task

        Returns:
            True if dependency exists, False otherwise
        """
        pass

    @abstractmethod
    async def find_all_blocking_task_ids(
        self,
        task_id: UUID,
    ) -> list[UUID]:
        """Find all task IDs that are blocking a task (for dependency chain)

        Args:
            task_id: UUID of the task

        Returns:
            List of blocking task UUIDs
        """
        pass
