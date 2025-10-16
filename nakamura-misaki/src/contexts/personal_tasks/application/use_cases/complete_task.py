"""CompleteTask Use Case - Application layer"""

from uuid import UUID

from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import TaskDTO


class CompleteTaskUseCase:
    """Use Case for completing a task

    Orchestrates task completion business logic:
    1. Retrieve task from repository
    2. Execute domain logic (task.complete())
    3. Persist updated task
    4. Return TaskDTO for presentation

    This follows Clean Architecture principles:
    - Application layer orchestrates domain logic
    - Domain entity enforces business rules
    - No dependencies on infrastructure or adapters
    """

    def __init__(self, task_repository: TaskRepository):
        """Initialize use case with dependencies

        Args:
            task_repository: Repository for task persistence
        """
        self.task_repository = task_repository

    async def execute(self, task_id: UUID) -> TaskDTO:
        """Execute the complete task use case

        Args:
            task_id: ID of task to complete

        Returns:
            TaskDTO with completed task data

        Raises:
            ValueError: If task not found or already completed
        """
        # Retrieve task
        task = await self.task_repository.get_by_id(task_id)
        if task is None:
            raise ValueError("Task not found")

        # Execute domain logic (raises ValueError if already completed)
        task.complete()

        # Persist updated task
        await self.task_repository.save(task)

        # Return DTO for presentation
        return TaskDTO.from_domain(task)
