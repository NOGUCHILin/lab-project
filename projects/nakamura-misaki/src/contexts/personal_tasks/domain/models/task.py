"""Task domain model - Personal Tasks Context"""

from dataclasses import dataclass
from datetime import UTC, datetime
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
        priority: Task priority (1-10, default 5, lower=higher priority)
        progress_percent: Task progress percentage (0-100, default 0)
        estimated_hours: Estimated hours to complete (optional)
        completed_at: When the task was completed (None if not completed)
        created_at: When the task was created
        updated_at: When the task was last updated

    Business Rules:
        - Title cannot be empty
        - Only the creator or assignee can modify the task
        - Status transitions must be valid
        - Completed tasks have a completed_at timestamp
        - Priority must be between 1 and 10
        - Progress must be between 0 and 100
    """

    id: UUID
    title: str
    description: str | None
    assignee_user_id: str
    creator_user_id: str
    status: TaskStatus
    due_at: datetime | None
    priority: int  # Phase 4: 1-10 (lower=higher priority)
    progress_percent: int  # Phase 4: 0-100
    estimated_hours: float | None  # Phase 4: Estimated hours
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
        due_at: datetime | None = None,
        priority: int = 5,
        estimated_hours: float | None = None
    ) -> "Task":
        """Factory method to create a new Task

        Args:
            title: Task title (required, cannot be empty)
            assignee_user_id: User ID assigned to this task
            creator_user_id: User ID who created this task
            description: Task description (optional)
            due_at: Due date/time (optional)
            priority: Task priority 1-10 (optional, default 5)
            estimated_hours: Estimated hours to complete (optional)

        Returns:
            New Task instance with PENDING status

        Raises:
            ValueError: If title is empty or whitespace-only, or priority out of range
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        # Validate priority
        if not 1 <= priority <= 10:
            raise ValueError("Task priority must be between 1 and 10")

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
            priority=priority,
            progress_percent=0,
            estimated_hours=estimated_hours,
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

    def complete(self) -> None:
        """Mark task as completed

        Sets status to COMPLETED and records completion timestamp.

        Raises:
            ValueError: If task is already completed
        """
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Task is already completed")

        now = datetime.now(UTC)
        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
        due_at: datetime | None = None,
        priority: int | None = None,
        estimated_hours: float | None = None
    ) -> None:
        """Update task fields

        Args:
            title: New title (optional, cannot be empty if provided)
            description: New description (optional)
            status: New status (optional)
            due_at: New due date (optional)
            priority: New priority (optional, 1-10)
            estimated_hours: New estimated hours (optional)

        Raises:
            ValueError: If title is provided but empty or priority out of range
        """
        # Validate title if provided
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Task title cannot be empty")
            self.title = title.strip()

        # Validate priority if provided
        if priority is not None:
            if not 1 <= priority <= 10:
                raise ValueError("Task priority must be between 1 and 10")
            self.priority = priority

        # Update other fields if provided
        if description is not None:
            self.description = description

        if status is not None:
            self.status = status

        if due_at is not None:
            self.due_at = due_at

        if estimated_hours is not None:
            self.estimated_hours = estimated_hours

        # Always update the timestamp
        self.updated_at = datetime.now(UTC)

    def update_progress(self, progress_percent: int) -> None:
        """Update task progress percentage

        Args:
            progress_percent: Progress percentage (0-100)

        Raises:
            ValueError: If progress is not between 0 and 100
        """
        if not 0 <= progress_percent <= 100:
            raise ValueError("Progress percent must be between 0 and 100")

        self.progress_percent = progress_percent
        self.updated_at = datetime.now(UTC)

    def is_overdue(self) -> bool:
        """Check if task is overdue

        A task is overdue if:
        - It has a due_at date
        - The due_at date is in the past
        - The task is not completed

        Returns:
            True if task is overdue, False otherwise
        """
        if self.due_at is None:
            return False

        if self.status == TaskStatus.COMPLETED:
            return False

        return datetime.now(UTC) > self.due_at
