"""Mark Notification Read Use Case"""

from uuid import UUID

from ...domain.repositories.notification_repository import NotificationRepository
from ..dto.notification_dto import NotificationDTO


class MarkNotificationReadUseCase:
    """Use case for marking a notification as read"""

    def __init__(self, notification_repository: NotificationRepository):
        """Initialize use case

        Args:
            notification_repository: Repository for notifications
        """
        self._notification_repo = notification_repository

    async def execute(self, notification_id: UUID) -> NotificationDTO:
        """Mark a notification as read

        Args:
            notification_id: ID of notification to mark as read

        Returns:
            NotificationDTO of the updated notification

        Raises:
            ValueError: If notification not found or cannot be marked as read
        """
        # Find notification
        notification = await self._notification_repo.find_by_id(notification_id)

        if notification is None:
            raise ValueError(f"Notification {notification_id} not found")

        # Mark as read
        read_notification = notification.mark_as_read()

        # Save updated notification
        saved_notification = await self._notification_repo.save(read_notification)

        return NotificationDTO.from_entity(saved_notification)
