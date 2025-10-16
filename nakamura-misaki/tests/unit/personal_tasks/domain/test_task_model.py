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
