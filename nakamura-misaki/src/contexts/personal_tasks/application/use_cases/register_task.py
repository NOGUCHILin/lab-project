"""RegisterTask Use Case - Application layer"""

from ...domain.models.task import Task
from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import CreateTaskDTO, TaskDTO


class RegisterTaskUseCase:
    """Use Case for registering a new task

    Orchestrates task creation business logic:
    1. Create Task domain entity from DTO
    2. Persist task via repository
    3. Return TaskDTO for presentation

    This follows Clean Architecture principles:
    - Application layer orchestrates domain logic
    - Depends on domain abstractions (Task, TaskRepository)
    - No dependencies on infrastructure or adapters
    """

    def __init__(self, task_repository: TaskRepository):
        """Initialize use case with dependencies

        Args:
            task_repository: Repository for task persistence
        """
        self.task_repository = task_repository

    async def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        """Execute the register task use case

        Args:
            dto: Task creation data from UI/API

        Returns:
            TaskDTO with created task data
        """
        # Create domain entity
        task = Task.create(
            title=dto.title,
            assignee_user_id=dto.assignee_user_id,
            creator_user_id=dto.creator_user_id,
            description=dto.description,
            due_at=dto.due_at
        )

        # Persist via repository
        await self.task_repository.save(task)

        # Return DTO for presentation
        return TaskDTO.from_domain(task)
