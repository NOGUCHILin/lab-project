"""QueryDueTasks Use Case - Application layer"""

from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import TaskDTO


class QueryDueTasksUseCase:
    """Use Case for querying due/overdue tasks

    Provides two query methods:
    - execute_due_today: Retrieve tasks due today
    - execute_overdue: Retrieve overdue tasks

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

    async def execute_due_today(self, user_id: str) -> list[TaskDTO]:
        """Execute query for tasks due today

        Args:
            user_id: User ID to query tasks for

        Returns:
            List of TaskDTOs due today (empty list if none)
        """
        tasks = await self.task_repository.list_due_today(user_id)
        return [TaskDTO.from_domain(task) for task in tasks]

    async def execute_overdue(self, user_id: str) -> list[TaskDTO]:
        """Execute query for overdue tasks

        Args:
            user_id: User ID to query tasks for

        Returns:
            List of overdue TaskDTOs (empty list if none)
        """
        tasks = await self.task_repository.list_overdue(user_id)
        return [TaskDTO.from_domain(task) for task in tasks]
