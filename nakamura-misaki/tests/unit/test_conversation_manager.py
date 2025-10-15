"""
Unit tests for ConversationManager domain service.

Following TDD: Red -> Green -> Refactor
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.domain.models.conversation import Conversation, Message, MessageRole
from src.domain.services.conversation_manager import ConversationManager


@pytest.fixture
def mock_repository():
    """Mock ConversationRepository."""
    repository = Mock()
    repository.save = AsyncMock()
    repository.get_by_user_and_channel = AsyncMock()
    repository.delete_expired = AsyncMock()
    return repository


@pytest.fixture
def conversation_manager(mock_repository):
    """Create ConversationManager instance."""
    return ConversationManager(repository=mock_repository, ttl_hours=24)


@pytest.mark.asyncio
async def test_get_or_create_new_conversation(conversation_manager, mock_repository):
    """Should create new conversation when none exists."""
    user_id = "U5D0CJKMH"
    channel_id = "C1234567890"
    initial_message = "こんにちは"

    # No existing conversation
    mock_repository.get_by_user_and_channel.return_value = None

    conversation = await conversation_manager.get_or_create(
        user_id=user_id,
        channel_id=channel_id,
        initial_message=initial_message,
    )

    assert conversation.user_id == user_id
    assert conversation.channel_id == channel_id
    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[0].content == initial_message

    # Should save new conversation
    mock_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_existing_not_expired(conversation_manager, mock_repository):
    """Should return existing conversation when not expired."""
    user_id = "U5D0CJKMH"
    channel_id = "C1234567890"

    existing_conversation = Conversation(
        conversation_id=uuid4(),
        user_id=user_id,
        channel_id=channel_id,
        messages=[Message(role=MessageRole.USER, content="既存メッセージ")],
    )

    mock_repository.get_by_user_and_channel.return_value = existing_conversation

    conversation = await conversation_manager.get_or_create(
        user_id=user_id,
        channel_id=channel_id,
        initial_message="新規メッセージ",
    )

    assert conversation.conversation_id == existing_conversation.conversation_id
    assert len(conversation.messages) == 1  # No new message added yet

    # Should not save (just returned existing)
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_existing_expired(conversation_manager, mock_repository):
    """Should create new conversation when existing one is expired."""
    user_id = "U5D0CJKMH"
    channel_id = "C1234567890"

    # Expired conversation (25 hours old)
    old_time = datetime.now(timezone.utc) - timedelta(hours=25)
    expired_conversation = Conversation(
        conversation_id=uuid4(),
        user_id=user_id,
        channel_id=channel_id,
        messages=[Message(role=MessageRole.USER, content="古いメッセージ")],
        last_message_at=old_time,
    )

    mock_repository.get_by_user_and_channel.return_value = expired_conversation

    conversation = await conversation_manager.get_or_create(
        user_id=user_id,
        channel_id=channel_id,
        initial_message="新規メッセージ",
    )

    # Should create new conversation (different ID)
    assert conversation.conversation_id != expired_conversation.conversation_id
    assert len(conversation.messages) == 1
    assert conversation.messages[0].content == "新規メッセージ"

    # Should save new conversation
    mock_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_add_user_message(conversation_manager, mock_repository):
    """Should add user message to conversation."""
    user_id = "U5D0CJKMH"
    channel_id = "C1234567890"

    existing_conversation = Conversation(
        conversation_id=uuid4(),
        user_id=user_id,
        channel_id=channel_id,
        messages=[Message(role=MessageRole.USER, content="初回")],
    )

    mock_repository.get_by_user_and_channel.return_value = existing_conversation

    await conversation_manager.add_user_message(
        user_id=user_id,
        channel_id=channel_id,
        message="追加メッセージ",
    )

    # Should add message and save
    assert len(existing_conversation.messages) == 2
    assert existing_conversation.messages[1].role == MessageRole.USER
    assert existing_conversation.messages[1].content == "追加メッセージ"

    mock_repository.save.assert_called_once_with(existing_conversation)


@pytest.mark.asyncio
async def test_add_assistant_message(conversation_manager, mock_repository):
    """Should add assistant message to conversation."""
    user_id = "U5D0CJKMH"
    channel_id = "C1234567890"

    existing_conversation = Conversation(
        conversation_id=uuid4(),
        user_id=user_id,
        channel_id=channel_id,
        messages=[Message(role=MessageRole.USER, content="ユーザーメッセージ")],
    )

    mock_repository.get_by_user_and_channel.return_value = existing_conversation

    await conversation_manager.add_assistant_message(
        user_id=user_id,
        channel_id=channel_id,
        message="アシスタント応答",
    )

    # Should add message and save
    assert len(existing_conversation.messages) == 2
    assert existing_conversation.messages[1].role == MessageRole.ASSISTANT
    assert existing_conversation.messages[1].content == "アシスタント応答"

    mock_repository.save.assert_called_once_with(existing_conversation)


@pytest.mark.asyncio
async def test_get_conversation_history(conversation_manager, mock_repository):
    """Should get conversation history for Claude API."""
    user_id = "U5D0CJKMH"
    channel_id = "C1234567890"

    existing_conversation = Conversation(
        conversation_id=uuid4(),
        user_id=user_id,
        channel_id=channel_id,
        messages=[
            Message(role=MessageRole.USER, content="タスク登録"),
            Message(role=MessageRole.ASSISTANT, content="承知しました"),
            Message(role=MessageRole.USER, content="明日までにレポート"),
        ],
    )

    mock_repository.get_by_user_and_channel.return_value = existing_conversation

    history = await conversation_manager.get_conversation_history(
        user_id=user_id,
        channel_id=channel_id,
    )

    assert len(history) == 3
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "タスク登録"
    assert history[1]["role"] == "assistant"
    assert history[2]["role"] == "user"


@pytest.mark.asyncio
async def test_get_conversation_history_no_conversation(
    conversation_manager, mock_repository
):
    """Should return empty list when no conversation exists."""
    mock_repository.get_by_user_and_channel.return_value = None

    history = await conversation_manager.get_conversation_history(
        user_id="U999999",
        channel_id="C999999",
    )

    assert history == []


@pytest.mark.asyncio
async def test_cleanup_expired_conversations(conversation_manager, mock_repository):
    """Should clean up expired conversations."""
    mock_repository.delete_expired.return_value = 5

    deleted_count = await conversation_manager.cleanup_expired()

    assert deleted_count == 5
    mock_repository.delete_expired.assert_called_once_with(ttl_hours=24)


@pytest.mark.asyncio
async def test_custom_ttl_hours(mock_repository):
    """Should support custom TTL hours."""
    manager = ConversationManager(repository=mock_repository, ttl_hours=12)

    mock_repository.delete_expired.return_value = 3

    await manager.cleanup_expired()

    mock_repository.delete_expired.assert_called_once_with(ttl_hours=12)
