"""Integration test for ClaudeAgentService message building

This test verifies that the ClaudeAgentService can correctly build
Claude API messages from Conversation entities with Message objects.

This test specifically catches the AttributeError that occurs when
trying to access .value on msg.role (which is a str, not an Enum).
"""

from unittest.mock import Mock

import pytest

from src.contexts.personal_tasks.domain.models.conversation import Conversation, Message
from src.domain.services.claude_agent_service import ClaudeAgentService


class TestClaudeAgentServiceMessageBuilding:
    """Test suite for ClaudeAgentService._build_messages method"""

    @pytest.fixture
    def service(self):
        """Create a ClaudeAgentService instance for testing"""
        # Create mock dependencies
        mock_anthropic_client = Mock()
        mock_tools = []  # Empty tools list is fine for this test

        return ClaudeAgentService(
            anthropic_client=mock_anthropic_client,
            tools=mock_tools
        )

    def test_build_messages_with_user_message(self, service):
        """Test building messages array with a user message

        This test verifies that Message objects with role as str
        can be correctly converted to Claude API format.

        Regression test for: AttributeError: 'str' object has no attribute 'value'
        """
        # Arrange: Create a conversation with user message
        user_message = Message.user(content="Hello, assistant!")

        conversation = Conversation.create(
            user_id="U12345",
            channel_id="C12345",
            messages=[user_message],
        )

        # Act: Build messages for Claude API
        result = service._build_messages(conversation)

        # Assert: Verify the result
        assert len(result) == 1
        assert result[0] == {"role": "user", "content": "Hello, assistant!"}

    def test_build_messages_with_conversation_history(self, service):
        """Test building messages array with full conversation history"""
        # Arrange: Create a conversation with multiple messages
        messages = [
            Message.user(content="What is 2+2?"),
            Message.assistant(content="2+2 equals 4."),
            Message.user(content="What about 3+3?"),
        ]

        conversation = Conversation.create(
            user_id="U12345",
            channel_id="C12345",
            messages=messages,
        )

        # Act: Build messages for Claude API
        result = service._build_messages(conversation)

        # Assert: Verify the result
        assert len(result) == 3
        assert result[0] == {"role": "user", "content": "What is 2+2?"}
        assert result[1] == {"role": "assistant", "content": "2+2 equals 4."}
        assert result[2] == {"role": "user", "content": "What about 3+3?"}

    def test_build_messages_preserves_message_order(self, service):
        """Test that message order is preserved"""
        # Arrange: Create messages with specific order
        messages = [
            Message.user(content="First"),
            Message.assistant(content="Second"),
            Message.user(content="Third"),
            Message.assistant(content="Fourth"),
        ]

        conversation = Conversation.create(
            user_id="U12345",
            channel_id="C12345",
            messages=messages,
        )

        # Act
        result = service._build_messages(conversation)

        # Assert: Order is preserved
        assert [msg["content"] for msg in result] == ["First", "Second", "Third", "Fourth"]

    def test_build_messages_handles_empty_conversation(self, service):
        """Test building messages from conversation with no messages"""
        # Arrange: Create empty conversation
        conversation = Conversation.create(
            user_id="U12345",
            channel_id="C12345",
            messages=[],
        )

        # Act
        result = service._build_messages(conversation)

        # Assert: Empty list is returned
        assert result == []
