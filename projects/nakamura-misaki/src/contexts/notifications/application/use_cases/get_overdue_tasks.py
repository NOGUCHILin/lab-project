"""Get Overdue Tasks Use Case"""

from datetime import datetime

from src.contexts.personal_tasks.domain.repositories.task_repository import (
    TaskRepository,
)

from ..dto.notification_dto import OverdueTaskDTO


class GetOverdueTasksUseCase:
    """Use case for finding overdue tasks"""

    def __init__(self, task_repository: TaskRepository):
        """Initialize use case

        Args:
            task_repository: Repository for tasks
        """
        self._task_repo = task_repository

    async def execute(self, user_id: str) -> list[OverdueTaskDTO]:
        """Find all overdue tasks for a user

        Args:
            user_id: User ID to find overdue tasks for

        Returns:
            List of OverdueTaskDTO for tasks past their deadline
        """
        # Get all tasks for user
        all_tasks = await self._task_repo.find_by_user_id(user_id)

        # Filter for overdue tasks (deadline in past and not completed)
        now = datetime.now()
        overdue_dtos = []

        for task in all_tasks:
            if task.deadline and task.deadline < now and task.status != "completed":
                days_overdue = (now - task.deadline).days
                overdue_dtos.append(
                    OverdueTaskDTO(
                        task_id=task.id,
                        title=task.title,
                        user_id=task.user_id,
                        deadline=task.deadline,
                        days_overdue=days_overdue,
                    )
                )

        # Sort by most overdue first
        overdue_dtos.sort(key=lambda x: x.days_overdue, reverse=True)

        return overdue_dtos
