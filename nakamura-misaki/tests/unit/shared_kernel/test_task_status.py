"""Unit tests for TaskStatus value object"""

import pytest

from src.shared_kernel.domain.value_objects.task_status import TaskStatus


class TestTaskStatus:
    """Test suite for TaskStatus value object"""

    def test_task_status_values(self):
        """Test that TaskStatus has the correct values"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"

    def test_task_status_from_string(self):
        """Test creating TaskStatus from string value"""
        assert TaskStatus("pending") == TaskStatus.PENDING
        assert TaskStatus("in_progress") == TaskStatus.IN_PROGRESS
        assert TaskStatus("completed") == TaskStatus.COMPLETED

    def test_task_status_invalid_value(self):
        """Test that invalid status raises ValueError"""
        with pytest.raises(ValueError):
            TaskStatus("invalid_status")

    def test_task_status_equality(self):
        """Test TaskStatus equality comparison"""
        status1 = TaskStatus.PENDING
        status2 = TaskStatus.PENDING
        status3 = TaskStatus.COMPLETED

        assert status1 == status2
        assert status1 != status3

    def test_task_status_string_representation(self):
        """Test TaskStatus string representation"""
        assert str(TaskStatus.PENDING) == "TaskStatus.PENDING"
        assert repr(TaskStatus.PENDING) == "<TaskStatus.PENDING: 'pending'>"
