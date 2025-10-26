"""Notification DTOs"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.entities.notification import Notification
from ...domain.value_objects.notification_type import NotificationType


@dataclass(frozen=True)
class NotificationDTO:
    """Data Transfer Object for Notification"""

    id: UUID
    user_id: str | None
    notification_type: str  # Serialized from enum
    task_id: UUID | None
    content: str
    sent_at: datetime | None
    read_at: datetime | None
    created_at: datetime
    is_sent: bool
    is_read: bool
    is_unread: bool

    @classmethod
    def from_entity(cls, notification: Notification) -> "NotificationDTO":
        """Convert Notification entity to DTO

        Args:
            notification: Notification entity

        Returns:
            NotificationDTO
        """
        return cls(
            id=notification.id,
            user_id=notification.user_id,
            notification_type=notification.notification_type.value,
            task_id=notification.task_id,
            content=notification.content,
            sent_at=notification.sent_at,
            read_at=notification.read_at,
            created_at=notification.created_at,
            is_sent=notification.is_sent,
            is_read=notification.is_read,
            is_unread=notification.is_unread,
        )


@dataclass(frozen=True)
class OverdueTaskDTO:
    """Data Transfer Object for Overdue Task information"""

    task_id: UUID
    title: str
    user_id: str
    deadline: datetime
    days_overdue: int


@dataclass(frozen=True)
class DueSoonTaskDTO:
    """Data Transfer Object for Due Soon Task information"""

    task_id: UUID
    title: str
    user_id: str
    deadline: datetime
    hours_until_due: float
