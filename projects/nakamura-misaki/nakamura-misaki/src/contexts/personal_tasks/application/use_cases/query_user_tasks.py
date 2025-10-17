"""QueryUserTasks Use Case - Application layer"""

from src.shared_kernel.domain.value_objects.task_status import TaskStatus

from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import TaskDTO


class QueryUserTasksUseCase:
    """Use Case for querying user's tasks

    Retrieves tasks assigned to a user, optionally filtered by status.

    This is a query use case (read-only):
    - No domain logic execution
    - No state changes
    - Simple repository query + DTO conversion
    """

    def __init__(self, task_repository: TaskRepository):
        """Initialize use case with dependencies

        Args:
            task_repository: Repository for task queries
        """
        self.task_repository = task_repository

    async def execute(
        self,
        user_id: str,
        status: TaskStatus | None = None
    ) -> list[TaskDTO]:
        """Execute the query user tasks use case

        Args:
            user_id: User ID to query tasks for
            status: Optional status filter

        Returns:
            List of TaskDTOs (empty list if no tasks found)
        """
        # Query tasks from repository
        tasks = await self.task_repository.list_by_user(user_id, status)

        # Convert to DTOs
        return [TaskDTO.from_domain(task) for task in tasks]
