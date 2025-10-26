"""Tests for SendReminderUseCase"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.notifications.application.use_cases.send_reminder import (
    SendReminderUseCase,
)


@pytest.mark.asyncio
async def test_send_reminder_success():
    """Test sending a reminder notification"""
    # Arrange
    mock_repo = AsyncMock()
    task_id = uuid4()

    # Mock save to return the notification passed to it
    async def mock_save(notification):
        return notification

    mock_repo.save.side_effect = mock_save

    use_case = SendReminderUseCase(mock_repo)

    # Act
    result = await use_case.execute(
        user_id="U12345",
        task_id=task_id,
        message="Your task is due tomorrow",
    )

    # Assert
    assert result.user_id == "U12345"
    assert result.task_id == task_id
    assert result.content == "Your task is due tomorrow"
    assert result.notification_type == "reminder"
    assert result.is_sent
    assert not result.is_read
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_send_reminder_with_empty_message_raises_error():
    """Test that sending reminder with empty message raises ValueError"""
    # Arrange
    mock_repo = AsyncMock()
    use_case = SendReminderUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(
            user_id="U12345",
            task_id=uuid4(),
            message="",
        )

    assert "content cannot be empty" in str(exc_info.value)
