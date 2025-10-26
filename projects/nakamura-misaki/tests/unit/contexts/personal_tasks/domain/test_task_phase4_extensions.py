"""Tests for Task Entity Phase 4 Extensions (priority, progress, estimated_hours)"""

import pytest

from src.contexts.personal_tasks.domain.models.task import Task


def test_create_task_with_default_priority():
    """Test creating task with default priority (5)"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    assert task.priority == 5
    assert task.progress_percent == 0
    assert task.estimated_hours is None


def test_create_task_with_custom_priority():
    """Test creating task with custom priority"""
    task = Task.create(
        title="High Priority Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        priority=1,  # Highest priority
    )

    assert task.priority == 1


def test_create_task_with_estimated_hours():
    """Test creating task with estimated hours"""
    task = Task.create(
        title="Complex Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        estimated_hours=8.5,
    )

    assert task.estimated_hours == 8.5


def test_create_task_with_invalid_priority_too_low_raises_error():
    """Test that priority < 1 raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        Task.create(
            title="Test Task",
            assignee_user_id="U12345",
            creator_user_id="U67890",
            priority=0,
        )

    assert "priority must be between 1 and 10" in str(exc_info.value)


def test_create_task_with_invalid_priority_too_high_raises_error():
    """Test that priority > 10 raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        Task.create(
            title="Test Task",
            assignee_user_id="U12345",
            creator_user_id="U67890",
            priority=11,
        )

    assert "priority must be between 1 and 10" in str(exc_info.value)


def test_update_task_priority():
    """Test updating task priority"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
        priority=5,
    )

    task.update(priority=2)

    assert task.priority == 2


def test_update_task_priority_invalid_raises_error():
    """Test that updating with invalid priority raises ValueError"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    with pytest.raises(ValueError) as exc_info:
        task.update(priority=15)

    assert "priority must be between 1 and 10" in str(exc_info.value)


def test_update_task_estimated_hours():
    """Test updating task estimated hours"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    task.update(estimated_hours=5.5)

    assert task.estimated_hours == 5.5


def test_update_progress_valid():
    """Test updating task progress with valid percentage"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    assert task.progress_percent == 0

    task.update_progress(25)
    assert task.progress_percent == 25

    task.update_progress(100)
    assert task.progress_percent == 100


def test_update_progress_invalid_too_low_raises_error():
    """Test that progress < 0 raises ValueError"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    with pytest.raises(ValueError) as exc_info:
        task.update_progress(-1)

    assert "must be between 0 and 100" in str(exc_info.value)


def test_update_progress_invalid_too_high_raises_error():
    """Test that progress > 100 raises ValueError"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    with pytest.raises(ValueError) as exc_info:
        task.update_progress(101)

    assert "must be between 0 and 100" in str(exc_info.value)


def test_update_progress_updates_timestamp():
    """Test that update_progress updates the updated_at timestamp"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U12345",
        creator_user_id="U67890",
    )

    original_updated_at = task.updated_at

    # Small delay to ensure timestamp difference
    import time
    time.sleep(0.01)

    task.update_progress(50)

    assert task.updated_at > original_updated_at
