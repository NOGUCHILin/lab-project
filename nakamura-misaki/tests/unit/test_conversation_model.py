"""
Unit tests for Conversation entity.

Tests the domain model for conversation history management.
Following TDD: Red -> Green -> Refactor
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.domain.models.conversation import Conversation, Message, MessageRole


class TestMessage:
    """Tests for Message value object."""

    def test_create_user_message(self):
        """Should create a user message with text content."""
        message = Message(
            role=MessageRole.USER,
            content="タスクを登録して",
        )

        assert message.role == MessageRole.USER
        assert message.content == "タスクを登録して"

    def test_create_assistant_message(self):
        """Should create an assistant message."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="承知しました。タスクのタイトルを教えてください。",
        )

        assert message.role == MessageRole.ASSISTANT
        assert message.content == "承知しました。タスクのタイトルを教えてください。"

    def test_message_immutability(self):
        """Messages should be immutable (frozen dataclass)."""
        message = Message(role=MessageRole.USER, content="test")

        with pytest.raises(AttributeError):
            message.content = "modified"  # type: ignore


class TestConversation:
    """Tests for Conversation entity."""

    def test_create_new_conversation(self):
        """Should create a new conversation with initial message."""
        conversation_id = uuid4()
        user_id = "U5D0CJKMH"
        channel_id = "C1234567890"
        initial_message = Message(role=MessageRole.USER, content="こんにちは")

        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            channel_id=channel_id,
            messages=[initial_message],
        )

        assert conversation.conversation_id == conversation_id
        assert conversation.user_id == user_id
        assert conversation.channel_id == channel_id
        assert len(conversation.messages) == 1
        assert conversation.messages[0] == initial_message
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
        assert isinstance(conversation.last_message_at, datetime)

    def test_add_message(self):
        """Should add a message to the conversation."""
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="初回メッセージ")],
        )

        initial_message_count = len(conversation.messages)
        initial_updated_at = conversation.updated_at

        new_message = Message(role=MessageRole.ASSISTANT, content="こんにちは！")
        conversation.add_message(new_message)

        assert len(conversation.messages) == initial_message_count + 1
        assert conversation.messages[-1] == new_message
        assert conversation.updated_at > initial_updated_at
        assert conversation.last_message_at > initial_updated_at

    def test_is_expired_not_expired(self):
        """Should return False if conversation is within TTL."""
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="test")],
        )

        ttl_hours = 24
        assert not conversation.is_expired(ttl_hours)

    def test_is_expired_expired(self):
        """Should return True if conversation exceeds TTL."""
        past_time = datetime.now(timezone.utc) - timedelta(hours=25)

        conversation = Conversation(
            conversation_id=uuid4(),
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="test")],
            last_message_at=past_time,
        )

        ttl_hours = 24
        assert conversation.is_expired(ttl_hours)

    def test_get_messages_for_claude_api(self):
        """Should format messages for Claude API."""
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[
                Message(role=MessageRole.USER, content="タスクを登録"),
                Message(role=MessageRole.ASSISTANT, content="承知しました"),
                Message(role=MessageRole.USER, content="明日までにレポート作成"),
            ],
        )

        claude_messages = conversation.get_messages_for_claude_api()

        assert len(claude_messages) == 3
        assert claude_messages[0] == {"role": "user", "content": "タスクを登録"}
        assert claude_messages[1] == {"role": "assistant", "content": "承知しました"}
        assert claude_messages[2] == {"role": "user", "content": "明日までにレポート作成"}

    def test_conversation_with_empty_messages_should_fail(self):
        """Should raise ValueError when creating conversation with no messages."""
        with pytest.raises(ValueError, match="Conversation must have at least one message"):
            Conversation(
                conversation_id=uuid4(),
                user_id="U5D0CJKMH",
                channel_id="C1234567890",
                messages=[],
            )

    def test_conversation_equality(self):
        """Should compare conversations by conversation_id."""
        conversation_id = uuid4()

        conversation1 = Conversation(
            conversation_id=conversation_id,
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="test")],
        )

        conversation2 = Conversation(
            conversation_id=conversation_id,
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="different")],
        )

        assert conversation1 == conversation2

    def test_conversation_inequality(self):
        """Should compare conversations by conversation_id."""
        conversation1 = Conversation(
            conversation_id=uuid4(),
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="test")],
        )

        conversation2 = Conversation(
            conversation_id=uuid4(),
            user_id="U5D0CJKMH",
            channel_id="C1234567890",
            messages=[Message(role=MessageRole.USER, content="test")],
        )

        assert conversation1 != conversation2
