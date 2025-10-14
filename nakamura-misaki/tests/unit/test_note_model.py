"""Unit tests for Note domain model"""

import pytest
from datetime import datetime
from uuid import UUID

from src.domain.models.note import Note


def test_note_creation():
    """ノート作成テスト"""
    note = Note.create(
        session_id="session-123",
        user_id="user-456",
        content="Test note content",
        category="decisions",
    )

    assert isinstance(note.id, UUID)
    assert note.session_id == "session-123"
    assert note.user_id == "user-456"
    assert note.content == "Test note content"
    assert note.category == "decisions"
    assert isinstance(note.created_at, datetime)


def test_note_validation_empty_content():
    """空のコンテンツでバリデーションエラー"""
    with pytest.raises(ValueError, match="Note content cannot be empty"):
        Note(session_id="session-123", user_id="user-456", content="")


def test_note_validation_empty_user_id():
    """空のuser_idでバリデーションエラー"""
    with pytest.raises(ValueError, match="Note user_id cannot be empty"):
        Note(session_id="session-123", user_id="", content="Test")


def test_note_validation_empty_session_id():
    """空のsession_idでバリデーションエラー"""
    with pytest.raises(ValueError, match="Note session_id cannot be empty"):
        Note(session_id="", user_id="user-456", content="Test")


def test_note_to_dict():
    """辞書変換テスト"""
    note = Note.create(
        session_id="session-123",
        user_id="user-456",
        content="Test content",
    )

    data = note.to_dict()

    assert data["session_id"] == "session-123"
    assert data["user_id"] == "user-456"
    assert data["content"] == "Test content"
    assert data["category"] == "general"
    assert "id" in data
    assert "created_at" in data
