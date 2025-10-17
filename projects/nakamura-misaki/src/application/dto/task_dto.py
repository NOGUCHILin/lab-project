"""Task Data Transfer Objects"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateTaskDTO:
    """タスク作成用DTO"""

    user_id: str
    title: str
    description: str = ""
    due_at: datetime | None = None


@dataclass
class UpdateTaskDTO:
    """タスク更新用DTO"""

    task_id: UUID
    title: str | None = None
    description: str | None = None
    status: str | None = None
    due_at: datetime | None = None


@dataclass
class TaskDTO:
    """タスク出力用DTO"""

    id: UUID
    user_id: str
    title: str
    description: str
    status: str
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    @classmethod
    def from_entity(cls, task) -> "TaskDTO":
        """Taskエンティティから変換"""
        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
        )
