"""QueryTodayTasksUseCase - 今日のタスク取得"""

from src.application.dto.task_dto import TaskDTO
from src.domain.repositories.task_repository import TaskRepository


class QueryTodayTasksUseCase:
    """今日のタスク取得ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, user_id: str) -> list[TaskDTO]:
        """今日のタスクを取得"""
        tasks = await self._task_repository.list_due_today(user_id)

        return [TaskDTO.from_entity(task) for task in tasks]
