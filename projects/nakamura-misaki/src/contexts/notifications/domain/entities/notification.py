"""Notification Entity"""

from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects.notification_type import NotificationType


@dataclass(frozen=True)
class Notification:
    """Notification domain entity representing a user notification"""

    id: UUID
    user_id: str | None
    notification_type: NotificationType
    task_id: UUID | None
    content: str
    sent_at: datetime | None
    read_at: datetime | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: str | None,
        notification_type: NotificationType,
        content: str,
        task_id: UUID | None = None,
    ) -> "Notification":
        """Create a new notification

        Args:
            user_id: ID of the user to notify (None for system notifications)
            notification_type: Type of notification
            content: Notification content text
            task_id: Optional task ID related to this notification

        Returns:
            New Notification instance

        Raises:
            ValueError: If content is empty
        """
        if not content or not content.strip():
            raise ValueError("Notification content cannot be empty")

        return cls(
            id=uuid4(),
            user_id=user_id,
            notification_type=notification_type,
            task_id=task_id,
            content=content.strip(),
            sent_at=None,
            read_at=None,
            created_at=datetime.now(),
        )

    def mark_as_sent(self) -> "Notification":
        """Mark notification as sent

        Returns:
            New Notification instance with sent_at timestamp

        Raises:
            ValueError: If notification was already sent
        """
        if self.sent_at is not None:
            raise ValueError("Notification was already sent")

        return replace(self, sent_at=datetime.now())

    def mark_as_read(self) -> "Notification":
        """Mark notification as read

        Returns:
            New Notification instance with read_at timestamp

        Raises:
            ValueError: If notification was not sent yet or already read
        """
        if self.sent_at is None:
            raise ValueError("Cannot mark unsent notification as read")
        if self.read_at is not None:
            raise ValueError("Notification was already read")

        return replace(self, read_at=datetime.now())

    @property
    def is_sent(self) -> bool:
        """Check if notification was sent"""
        return self.sent_at is not None

    @property
    def is_read(self) -> bool:
        """Check if notification was read"""
        return self.read_at is not None

    @property
    def is_unread(self) -> bool:
        """Check if notification is unread (sent but not read)"""
        return self.is_sent and not self.is_read
