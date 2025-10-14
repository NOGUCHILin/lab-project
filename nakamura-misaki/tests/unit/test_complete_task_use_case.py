"""Unit tests for CompleteTaskUseCase"""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.complete_task import CompleteTaskUseCase
from src.domain.models.task import Task, TaskStatus


@pytest.fixture
def mock_repository():
    """Create mock task repository"""
    repository = AsyncMock()
    return repository


@pytest.fixture
def use_case(mock_repository):
    """Create use case instance"""
    return CompleteTaskUseCase(mock_repository)


@pytest.mark.asyncio
async def test_complete_task_success(use_case, mock_repository):
    """Test complete task success"""
    task_id = uuid4()
    mock_task = Task(
        id=task_id,
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.PENDING,
    )

    mock_repository.get.return_value = mock_task
    mock_repository.update.return_value = mock_task

    result = await use_case.execute(task_id)

    assert result.status == TaskStatus.COMPLETED.value
    assert mock_task.completed_at is not None
    mock_repository.get.assert_called_once_with(task_id)
    mock_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_complete_nonexistent_task(use_case, mock_repository):
    """Test complete nonexistent task"""
    task_id = uuid4()
    mock_repository.get.return_value = None

    with pytest.raises(ValueError, match="Task not found"):
        await use_case.execute(task_id)


@pytest.mark.asyncio
async def test_complete_already_completed_task(use_case, mock_repository):
    """Test complete already completed task"""
    task_id = uuid4()
    mock_task = Task(
        id=task_id,
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.COMPLETED,
        completed_at=datetime.now(),
    )

    mock_repository.get.return_value = mock_task
    mock_repository.update.return_value = mock_task

    result = await use_case.execute(task_id)

    # Should still work (idempotent)
    assert result.status == TaskStatus.COMPLETED.value
