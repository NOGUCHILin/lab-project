"""Tests for Notification Entity"""

from uuid import uuid4

import pytest

from src.contexts.notifications.domain.entities.notification import Notification
from src.contexts.notifications.domain.value_objects.notification_type import (
    NotificationType,
)


def test_create_notification_with_valid_data():
    """Test creating a notification with valid data"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder: Complete project proposal",
        task_id=uuid4(),
    )

    assert notification.user_id == "U12345"
    assert notification.notification_type == NotificationType.REMINDER
    assert notification.content == "Task reminder: Complete project proposal"
    assert notification.task_id is not None
    assert notification.id is not None
    assert notification.created_at is not None
    assert notification.sent_at is None
    assert notification.read_at is None


def test_create_notification_without_task_id():
    """Test creating a notification without task_id"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.TASK_ASSIGNED,
        content="New task assigned to you",
    )

    assert notification.task_id is None
    assert notification.content == "New task assigned to you"


def test_create_notification_with_empty_content_raises_error():
    """Test that creating notification with empty content raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        Notification.create(
            user_id="U12345",
            notification_type=NotificationType.REMINDER,
            content="",
        )

    assert "content cannot be empty" in str(exc_info.value)


def test_mark_as_sent_success():
    """Test marking notification as sent"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )

    assert not notification.is_sent

    sent_notification = notification.mark_as_sent()

    assert sent_notification.is_sent
    assert sent_notification.sent_at is not None
    assert not sent_notification.is_read


def test_mark_as_sent_when_already_sent_raises_error():
    """Test that marking already sent notification raises ValueError"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )
    sent_notification = notification.mark_as_sent()

    with pytest.raises(ValueError) as exc_info:
        sent_notification.mark_as_sent()

    assert "already sent" in str(exc_info.value)


def test_mark_as_read_success():
    """Test marking notification as read"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )
    sent_notification = notification.mark_as_sent()

    assert sent_notification.is_unread

    read_notification = sent_notification.mark_as_read()

    assert read_notification.is_read
    assert read_notification.read_at is not None
    assert not read_notification.is_unread


def test_mark_as_read_when_not_sent_raises_error():
    """Test that marking unsent notification as read raises ValueError"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )

    with pytest.raises(ValueError) as exc_info:
        notification.mark_as_read()

    assert "unsent notification" in str(exc_info.value)


def test_mark_as_read_when_already_read_raises_error():
    """Test that marking already read notification raises ValueError"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )
    sent_notification = notification.mark_as_sent()
    read_notification = sent_notification.mark_as_read()

    with pytest.raises(ValueError) as exc_info:
        read_notification.mark_as_read()

    assert "already read" in str(exc_info.value)


def test_is_sent_property():
    """Test is_sent property"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )

    assert not notification.is_sent

    sent_notification = notification.mark_as_sent()
    assert sent_notification.is_sent


def test_is_read_property():
    """Test is_read property"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )
    sent_notification = notification.mark_as_sent()

    assert not sent_notification.is_read

    read_notification = sent_notification.mark_as_read()
    assert read_notification.is_read


def test_is_unread_property():
    """Test is_unread property"""
    notification = Notification.create(
        user_id="U12345",
        notification_type=NotificationType.REMINDER,
        content="Task reminder",
    )

    # Not sent → not unread
    assert not notification.is_unread

    sent_notification = notification.mark_as_sent()
    # Sent but not read → unread
    assert sent_notification.is_unread

    read_notification = sent_notification.mark_as_read()
    # Read → not unread
    assert not read_notification.is_unread
