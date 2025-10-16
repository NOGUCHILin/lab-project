"""Unit tests for Conversation domain model"""

from datetime import datetime, timedelta, UTC
from uuid import UUID

import pytest

from src.contexts.personal_tasks.domain.models.conversation import Conversation, Message


class TestMessage:
    """Test suite for Message value object"""

    def test_create_user_message(self):
        """Test creating a user message"""
        message = Message.user("Hello, Claude!")

        assert message.role == "user"
        assert message.content == "Hello, Claude!"
        assert isinstance(message.timestamp, datetime)

    def test_create_assistant_message(self):
        """Test creating an assistant message"""
        message = Message.assistant("Hello! How can I help?")

        assert message.role == "assistant"
        assert message.content == "Hello! How can I help?"
        assert isinstance(message.timestamp, datetime)

    def test_message_to_dict(self):
        """Test converting message to dict for Claude API"""
        message = Message.user("Test message")
        message_dict = message.to_dict()

        assert message_dict == {
            "role": "user",
            "content": "Test message"
        }

    def test_message_equality(self):
        """Test message equality based on all fields"""
        timestamp = datetime.now(UTC)
        msg1 = Message(role="user", content="Test", timestamp=timestamp)
        msg2 = Message(role="user", content="Test", timestamp=timestamp)
        msg3 = Message(role="user", content="Different", timestamp=timestamp)

        assert msg1 == msg2
        assert msg1 != msg3


class TestConversationCreation:
    """Test suite for Conversation.create() factory method"""

    def test_create_conversation_with_minimum_fields(self):
        """Test creating conversation with only required fields"""
        conv = Conversation.create(
            user_id="U12345",
            channel_id="C67890"
        )

        assert conv.user_id == "U12345"
        assert conv.channel_id == "C67890"
        assert conv.messages == []
        assert isinstance(conv.id, UUID)
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)
        assert conv.expires_at is not None
        assert conv.expires_at > conv.created_at

    def test_create_conversation_with_custom_ttl(self):
        """Test creating conversation with custom TTL"""
        conv = Conversation.create(
            user_id="U12345",
            channel_id="C67890",
            ttl_hours=48
        )

        expected_expiry = conv.created_at + timedelta(hours=48)
        # Allow 1 second tolerance for test execution time
        assert abs((conv.expires_at - expected_expiry).total_seconds()) < 1

    def test_create_conversation_with_initial_messages(self):
        """Test creating conversation with initial messages"""
        initial_messages = [
            Message.user("Hello"),
            Message.assistant("Hi there!")
        ]
        conv = Conversation.create(
            user_id="U12345",
            channel_id="C67890",
            messages=initial_messages
        )

        assert len(conv.messages) == 2
        assert conv.messages[0].content == "Hello"
        assert conv.messages[1].content == "Hi there!"


class TestConversationAddMessage:
    """Test suite for Conversation.add_message() method"""

    def test_add_user_message(self):
        """Test adding a user message to conversation"""
        conv = Conversation.create("U123", "C456")
        original_updated_at = conv.updated_at

        conv.add_message(Message.user("New message"))

        assert len(conv.messages) == 1
        assert conv.messages[0].role == "user"
        assert conv.messages[0].content == "New message"
        assert conv.updated_at > original_updated_at

    def test_add_assistant_message(self):
        """Test adding an assistant message to conversation"""
        conv = Conversation.create("U123", "C456")
        conv.add_message(Message.user("Question"))

        conv.add_message(Message.assistant("Answer"))

        assert len(conv.messages) == 2
        assert conv.messages[1].role == "assistant"
        assert conv.messages[1].content == "Answer"

    def test_add_multiple_messages(self):
        """Test adding multiple messages maintains order"""
        conv = Conversation.create("U123", "C456")

        conv.add_message(Message.user("Message 1"))
        conv.add_message(Message.assistant("Response 1"))
        conv.add_message(Message.user("Message 2"))

        assert len(conv.messages) == 3
        assert conv.messages[0].content == "Message 1"
        assert conv.messages[1].content == "Response 1"
        assert conv.messages[2].content == "Message 2"


class TestConversationIsExpired:
    """Test suite for Conversation.is_expired() method"""

    def test_new_conversation_is_not_expired(self):
        """Test that newly created conversation is not expired"""
        conv = Conversation.create("U123", "C456", ttl_hours=24)

        assert conv.is_expired() is False

    def test_expired_conversation_is_expired(self):
        """Test that conversation past expiry time is expired"""
        conv = Conversation.create("U123", "C456", ttl_hours=24)
        # Manually set expires_at to past
        conv.expires_at = datetime.now(UTC) - timedelta(hours=1)

        assert conv.is_expired() is True

    def test_conversation_at_exact_expiry_is_expired(self):
        """Test that conversation at exact expiry time is considered expired"""
        conv = Conversation.create("U123", "C456", ttl_hours=24)
        # Set expires_at to now (edge case)
        conv.expires_at = datetime.now(UTC)

        assert conv.is_expired() is True


class TestConversationGetMessagesForAPI:
    """Test suite for Conversation.get_messages_for_api() method"""

    def test_get_messages_for_api_format(self):
        """Test that messages are formatted correctly for Claude API"""
        conv = Conversation.create("U123", "C456")
        conv.add_message(Message.user("Hello"))
        conv.add_message(Message.assistant("Hi there!"))

        api_messages = conv.get_messages_for_api()

        assert len(api_messages) == 2
        assert api_messages[0] == {"role": "user", "content": "Hello"}
        assert api_messages[1] == {"role": "assistant", "content": "Hi there!"}

    def test_get_messages_for_empty_conversation(self):
        """Test getting messages from empty conversation"""
        conv = Conversation.create("U123", "C456")

        api_messages = conv.get_messages_for_api()

        assert api_messages == []


class TestConversationEquality:
    """Test suite for Conversation equality"""

    def test_conversation_equality_by_id(self):
        """Test that conversations with same ID are equal"""
        conv1 = Conversation.create("U123", "C456")
        # Create another conversation with same ID
        conv2 = Conversation(
            id=conv1.id,
            user_id="U123",
            channel_id="C456",
            messages=[],
            created_at=conv1.created_at,
            updated_at=conv1.updated_at,
            expires_at=conv1.expires_at
        )

        assert conv1 == conv2

    def test_conversation_inequality_by_id(self):
        """Test that conversations with different IDs are not equal"""
        conv1 = Conversation.create("U123", "C456")
        conv2 = Conversation.create("U123", "C456")

        assert conv1 != conv2
