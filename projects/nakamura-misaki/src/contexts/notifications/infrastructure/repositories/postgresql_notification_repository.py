"""PostgreSQL Notification Repository Implementation"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import NotificationTable

from ...domain.entities.notification import Notification
from ...domain.repositories.notification_repository import NotificationRepository
from ...domain.value_objects.notification_type import NotificationType


class PostgreSQLNotificationRepository(NotificationRepository):
    """PostgreSQL implementation of NotificationRepository"""

    def __init__(self, session: AsyncSession):
        """Initialize repository

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, notification: Notification) -> Notification:
        """Save a notification

        Args:
            notification: Notification entity to save

        Returns:
            Saved notification entity
        """
        # Check if notification exists
        existing = await self._session.get(NotificationTable, notification.id)

        if existing:
            # Update existing
            existing.user_id = notification.user_id
            existing.notification_type = notification.notification_type.value
            existing.task_id = notification.task_id
            existing.content = notification.content
            existing.sent_at = notification.sent_at
            existing.read_at = notification.read_at
        else:
            # Insert new
            table_row = NotificationTable(
                id=notification.id,
                user_id=notification.user_id,
                notification_type=notification.notification_type.value,
                task_id=notification.task_id,
                content=notification.content,
                sent_at=notification.sent_at,
                read_at=notification.read_at,
                created_at=notification.created_at,
            )
            self._session.add(table_row)

        await self._session.flush()
        return notification

    async def find_by_id(self, notification_id: UUID) -> Notification | None:
        """Find notification by ID

        Args:
            notification_id: Notification ID

        Returns:
            Notification if found, None otherwise
        """
        table_row = await self._session.get(NotificationTable, notification_id)

        if table_row is None:
            return None

        return self._to_entity(table_row)

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
        stmt = (
            select(NotificationTable)
            .where(NotificationTable.user_id == user_id)
            .order_by(NotificationTable.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        table_rows = result.scalars().all()

        return [self._to_entity(row) for row in table_rows]

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
        stmt = (
            select(NotificationTable)
            .where(
                NotificationTable.user_id == user_id,
                NotificationTable.sent_at.isnot(None),
                NotificationTable.read_at.is_(None),
            )
            .order_by(NotificationTable.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        table_rows = result.scalars().all()

        return [self._to_entity(row) for row in table_rows]

    async def find_by_task_id(self, task_id: UUID) -> list[Notification]:
        """Find all notifications related to a specific task

        Args:
            task_id: Task ID

        Returns:
            List of notifications ordered by created_at DESC
        """
        stmt = (
            select(NotificationTable)
            .where(NotificationTable.task_id == task_id)
            .order_by(NotificationTable.created_at.desc())
        )

        result = await self._session.execute(stmt)
        table_rows = result.scalars().all()

        return [self._to_entity(row) for row in table_rows]

    def _to_entity(self, table_row: NotificationTable) -> Notification:
        """Convert table row to domain entity

        Args:
            table_row: NotificationTable row

        Returns:
            Notification domain entity
        """
        return Notification(
            id=table_row.id,
            user_id=table_row.user_id,
            notification_type=NotificationType.from_string(table_row.notification_type),
            task_id=table_row.task_id,
            content=table_row.content,
            sent_at=table_row.sent_at,
            read_at=table_row.read_at,
            created_at=table_row.created_at,
        )
