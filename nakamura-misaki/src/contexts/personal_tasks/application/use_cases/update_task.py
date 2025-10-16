"""UpdateTask Use Case - Application layer"""

from uuid import UUID

from ..dto.task_dto import UpdateTaskDTO, TaskDTO
from ...domain.repositories.task_repository import TaskRepository


class UpdateTaskUseCase:
    """Use Case for updating a task

    Orchestrates task update business logic:
    1. Retrieve task from repository
    2. Execute domain logic (task.update())
    3. Persist updated task
    4. Return TaskDTO for presentation
    """

    def __init__(self, task_repository: TaskRepository):
        """Initialize use case with dependencies

        Args:
            task_repository: Repository for task persistence
        """
        self.task_repository = task_repository

    async def execute(self, task_id: UUID, dto: UpdateTaskDTO) -> TaskDTO:
        """Execute the update task use case

        Args:
            task_id: ID of task to update
            dto: Update data (all fields optional)

        Returns:
            TaskDTO with updated task data

        Raises:
            ValueError: If task not found or validation fails
        """
        # Retrieve task
        task = await self.task_repository.get_by_id(task_id)
        if task is None:
            raise ValueError("Task not found")

        # Execute domain logic
        task.update(
            title=dto.title,
            description=dto.description,
            status=dto.status,
            due_at=dto.due_at
        )

        # Persist updated task
        await self.task_repository.save(task)

        # Return DTO for presentation
        return TaskDTO.from_domain(task)
