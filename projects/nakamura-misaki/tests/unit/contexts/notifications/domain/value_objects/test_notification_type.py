"""Tests for NotificationType Value Object"""

import pytest

from src.contexts.notifications.domain.value_objects.notification_type import (
    NotificationType,
)


def test_notification_type_has_expected_values():
    """Test that NotificationType enum has all expected values"""
    assert NotificationType.REMINDER.value == "reminder"
    assert NotificationType.OVERDUE.value == "overdue"
    assert NotificationType.TASK_ASSIGNED.value == "task_assigned"
    assert NotificationType.TASK_COMPLETED.value == "task_completed"
    assert NotificationType.DEADLINE_APPROACHING.value == "deadline_approaching"


def test_notification_type_from_string_valid():
    """Test from_string() with valid notification type string"""
    notification_type = NotificationType.from_string("reminder")
    assert notification_type == NotificationType.REMINDER

    notification_type = NotificationType.from_string("overdue")
    assert notification_type == NotificationType.OVERDUE


def test_notification_type_from_string_invalid():
    """Test that from_string() raises ValueError for invalid type"""
    with pytest.raises(ValueError) as exc_info:
        NotificationType.from_string("invalid_type")

    assert "Invalid notification type" in str(exc_info.value)
    assert "valid types are" in str(exc_info.value).lower()
