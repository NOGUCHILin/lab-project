"""Notification Repository Interface"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.notification import Notification


class NotificationRepository(ABC):
    """Repository interface for notification persistence"""

    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        """Save a notification

        Args:
            notification: Notification entity to save

        Returns:
            Saved notification entity
        """
        pass

    @abstractmethod
    async def find_by_id(self, notification_id: UUID) -> Notification | None:
        """Find notification by ID

        Args:
            notification_id: Notification ID

        Returns:
            Notification if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_user_id(
        self, user_id: str, limit: int = 100
    ) -> list[Notification]:
        """Find all notifications for a user

        Args:
            user_id: User ID
            limit: Maximum number of notifications to return

        Returns:
            List of notifications ordered by created_at DESC
        """
        pass

    @abstractmethod
    async def find_unread_by_user_id(
        self, user_id: str, limit: int = 50
    ) -> list[Notification]:
        """Find unread notifications for a user

        Args:
            user_id: User ID
            limit: Maximum number of notifications to return

        Returns:
            List of unread notifications ordered by created_at DESC
        """
        pass

    @abstractmethod
    async def find_by_task_id(self, task_id: UUID) -> list[Notification]:
        """Find all notifications related to a specific task

        Args:
            task_id: Task ID

        Returns:
            List of notifications ordered by created_at DESC
        """
        pass
