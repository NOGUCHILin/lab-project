"""Get Dependency Chain Use Case"""

from uuid import UUID

from ...domain.repositories.dependency_repository import DependencyRepository
from ..dto.dependency_dto import DependencyChainDTO, DependencyDTO


class GetDependencyChainUseCase:
    """Use case for getting the full dependency chain of a task"""

    def __init__(
        self,
        dependency_repository: DependencyRepository,
    ):
        """Initialize use case

        Args:
            dependency_repository: DependencyRepository instance
        """
        self._dependency_repo = dependency_repository

    async def execute(self, task_id: UUID) -> DependencyChainDTO:
        """Execute use case

        Args:
            task_id: UUID of the task

        Returns:
            DependencyChainDTO with full dependency chain information
        """
        # Find dependencies that are blocking this task
        blocking_dependencies = await self._dependency_repo.find_blocking_dependencies(task_id)

        # Find dependencies that this task is blocking
        blocked_dependencies = await self._dependency_repo.find_blocked_dependencies(task_id)

        # Get all blocking task IDs recursively
        all_blocking_task_ids = await self._dependency_repo.find_all_blocking_task_ids(task_id)

        # Convert to DTOs
        blocking_dtos = [
            DependencyDTO(
                id=dep.id,
                blocking_task_id=dep.blocking_task_id,
                blocked_task_id=dep.blocked_task_id,
                dependency_type=dep.dependency_type.value,
                created_at=dep.created_at,
            )
            for dep in blocking_dependencies
        ]

        blocked_dtos = [
            DependencyDTO(
                id=dep.id,
                blocking_task_id=dep.blocking_task_id,
                blocked_task_id=dep.blocked_task_id,
                dependency_type=dep.dependency_type.value,
                created_at=dep.created_at,
            )
            for dep in blocked_dependencies
        ]

        return DependencyChainDTO(
            task_id=task_id,
            blocking_dependencies=blocking_dtos,
            blocked_dependencies=blocked_dtos,
            all_blocking_task_ids=all_blocking_task_ids,
        )
