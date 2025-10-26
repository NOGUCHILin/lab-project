"""NotificationType Value Object"""

from enum import Enum


class NotificationType(Enum):
    """Notification type enumeration"""

    REMINDER = "reminder"  # Task reminder (due soon)
    OVERDUE = "overdue"  # Task is overdue
    TASK_ASSIGNED = "task_assigned"  # Task was assigned to user
    TASK_COMPLETED = "task_completed"  # Task was completed
    DEADLINE_APPROACHING = "deadline_approaching"  # Deadline is approaching (24h)

    @classmethod
    def from_string(cls, value: str) -> "NotificationType":
        """Convert string to NotificationType enum

        Args:
            value: String value to convert

        Returns:
            NotificationType enum value

        Raises:
            ValueError: If value is not a valid notification type
        """
        try:
            return cls(value)
        except ValueError as e:
            valid_types = ", ".join([t.value for t in cls])
            raise ValueError(
                f"Invalid notification type: {value}. Valid types are: {valid_types}"
            ) from e
