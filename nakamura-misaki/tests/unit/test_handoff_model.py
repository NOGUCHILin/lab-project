"""Unit tests for Handoff domain model"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.models.handoff import Handoff


def test_handoff_creation():
    """ハンドオフ作成テスト"""
    handoff = Handoff(
        from_user_id="user-123",
        to_user_id="user-456",
        progress_note="API実装完了",
        next_steps="テスト実施",
        handoff_at=datetime.now() + timedelta(hours=1),
    )

    assert isinstance(handoff.id, UUID)
    assert handoff.from_user_id == "user-123"
    assert handoff.to_user_id == "user-456"
    assert handoff.progress_note == "API実装完了"
    assert handoff.next_steps == "テスト実施"
    assert isinstance(handoff.created_at, datetime)


def test_handoff_validation():
    """バリデーションテスト"""
    with pytest.raises(ValueError, match="Handoff from_user_id cannot be empty"):
        Handoff(
            from_user_id="",
            to_user_id="user-456",
            progress_note="Test",
            next_steps="Test",
        )

    with pytest.raises(ValueError, match="Handoff to_user_id cannot be empty"):
        Handoff(
            from_user_id="user-123",
            to_user_id="",
            progress_note="Test",
            next_steps="Test",
        )


def test_handoff_is_pending():
    """未完了判定テスト"""
    handoff = Handoff(
        from_user_id="user-123",
        to_user_id="user-456",
        progress_note="Test",
        next_steps="Test",
    )

    assert handoff.is_pending() is True

    handoff.complete()
    assert handoff.is_pending() is False


def test_handoff_is_reminder_needed():
    """リマインダー必要判定テスト"""
    # 1時間後が引き継ぎ予定（リマインダーは10分前）
    handoff = Handoff(
        from_user_id="user-123",
        to_user_id="user-456",
        progress_note="Test",
        next_steps="Test",
        handoff_at=datetime.now() + timedelta(minutes=5),  # 5分後
    )

    # 5分後なのでリマインダー必要（10分前なので）
    current_time = datetime.now()
    assert handoff.is_reminder_needed(current_time) is True

    # リマインダー送信済みにする
    handoff.mark_reminded()
    assert handoff.is_reminder_needed(current_time) is False

    # 完了したらリマインダー不要
    handoff_completed = Handoff(
        from_user_id="user-123",
        to_user_id="user-456",
        progress_note="Test",
        next_steps="Test",
        handoff_at=datetime.now() + timedelta(minutes=5),
    )
    handoff_completed.complete()
    assert handoff_completed.is_reminder_needed(current_time) is False


def test_handoff_to_dict():
    """辞書変換テスト"""
    handoff = Handoff(
        from_user_id="user-123",
        to_user_id="user-456",
        progress_note="Progress",
        next_steps="Next",
    )

    data = handoff.to_dict()

    assert data["from_user_id"] == "user-123"
    assert data["to_user_id"] == "user-456"
    assert data["progress_note"] == "Progress"
    assert data["next_steps"] == "Next"
    assert "id" in data
    assert "created_at" in data
