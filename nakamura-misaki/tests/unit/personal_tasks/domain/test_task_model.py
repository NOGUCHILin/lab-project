"""Unit tests for Task domain model - Part 1: Basic structure"""

from datetime import datetime, timedelta, UTC
from uuid import UUID

import pytest

from src.contexts.personal_tasks.domain.models.task import Task
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class TestTaskCreation:
    """Test suite for Task.create() factory method"""

    def test_create_task_with_minimum_fields(self):
        """Test creating task with only required fields"""
        task = Task.create(
            title="Complete Phase 1",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        assert task.title == "Complete Phase 1"
        assert task.assignee_user_id == "U12345"
        assert task.creator_user_id == "U12345"
        assert task.status == TaskStatus.PENDING
        assert task.description is None
        assert task.due_at is None
        assert task.completed_at is None
        assert isinstance(task.id, UUID)
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_with_all_fields(self):
        """Test creating task with all optional fields"""
        due_date = datetime.now(UTC) + timedelta(days=1)
        task = Task.create(
            title="Complete Phase 1",
            assignee_user_id="U12345",
            creator_user_id="U67890",
            description="Implement Bounded Context structure",
            due_at=due_date
        )

        assert task.title == "Complete Phase 1"
        assert task.description == "Implement Bounded Context structure"
        assert task.assignee_user_id == "U12345"
        assert task.creator_user_id == "U67890"
        assert task.due_at == due_date
        assert task.status == TaskStatus.PENDING

    def test_create_task_with_empty_title_raises_error(self):
        """Test that empty title raises ValueError"""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(
                title="",
                assignee_user_id="U12345",
                creator_user_id="U12345"
            )

    def test_create_task_with_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError"""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(
                title="   ",
                assignee_user_id="U12345",
                creator_user_id="U12345"
            )

    def test_create_task_strips_whitespace_from_title(self):
        """Test that leading/trailing whitespace is stripped from title"""
        task = Task.create(
            title="  Complete Phase 1  ",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        assert task.title == "Complete Phase 1"


class TestTaskEquality:
    """Test suite for Task equality"""

    def test_task_equality_by_id(self):
        """Test that tasks with same ID are equal"""
        task1 = Task.create("Task 1", "U123", "U123")
        # Create another task with same ID (simulating repository load)
        task2 = Task(
            id=task1.id,
            title="Task 1 Modified",
            description=None,
            assignee_user_id="U123",
            creator_user_id="U123",
            status=TaskStatus.COMPLETED,
            due_at=None,
            completed_at=None,
            created_at=task1.created_at,
            updated_at=task1.updated_at
        )

        assert task1 == task2  # Same ID = equal

    def test_task_inequality_by_id(self):
        """Test that tasks with different IDs are not equal"""
        task1 = Task.create("Task 1", "U123", "U123")
        task2 = Task.create("Task 2", "U123", "U123")

        assert task1 != task2


class TestTaskComplete:
    """Test suite for Task.complete() method"""

    def test_complete_task_success(self):
        """Test completing a pending task"""
        task = Task.create("Task 1", "U123", "U123")
        original_updated_at = task.updated_at

        task.complete()

        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)
        assert task.updated_at > original_updated_at

    def test_complete_already_completed_task_raises_error(self):
        """Test that completing an already completed task raises ValueError"""
        task = Task.create("Task 1", "U123", "U123")
        task.complete()

        with pytest.raises(ValueError, match="Task is already completed"):
            task.complete()

    def test_complete_sets_correct_timestamps(self):
        """Test that complete() sets completed_at and updates updated_at"""
        task = Task.create("Task 1", "U123", "U123")
        before_complete = datetime.now(UTC)

        task.complete()

        assert task.completed_at >= before_complete
        assert task.updated_at >= before_complete
        assert task.completed_at == task.updated_at  # Should be set at the same time


class TestTaskUpdate:
    """Test suite for Task.update() method"""

    def test_update_task_title(self):
        """Test updating task title"""
        task = Task.create("Original Title", "U123", "U123")
        original_updated_at = task.updated_at

        task.update(title="Updated Title")

        assert task.title == "Updated Title"
        assert task.updated_at > original_updated_at

    def test_update_task_description(self):
        """Test updating task description"""
        task = Task.create("Task 1", "U123", "U123")

        task.update(description="New description")

        assert task.description == "New description"

    def test_update_task_status(self):
        """Test updating task status"""
        task = Task.create("Task 1", "U123", "U123")

        task.update(status=TaskStatus.IN_PROGRESS)

        assert task.status == TaskStatus.IN_PROGRESS

    def test_update_task_due_date(self):
        """Test updating task due date"""
        task = Task.create("Task 1", "U123", "U123")
        new_due_date = datetime.now(UTC) + timedelta(days=2)

        task.update(due_at=new_due_date)

        assert task.due_at == new_due_date

    def test_update_task_multiple_fields(self):
        """Test updating multiple fields at once"""
        task = Task.create("Task 1", "U123", "U123")
        new_due_date = datetime.now(UTC) + timedelta(days=3)

        task.update(
            title="Updated Task",
            description="Updated description",
            status=TaskStatus.IN_PROGRESS,
            due_at=new_due_date
        )

        assert task.title == "Updated Task"
        assert task.description == "Updated description"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.due_at == new_due_date

    def test_update_with_empty_title_raises_error(self):
        """Test that updating to empty title raises ValueError"""
        task = Task.create("Task 1", "U123", "U123")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task.update(title="")

    def test_update_with_no_changes_still_updates_timestamp(self):
        """Test that update() with no changes still updates updated_at"""
        task = Task.create("Task 1", "U123", "U123")
        original_updated_at = task.updated_at

        task.update()

        assert task.updated_at > original_updated_at

    def test_update_strips_whitespace_from_title(self):
        """Test that update() strips whitespace from title"""
        task = Task.create("Task 1", "U123", "U123")

        task.update(title="  Updated Title  ")

        assert task.title == "Updated Title"


class TestTaskIsOverdue:
    """Test suite for Task.is_overdue() method"""

    def test_task_without_due_date_is_not_overdue(self):
        """Test that task with no due_at is not overdue"""
        task = Task.create("Task 1", "U123", "U123")

        assert task.is_overdue() is False

    def test_task_with_future_due_date_is_not_overdue(self):
        """Test that task with future due_at is not overdue"""
        future_date = datetime.now(UTC) + timedelta(days=1)
        task = Task.create("Task 1", "U123", "U123", due_at=future_date)

        assert task.is_overdue() is False

    def test_task_with_past_due_date_is_overdue(self):
        """Test that task with past due_at is overdue"""
        past_date = datetime.now(UTC) - timedelta(days=1)
        task = Task.create("Task 1", "U123", "U123", due_at=past_date)

        assert task.is_overdue() is True

    def test_completed_task_is_not_overdue(self):
        """Test that completed task is never overdue"""
        past_date = datetime.now(UTC) - timedelta(days=1)
        task = Task.create("Task 1", "U123", "U123", due_at=past_date)
        task.complete()

        assert task.is_overdue() is False
