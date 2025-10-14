"""Unit tests for SendHandoffReminderUseCase"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.send_handoff_reminder import SendHandoffReminderUseCase
from src.domain.models.handoff import Handoff


@pytest.fixture
def mock_repository():
    """Create mock handoff repository"""
    repository = AsyncMock()
    return repository


@pytest.fixture
def mock_slack_client():
    """Create mock Slack client"""
    client = AsyncMock()
    return client


@pytest.fixture
def use_case(mock_repository, mock_slack_client):
    """Create use case instance"""
    return SendHandoffReminderUseCase(mock_repository, mock_slack_client)


@pytest.mark.asyncio
async def test_send_reminders(use_case, mock_repository, mock_slack_client):
    """Test send reminders"""
    now = datetime.now()
    handoff = Handoff(
        id=uuid4(),
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=now + timedelta(minutes=5),
    )

    mock_repository.list_pending_reminders.return_value = [handoff]

    sent_count = await use_case.execute()

    assert sent_count == 1
    mock_repository.list_pending_reminders.assert_called_once()
    mock_slack_client.send_dm.assert_called_once_with("user_456", pytest.any(str))
    mock_repository.mark_reminded.assert_called_once_with(handoff.id)


@pytest.mark.asyncio
async def test_no_reminders_needed(use_case, mock_repository, mock_slack_client):
    """Test no reminders needed"""
    mock_repository.list_pending_reminders.return_value = []

    sent_count = await use_case.execute()

    assert sent_count == 0
    mock_slack_client.send_dm.assert_not_called()
    mock_repository.mark_reminded.assert_not_called()


@pytest.mark.asyncio
async def test_reminder_failure_no_mark(use_case, mock_repository, mock_slack_client):
    """Test reminder failure does not mark as reminded"""
    now = datetime.now()
    handoff = Handoff(
        id=uuid4(),
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=now + timedelta(minutes=5),
    )

    mock_repository.list_pending_reminders.return_value = [handoff]
    mock_slack_client.send_dm.side_effect = Exception("Slack API error")

    sent_count = await use_case.execute()

    assert sent_count == 0
    mock_repository.mark_reminded.assert_not_called()
