"""Remove Task Dependency Use Case"""

from uuid import UUID

from ...domain.repositories.dependency_repository import DependencyRepository


class RemoveTaskDependencyUseCase:
    """Use case for removing a task dependency"""

    def __init__(
        self,
        dependency_repository: DependencyRepository,
    ):
        """Initialize use case

        Args:
            dependency_repository: DependencyRepository instance
        """
        self._dependency_repo = dependency_repository

    async def execute(
        self,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
    ) -> None:
        """Execute use case

        Args:
            blocking_task_id: UUID of the blocking task
            blocked_task_id: UUID of the blocked task
        """
        # Delete dependency by task IDs
        await self._dependency_repo.delete_by_tasks(
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
        )
