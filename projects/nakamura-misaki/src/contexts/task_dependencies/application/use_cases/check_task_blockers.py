"""Check Task Blockers Use Case"""

from uuid import UUID

from ...domain.repositories.dependency_repository import DependencyRepository
from ..dto.dependency_dto import BlockerCheckDTO


class CheckTaskBlockersUseCase:
    """Use case for checking if a task is blocked by other tasks"""

    def __init__(
        self,
        dependency_repository: DependencyRepository,
    ):
        """Initialize use case

        Args:
            dependency_repository: DependencyRepository instance
        """
        self._dependency_repo = dependency_repository

    async def execute(self, task_id: UUID) -> BlockerCheckDTO:
        """Execute use case

        Args:
            task_id: UUID of the task to check

        Returns:
            BlockerCheckDTO with blocker information
        """
        # Find all dependencies that are blocking this task
        blocking_dependencies = await self._dependency_repo.find_blocking_dependencies(task_id)

        # Extract blocking task IDs
        blocking_task_ids = [dep.blocking_task_id for dep in blocking_dependencies]

        # Determine if task is blocked
        is_blocked = len(blocking_dependencies) > 0
        can_start = not is_blocked

        return BlockerCheckDTO(
            task_id=task_id,
            is_blocked=is_blocked,
            blocking_task_ids=blocking_task_ids,
            blocking_task_count=len(blocking_task_ids),
            can_start=can_start,
            blocker_details=None,  # Optional: 詳細情報は将来実装
        )
