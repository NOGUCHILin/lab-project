"""Task domain model - Personal Tasks Context"""

from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import UUID, uuid4

from src.shared_kernel.domain.value_objects.task_status import TaskStatus


@dataclass
class Task:
    """Task aggregate root - Personal Tasks Context

    Represents a personal task in the individual todo management system.
    This is the core domain entity for personal task tracking.

    Attributes:
        id: Unique identifier for the task
        title: Task title (required)
        description: Detailed description (optional)
        assignee_user_id: User ID of the person assigned to this task
        creator_user_id: User ID of the person who created this task
        status: Current status of the task (PENDING, IN_PROGRESS, COMPLETED)
        due_at: Due date/time (optional)
        completed_at: When the task was completed (None if not completed)
        created_at: When the task was created
        updated_at: When the task was last updated

    Business Rules:
        - Title cannot be empty
        - Only the creator or assignee can modify the task
        - Status transitions must be valid
        - Completed tasks have a completed_at timestamp
    """

    id: UUID
    title: str
    description: str | None
    assignee_user_id: str
    creator_user_id: str
    status: TaskStatus
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        title: str,
        assignee_user_id: str,
        creator_user_id: str,
        description: str | None = None,
        due_at: datetime | None = None
    ) -> "Task":
        """Factory method to create a new Task

        Args:
            title: Task title (required, cannot be empty)
            assignee_user_id: User ID assigned to this task
            creator_user_id: User ID who created this task
            description: Task description (optional)
            due_at: Due date/time (optional)

        Returns:
            New Task instance with PENDING status

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        # Generate timestamps
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            title=title.strip(),
            description=description,
            assignee_user_id=assignee_user_id,
            creator_user_id=creator_user_id,
            status=TaskStatus.PENDING,
            due_at=due_at,
            completed_at=None,
            created_at=now,
            updated_at=now
        )

    def __eq__(self, other: object) -> bool:
        """Tasks are equal if they have the same ID"""
        if not isinstance(other, Task):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets/dicts"""
        return hash(self.id)
