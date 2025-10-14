"""Unit tests for TaskCommandParser"""

from datetime import datetime

import pytest

from src.adapters.primary.task_command_parser import TaskCommandParser


@pytest.fixture
def parser():
    """Create parser instance"""
    return TaskCommandParser()


def test_parse_register_task_with_title(parser):
    """Test parse register task with title"""
    result = parser.parse("「API統合」をやる", "user_456")

    assert result is not None
    assert result.command_type == "register"
    assert result.user_id == "user_456"
    assert result.title == "API統合"


def test_parse_register_task_with_due_date_today(parser):
    """Test parse register task with due date (today)"""
    result = parser.parse("「データベース移行」を今日やる", "user_456")

    assert result is not None
    assert result.command_type == "register"
    assert result.title == "データベース移行"
    assert result.due_at is not None
    assert result.due_at.date() == datetime.now().date()


def test_parse_register_task_with_due_date_tomorrow(parser):
    """Test parse register task with due date (tomorrow)"""
    result = parser.parse("「コードレビュー」を明日やる", "user_456")

    assert result is not None
    assert result.command_type == "register"
    assert result.title == "コードレビュー"
    assert result.due_at is not None


def test_parse_register_task_with_days_offset(parser):
    """Test parse register task with days offset"""
    result = parser.parse("「プレゼン準備」を3日後にやる", "user_456")

    assert result is not None
    assert result.command_type == "register"
    assert result.title == "プレゼン準備"
    assert result.due_at is not None


def test_parse_list_tasks(parser):
    """Test parse list tasks"""
    result = parser.parse("タスク一覧", "user_456")

    assert result is not None
    assert result.command_type == "list"
    assert result.user_id == "user_456"
    assert result.status is None


def test_parse_list_tasks_with_status_filter(parser):
    """Test parse list tasks with status filter"""
    result = parser.parse("進行中のタスクを見せて", "user_456")

    assert result is not None
    assert result.command_type == "list"
    assert result.status == "in_progress"


def test_parse_complete_task(parser):
    """Test parse complete task"""
    task_id = "12345678-1234-1234-1234-123456789abc"
    result = parser.parse(f"タスク {task_id} 完了", "user_456")

    assert result is not None
    assert result.command_type == "complete"
    assert result.user_id == "user_456"
    assert result.task_id is not None
    assert str(result.task_id) == task_id


def test_parse_non_task_command(parser):
    """Test parse non-task command"""
    result = parser.parse("天気はどう？", "user_456")

    assert result is None
