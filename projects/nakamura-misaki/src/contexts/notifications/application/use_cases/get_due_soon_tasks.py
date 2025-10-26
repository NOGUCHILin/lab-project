"""Get Due Soon Tasks Use Case"""

from datetime import datetime, timedelta

from src.contexts.personal_tasks.domain.repositories.task_repository import (
    TaskRepository,
)

from ..dto.notification_dto import DueSoonTaskDTO


class GetDueSoonTasksUseCase:
    """Use case for finding tasks due soon"""

    def __init__(self, task_repository: TaskRepository):
        """Initialize use case

        Args:
            task_repository: Repository for tasks
        """
        self._task_repo = task_repository

    async def execute(
        self, user_id: str, hours: int = 24
    ) -> list[DueSoonTaskDTO]:
        """Find all tasks due within specified hours for a user

        Args:
            user_id: User ID to find tasks for
            hours: Number of hours to look ahead (default: 24)

        Returns:
            List of DueSoonTaskDTO for tasks due within specified hours

        Raises:
            ValueError: If hours is not positive
        """
        if hours <= 0:
            raise ValueError("hours must be positive")

        # Get all tasks for user
        all_tasks = await self._task_repo.list_by_user(user_id)

        # Filter for tasks due within specified hours
        now = datetime.now()
        cutoff_time = now + timedelta(hours=hours)
        due_soon_dtos = []

        for task in all_tasks:
            if (
                task.due_at
                and now <= task.due_at <= cutoff_time
                and task.status.value != "completed"
            ):
                hours_until_due = (task.due_at - now).total_seconds() / 3600
                due_soon_dtos.append(
                    DueSoonTaskDTO(
                        task_id=task.id,
                        title=task.title,
                        user_id=task.assignee_user_id,
                        deadline=task.due_at,
                        hours_until_due=hours_until_due,
                    )
                )

        # Sort by soonest deadline first
        due_soon_dtos.sort(key=lambda x: x.hours_until_due)

        return due_soon_dtos
