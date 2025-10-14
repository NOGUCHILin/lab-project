"""QueryUserTasksUseCase - ユーザーのタスク一覧取得"""

from src.application.dto.task_dto import TaskDTO
from src.domain.repositories.task_repository import TaskRepository


class QueryUserTasksUseCase:
    """ユーザーのタスク一覧取得ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(
        self, user_id: str, status: str | None = None, limit: int = 100
    ) -> list[TaskDTO]:
        """ユーザーのタスク一覧を取得"""
        tasks = await self._task_repository.list_by_user(user_id, status, limit)

        return [TaskDTO.from_entity(task) for task in tasks]
