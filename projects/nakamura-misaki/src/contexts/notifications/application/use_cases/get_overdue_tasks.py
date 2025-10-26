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
        all_tasks = await self._task_repo.list_by_user(user_id)

        # Filter for overdue tasks (deadline in past and not completed)
        now = datetime.now()
        overdue_dtos = []

        for task in all_tasks:
            if task.due_at and task.due_at < now and task.status.value != "completed":
                days_overdue = (now - task.due_at).days
                overdue_dtos.append(
                    OverdueTaskDTO(
                        task_id=task.id,
                        title=task.title,
                        user_id=task.assignee_user_id,
                        deadline=task.due_at,
                        days_overdue=days_overdue,
                    )
                )

        # Sort by most overdue first
        overdue_dtos.sort(key=lambda x: x.days_overdue, reverse=True)

        return overdue_dtos
