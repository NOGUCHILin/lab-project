"""Unit tests for RegisterHandoffUseCase"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dto.handoff_dto import CreateHandoffDTO
from src.application.use_cases.register_handoff import RegisterHandoffUseCase
from src.domain.models.handoff import Handoff


@pytest.fixture
def mock_repository():
    """Create mock handoff repository"""
    repository = AsyncMock()
    return repository


@pytest.fixture
def use_case(mock_repository):
    """Create use case instance"""
    return RegisterHandoffUseCase(mock_repository)


@pytest.mark.asyncio
async def test_register_handoff_success(use_case, mock_repository):
    """Test register handoff success"""
    task_id = uuid4()
    handoff_at = datetime.now() + timedelta(hours=2)

    dto = CreateHandoffDTO(
        task_id=task_id,
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=handoff_at,
    )

    # Mock repository response
    mock_handoff = Handoff(
        task_id=task_id,
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=handoff_at,
    )
    mock_repository.create.return_value = mock_handoff

    result = await use_case.execute(dto)

    assert result.task_id == task_id
    assert result.from_user_id == "user_123"
    assert result.to_user_id == "user_456"
    assert result.progress_note == "Task is 50% complete"
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_handoff_past_date_error(use_case):
    """Test register handoff with past date"""
    task_id = uuid4()
    past_date = datetime.now() - timedelta(hours=1)

    dto = CreateHandoffDTO(
        task_id=task_id,
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=past_date,
    )

    with pytest.raises(ValueError, match="Handoff time must be in the future"):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_register_handoff_empty_progress_note(use_case):
    """Test register handoff with empty progress note"""
    task_id = uuid4()
    handoff_at = datetime.now() + timedelta(hours=2)

    dto = CreateHandoffDTO(
        task_id=task_id,
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="",
        handoff_at=handoff_at,
    )

    with pytest.raises(ValueError, match="Progress note cannot be empty"):
        await use_case.execute(dto)
