"""Tests for GetOverdueTasksUseCase"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.contexts.notifications.application.use_cases.get_overdue_tasks import (
    GetOverdueTasksUseCase,
)
from src.contexts.personal_tasks.domain.models.task import Task


@pytest.mark.asyncio
async def test_get_overdue_tasks_success():
    """Test getting overdue tasks for a user"""
    # Arrange
    mock_task_repo = AsyncMock()

    # Create tasks with different deadline statuses
    overdue_task1 = Task.create(
        title="Overdue Task 1",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() - timedelta(days=2),  # 2 days overdue
    )

    overdue_task2 = Task.create(
        title="Overdue Task 2",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() - timedelta(hours=1),  # 1 hour overdue
    )

    future_task = Task.create(
        title="Future Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(days=1),  # Due tomorrow
    )

    completed_task = Task.create(
        title="Completed Overdue Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() - timedelta(days=1),
    )
    completed_task.complete()  # Mark as completed

    mock_task_repo.list_by_user.return_value = [
        overdue_task1,
        overdue_task2,
        future_task,
        completed_task,
    ]

    use_case = GetOverdueTasksUseCase(mock_task_repo)

    # Act
    result = await use_case.execute(user_id="U12345")

    # Assert
    assert len(result) == 2  # Only 2 overdue incomplete tasks
    # Should be sorted by most overdue first (2 days > 1 hour)
    assert result[0].task_id == overdue_task1.id
    assert result[0].days_overdue == 2
    assert result[1].task_id == overdue_task2.id
    assert result[1].days_overdue == 0  # Less than 1 day


@pytest.mark.asyncio
async def test_get_overdue_tasks_with_no_overdue():
    """Test getting overdue tasks when there are none"""
    # Arrange
    mock_task_repo = AsyncMock()

    future_task = Task.create(
        title="Future Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        due_at=datetime.now() + timedelta(days=1),
    )

    mock_task_repo.list_by_user.return_value = [future_task]

    use_case = GetOverdueTasksUseCase(mock_task_repo)

    # Act
    result = await use_case.execute(user_id="U12345")

    # Assert
    assert len(result) == 0
