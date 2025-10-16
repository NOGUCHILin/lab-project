"""Task DTOs - Application layer data transfer objects"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.shared_kernel.domain.value_objects.task_status import TaskStatus

from ...domain.models.task import Task


@dataclass
class CreateTaskDTO:
    """DTO for creating a new task

    Used to transfer task creation data from UI/API to Application layer.

    Attributes:
        title: Task title (required)
        assignee_user_id: User ID assigned to this task
        creator_user_id: User ID who created this task
        description: Task description (optional)
        due_at: Due date/time (optional)
    """

    title: str
    assignee_user_id: str
    creator_user_id: str
    description: str | None = None
    due_at: datetime | None = None


@dataclass
class TaskDTO:
    """DTO for task representation

    Used to transfer task data from Application layer to UI/API.
    This is a read model - no business logic.

    Attributes:
        id: Task unique identifier
        title: Task title
        description: Task description
        assignee_user_id: User ID assigned to this task
        creator_user_id: User ID who created this task
        status: Task status as string
        due_at: Due date/time
        completed_at: Completion timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID
    title: str
    description: str | None
    assignee_user_id: str
    creator_user_id: str
    status: str
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task: Task) -> "TaskDTO":
        """Create DTO from Task domain model

        Args:
            task: Task domain entity

        Returns:
            TaskDTO with data from domain model
        """
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            assignee_user_id=task.assignee_user_id,
            creator_user_id=task.creator_user_id,
            status=task.status.value,  # Convert enum to string
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at
        )


@dataclass
class UpdateTaskDTO:
    """DTO for updating an existing task

    All fields are optional - only provided fields will be updated.

    Attributes:
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        due_at: New due date (optional)
    """

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None
