"""Tests for GetDueSoonTasksUseCase"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.contexts.notifications.application.use_cases.get_due_soon_tasks import (
    GetDueSoonTasksUseCase,
)
from src.contexts.personal_tasks.domain.models.task import Task


@pytest.mark.asyncio
async def test_get_due_soon_tasks_within_24_hours():
    """Test getting tasks due within 24 hours"""
    # Arrange
    mock_task_repo = AsyncMock()

    # Create tasks with different deadline statuses
    due_in_2_hours = Task.create(
        title="Due Soon Task 1",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(hours=2),
    )

    due_in_20_hours = Task.create(
        title="Due Soon Task 2",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(hours=20),
    )

    due_in_48_hours = Task.create(
        title="Future Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(hours=48),  # Outside 24h window
    )

    completed_task = Task.create(
        title="Completed Due Soon Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(hours=5),
    )
    completed_task.complete()

    mock_task_repo.list_by_user.return_value = [
        due_in_2_hours,
        due_in_20_hours,
        due_in_48_hours,
        completed_task,
    ]

    use_case = GetDueSoonTasksUseCase(mock_task_repo)

    # Act
    result = await use_case.execute(user_id="U12345", hours=24)

    # Assert
    assert len(result) == 2  # Only 2 tasks due within 24 hours
    # Should be sorted by soonest first
    assert result[0].task_id == due_in_2_hours.id
    assert result[0].hours_until_due < 3
    assert result[1].task_id == due_in_20_hours.id


@pytest.mark.asyncio
async def test_get_due_soon_tasks_custom_hours():
    """Test getting tasks due within custom hours"""
    # Arrange
    mock_task_repo = AsyncMock()

    due_in_2_hours = Task.create(
        title="Due Soon Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(hours=2),
    )

    due_in_10_hours = Task.create(
        title="Future Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(hours=10),
    )

    mock_task_repo.list_by_user.return_value = [due_in_2_hours, due_in_10_hours]

    use_case = GetDueSoonTasksUseCase(mock_task_repo)

    # Act
    result = await use_case.execute(user_id="U12345", hours=5)

    # Assert
    assert len(result) == 1  # Only 1 task due within 5 hours
    assert result[0].task_id == due_in_2_hours.id


@pytest.mark.asyncio
async def test_get_due_soon_tasks_invalid_hours_raises_error():
    """Test that invalid hours parameter raises ValueError"""
    # Arrange
    mock_task_repo = AsyncMock()
    use_case = GetDueSoonTasksUseCase(mock_task_repo)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(user_id="U12345", hours=0)

    assert "hours must be positive" in str(exc_info.value)
