"""Task Repository interface - Domain layer"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.shared_kernel.domain.value_objects.task_status import TaskStatus

from ..models.task import Task


class TaskRepository(ABC):
    """Repository interface for Task aggregate

    Defines persistence operations for Task entities.
    Implementations are provided in the Infrastructure layer.

    This interface follows Repository pattern from DDD:
    - Domain layer defines the interface
    - Infrastructure layer provides concrete implementation
    - Application layer depends on this abstraction
    """

    @abstractmethod
    async def save(self, task: Task) -> None:
        """Save a task (create or update)

        Args:
            task: Task entity to persist
        """
        pass

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get task by ID

        Args:
            task_id: Task unique identifier

        Returns:
            Task if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        status: TaskStatus | None = None
    ) -> list[Task]:
        """List tasks assigned to a user

        Args:
            user_id: User ID to filter by
            status: Optional status filter

        Returns:
            List of tasks (empty list if none found)
        """
        pass

    @abstractmethod
    async def list_due_today(self, user_id: str) -> list[Task]:
        """List tasks due today for a user

        Args:
            user_id: User ID to filter by

        Returns:
            List of tasks due today (empty list if none)
        """
        pass

    @abstractmethod
    async def list_overdue(self, user_id: str) -> list[Task]:
        """List overdue tasks for a user

        Args:
            user_id: User ID to filter by

        Returns:
            List of overdue tasks (empty list if none)
        """
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> None:
        """Delete a task

        Args:
            task_id: Task ID to delete
        """
        pass
