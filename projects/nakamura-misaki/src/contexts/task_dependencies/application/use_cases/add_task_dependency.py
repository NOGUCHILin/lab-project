"""Add Task Dependency Use Case"""

from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository

from ...domain.entities.task_dependency import TaskDependency
from ...domain.repositories.dependency_repository import DependencyRepository
from ..dto.dependency_dto import CreateDependencyDTO, DependencyDTO


class AddTaskDependencyUseCase:
    """Use case for adding a task dependency

    This use case orchestrates between Task Dependencies and Personal Tasks contexts.
    """

    def __init__(
        self,
        dependency_repository: DependencyRepository,
        task_repository: TaskRepository,
    ):
        """Initialize use case

        Args:
            dependency_repository: DependencyRepository instance
            task_repository: TaskRepository instance (from Personal Tasks context)
        """
        self._dependency_repo = dependency_repository
        self._task_repo = task_repository

    async def execute(self, dto: CreateDependencyDTO) -> DependencyDTO:
        """Execute use case

        Args:
            dto: CreateDependencyDTO with blocking_task_id and blocked_task_id

        Returns:
            DependencyDTO with created dependency information

        Raises:
            ValueError: If tasks not found, self-dependency, or dependency already exists
        """
        # 1. Validate: no self-dependency
        if dto.blocking_task_id == dto.blocked_task_id:
            raise ValueError("Task cannot depend on itself")

        # 2. Verify blocking task exists (Personal Tasks Context)
        blocking_task = await self._task_repo.get_by_id(dto.blocking_task_id)
        if not blocking_task:
            raise ValueError(f"Blocking task {dto.blocking_task_id} not found")

        # 3. Verify blocked task exists (Personal Tasks Context)
        blocked_task = await self._task_repo.get_by_id(dto.blocked_task_id)
        if not blocked_task:
            raise ValueError(f"Blocked task {dto.blocked_task_id} not found")

        # 4. Check if dependency already exists
        exists = await self._dependency_repo.exists(
            blocking_task_id=dto.blocking_task_id,
            blocked_task_id=dto.blocked_task_id,
        )
        if exists:
            raise ValueError("Dependency already exists")

        # 5. Create dependency entity
        dependency = TaskDependency.create(
            blocking_task_id=dto.blocking_task_id,
            blocked_task_id=dto.blocked_task_id,
        )

        # 6. Persist dependency
        saved_dependency = await self._dependency_repo.save(dependency)

        # 7. Return DTO
        return DependencyDTO(
            id=saved_dependency.id,
            blocking_task_id=saved_dependency.blocking_task_id,
            blocked_task_id=saved_dependency.blocked_task_id,
            dependency_type=saved_dependency.dependency_type.value,
            created_at=saved_dependency.created_at,
        )
