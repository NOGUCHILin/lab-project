"""RegisterTaskUseCase - タスク登録"""

from src.application.dto.task_dto import CreateTaskDTO, TaskDTO
from src.domain.models.task import Task
from src.domain.repositories.task_repository import TaskRepository


class RegisterTaskUseCase:
    """タスク登録ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        """タスクを登録"""
        if not dto.title:
            raise ValueError("Task title cannot be empty")

        task = Task(
            user_id=dto.user_id,
            title=dto.title,
            description=dto.description,
            due_at=dto.due_at,
        )

        created_task = await self._task_repository.create(task)

        return TaskDTO.from_entity(created_task)
