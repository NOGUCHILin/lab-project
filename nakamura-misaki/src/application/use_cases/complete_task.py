"""CompleteTaskUseCase - タスク完了"""

from uuid import UUID

from src.application.dto.task_dto import TaskDTO
from src.domain.repositories.task_repository import TaskRepository


class CompleteTaskUseCase:
    """タスク完了ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, task_id: UUID) -> TaskDTO:
        """タスクを完了"""
        task = await self._task_repository.get(task_id)

        if task is None:
            raise ValueError(f"Task not found: {task_id}")

        task.complete()

        updated_task = await self._task_repository.update(task)

        return TaskDTO.from_entity(updated_task)
