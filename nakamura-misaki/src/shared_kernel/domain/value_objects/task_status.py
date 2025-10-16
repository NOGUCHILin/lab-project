"""TaskStatus value object - Shared across contexts"""

from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration

    Value object representing the lifecycle states of a task.
    Shared across Personal Tasks and Work Tasks contexts.

    States:
        PENDING: Task is created but not started
        IN_PROGRESS: Task is being worked on
        COMPLETED: Task is finished
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    def __str__(self) -> str:
        """Return string representation with enum name"""
        return f"{self.__class__.__name__}.{self.name}"
