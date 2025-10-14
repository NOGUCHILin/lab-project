"""Unit tests for RegisterTaskUseCase"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.application.dto.task_dto import CreateTaskDTO
from src.application.use_cases.register_task import RegisterTaskUseCase
from src.domain.models.task import Task, TaskStatus


@pytest.fixture
def mock_repository():
    """Create mock task repository"""
    repository = AsyncMock()
    return repository


@pytest.fixture
def use_case(mock_repository):
    """Create use case instance"""
    return RegisterTaskUseCase(mock_repository)


@pytest.mark.asyncio
async def test_register_task_success(use_case, mock_repository):
    """Test register task success"""
    dto = CreateTaskDTO(
        user_id="user_456",
        title="Test task",
        description="Test description",
        due_at=datetime.now(),
    )

    # Mock repository response
    mock_task = Task(
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.PENDING,
        due_at=dto.due_at,
    )
    mock_repository.create.return_value = mock_task

    result = await use_case.execute(dto)

    assert result.title == "Test task"
    assert result.description == "Test description"
    assert result.status == TaskStatus.PENDING.value
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_task_empty_title(use_case):
    """Test register task with empty title"""
    dto = CreateTaskDTO(
        user_id="user_456",
        title="",
        description="Test description",
    )

    with pytest.raises(ValueError, match="Task title cannot be empty"):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_register_task_without_due_date(use_case, mock_repository):
    """Test register task without due date"""
    dto = CreateTaskDTO(
        user_id="user_456",
        title="Test task",
        description="Test description",
    )

    mock_task = Task(
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.PENDING,
    )
    mock_repository.create.return_value = mock_task

    result = await use_case.execute(dto)

    assert result.title == "Test task"
    assert result.due_at is None
