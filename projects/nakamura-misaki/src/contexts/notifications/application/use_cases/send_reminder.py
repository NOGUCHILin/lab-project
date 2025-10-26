"""Send Reminder Use Case"""

from uuid import UUID

from ...domain.entities.notification import Notification
from ...domain.repositories.notification_repository import NotificationRepository
from ...domain.value_objects.notification_type import NotificationType
from ..dto.notification_dto import NotificationDTO


class SendReminderUseCase:
    """Use case for sending task reminders"""

    def __init__(self, notification_repository: NotificationRepository):
        """Initialize use case

        Args:
            notification_repository: Repository for notifications
        """
        self._notification_repo = notification_repository

    async def execute(
        self, user_id: str, task_id: UUID, message: str
    ) -> NotificationDTO:
        """Send a reminder notification to a user

        Args:
            user_id: User to send reminder to
            task_id: Related task ID
            message: Reminder message content

        Returns:
            NotificationDTO of the created and sent notification

        Raises:
            ValueError: If message is empty
        """
        # Create reminder notification
        notification = Notification.create(
            user_id=user_id,
            notification_type=NotificationType.REMINDER,
            content=message,
            task_id=task_id,
        )

        # Mark as sent immediately (in real system, this would be after actual sending)
        notification = notification.mark_as_sent()

        # Save notification
        saved_notification = await self._notification_repo.save(notification)

        return NotificationDTO.from_entity(saved_notification)
