"""Can Start Task Use Case"""

from uuid import UUID

from ...domain.repositories.dependency_repository import DependencyRepository


class CanStartTaskUseCase:
    """Use case for checking if a task can be started (no blockers)"""

    def __init__(
        self,
        dependency_repository: DependencyRepository,
    ):
        """Initialize use case

        Args:
            dependency_repository: DependencyRepository instance
        """
        self._dependency_repo = dependency_repository

    async def execute(self, task_id: UUID) -> bool:
        """Execute use case

        Args:
            task_id: UUID of the task to check

        Returns:
            True if task can be started (no blockers), False otherwise
        """
        # Find all dependencies that are blocking this task
        blocking_dependencies = await self._dependency_repo.find_blocking_dependencies(task_id)

        # Task can start if there are no blocking dependencies
        return len(blocking_dependencies) == 0
