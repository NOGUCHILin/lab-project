"""Unit tests for HandoffCommandParser"""

from datetime import datetime
from uuid import uuid4

import pytest

from src.adapters.primary.handoff_command_parser import HandoffCommandParser


@pytest.fixture
def parser():
    """Create parser instance"""
    return HandoffCommandParser()


def test_parse_register_handoff(parser):
    """Test parse register handoff"""
    task_id = uuid4()
    result = parser.parse(
        f"「API統合」を @U01ABC123 に {task_id} 明日9時から引き継ぎ", "user_456"
    )

    assert result is not None
    assert result.command_type == "register"
    assert result.user_id == "user_456"
    assert result.task_id == task_id
    assert result.to_user_id == "U01ABC123"
    assert result.progress_note == "API統合"
    assert result.handoff_at is not None


def test_parse_register_handoff_with_hours_offset(parser):
    """Test parse register handoff with hours offset"""
    task_id = uuid4()
    result = parser.parse(f"{task_id} を @U01ABC123 に 3時間後に引き継ぎ", "user_456")

    assert result is not None
    assert result.command_type == "register"
    assert result.task_id == task_id
    assert result.to_user_id == "U01ABC123"
    assert result.handoff_at is not None


def test_parse_list_handoffs(parser):
    """Test parse list handoffs"""
    result = parser.parse("引き継ぎ一覧", "user_456")

    assert result is not None
    assert result.command_type == "list"
    assert result.user_id == "user_456"


def test_parse_complete_handoff(parser):
    """Test parse complete handoff"""
    handoff_id = uuid4()
    result = parser.parse(f"ハンドオフ {handoff_id} 完了", "user_456")

    assert result is not None
    assert result.command_type == "complete"
    assert result.user_id == "user_456"
    assert result.handoff_id == handoff_id


def test_parse_non_handoff_command(parser):
    """Test parse non-handoff command"""
    result = parser.parse("今日のタスクは？", "user_456")

    assert result is None
