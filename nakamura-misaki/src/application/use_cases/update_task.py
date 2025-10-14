"""UpdateTaskUseCase - タスク更新"""

from src.application.dto.task_dto import TaskDTO, UpdateTaskDTO
from src.domain.models.task import TaskStatus
from src.domain.repositories.task_repository import TaskRepository


class UpdateTaskUseCase:
    """タスク更新ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, dto: UpdateTaskDTO) -> TaskDTO:
        """タスクを更新"""
        task = await self._task_repository.get(dto.task_id)

        if task is None:
            raise ValueError(f"Task not found: {dto.task_id}")

        if dto.title is not None:
            task.title = dto.title

        if dto.description is not None:
            task.description = dto.description

        if dto.status is not None:
            task.status = TaskStatus(dto.status)

        if dto.due_at is not None:
            task.due_at = dto.due_at

        updated_task = await self._task_repository.update(task)

        return TaskDTO.from_entity(updated_task)
