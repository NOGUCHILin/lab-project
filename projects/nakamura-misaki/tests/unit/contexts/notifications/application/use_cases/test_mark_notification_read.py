"""Tests for MarkNotificationReadUseCase"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.notifications.application.use_cases.mark_notification_read import (
    MarkNotificationReadUseCase,
)
from src.contexts.notifications.domain.entities.notification import Notification
from src.contexts.notifications.domain.value_objects.notification_type import (
    NotificationType,
)


@pytest.mark.asyncio
async def test_mark_notification_read_success():
    """Test marking a notification as read"""
    # Arrange
    mock_repo = AsyncMock()
    notification_id = uuid4()

    # Create a sent notification
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    ).mark_as_sent()

    mock_repo.find_by_id.return_value = notification

    # Mock save to return the updated notification
    async def mock_save(notif):
        return notif

    mock_repo.save.side_effect = mock_save

    use_case = MarkNotificationReadUseCase(mock_repo)

    # Act
    result = await use_case.execute(notification_id)

    # Assert
    assert result.is_read
    assert result.read_at is not None
    mock_repo.find_by_id.assert_called_once_with(notification_id)
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_mark_notification_read_not_found_raises_error():
    """Test that marking non-existent notification raises ValueError"""
    # Arrange
    mock_repo = AsyncMock()
    notification_id = uuid4()

    mock_repo.find_by_id.return_value = None

    use_case = MarkNotificationReadUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(notification_id)

    assert "not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_mark_notification_read_not_sent_raises_error():
    """Test that marking unsent notification as read raises ValueError"""
    # Arrange
    mock_repo = AsyncMock()
    notification_id = uuid4()

    # Create an unsent notification
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )

    mock_repo.find_by_id.return_value = notification

    use_case = MarkNotificationReadUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(notification_id)

    assert "unsent notification" in str(exc_info.value)
