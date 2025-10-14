"""Unit tests for Task domain model"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.models.task import Task, TaskStatus


def test_task_creation():
    """タスク作成テスト"""
    task = Task(
        title="API統合",
        description="REST API実装",
        assignee_user_id="user-123",
        creator_user_id="user-456",
    )

    assert isinstance(task.id, UUID)
    assert task.title == "API統合"
    assert task.description == "REST API実装"
    assert task.status == TaskStatus.PENDING
    assert isinstance(task.created_at, datetime)


def test_task_validation_empty_title():
    """空のタイトルでバリデーションエラー"""
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        Task(
            title="",
            assignee_user_id="user-123",
            creator_user_id="user-456",
        )


def test_task_validation_long_title():
    """長すぎるタイトルでバリデーションエラー"""
    with pytest.raises(ValueError, match="Task title must be 200 characters or less"):
        Task(
            title="a" * 201,
            assignee_user_id="user-123",
            creator_user_id="user-456",
        )


def test_task_complete():
    """タスク完了テスト"""
    task = Task(
        title="Test",
        assignee_user_id="user-123",
        creator_user_id="user-456",
    )

    task.complete()

    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None
    assert isinstance(task.completed_at, datetime)


def test_task_cancel():
    """タスクキャンセルテスト"""
    task = Task(
        title="Test",
        assignee_user_id="user-123",
        creator_user_id="user-456",
    )

    task.cancel()

    assert task.status == TaskStatus.CANCELLED


def test_task_is_overdue():
    """期限切れ判定テスト"""
    # 昨日が期限
    task_overdue = Task(
        title="Test",
        assignee_user_id="user-123",
        creator_user_id="user-456",
        due_at=datetime.now() - timedelta(days=1),
    )
    assert task_overdue.is_overdue() is True

    # 明日が期限
    task_not_overdue = Task(
        title="Test",
        assignee_user_id="user-123",
        creator_user_id="user-456",
        due_at=datetime.now() + timedelta(days=1),
    )
    assert task_not_overdue.is_overdue() is False

    # 期限なし
    task_no_due = Task(
        title="Test",
        assignee_user_id="user-123",
        creator_user_id="user-456",
    )
    assert task_no_due.is_overdue() is False


def test_task_to_dict():
    """辞書変換テスト"""
    task = Task(
        title="Test Task",
        assignee_user_id="user-123",
        creator_user_id="user-456",
    )

    data = task.to_dict()

    assert data["title"] == "Test Task"
    assert data["assignee_user_id"] == "user-123"
    assert data["creator_user_id"] == "user-456"
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data
