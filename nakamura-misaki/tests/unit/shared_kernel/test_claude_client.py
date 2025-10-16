"""Unit tests for ClaudeClient interface"""

from typing import AsyncIterator

import pytest

from src.shared_kernel.infrastructure.claude_client import ClaudeClient, ClaudeMessage, ClaudeResponse


class FakeClaudeClient(ClaudeClient):
    """Fake implementation for testing interface"""

    def __init__(self):
        self.call_count = 0
        self.last_messages = []
        self.last_system_prompt = None

    async def send_message(
        self,
        messages: list[ClaudeMessage],
        system_prompt: str | None = None
    ) -> ClaudeResponse:
        """Fake implementation that returns a test response"""
        self.call_count += 1
        self.last_messages = messages
        self.last_system_prompt = system_prompt

        return ClaudeResponse(
            content="Test response",
            model="claude-3-5-sonnet-20241022",
            stop_reason="end_turn",
            usage={"input_tokens": 100, "output_tokens": 50}
        )

    async def send_message_stream(
        self,
        messages: list[ClaudeMessage],
        system_prompt: str | None = None
    ) -> AsyncIterator[str]:
        """Fake implementation that yields test chunks"""
        self.call_count += 1
        self.last_messages = messages
        self.last_system_prompt = system_prompt

        for chunk in ["Test ", "streaming ", "response"]:
            yield chunk


class TestClaudeClientInterface:
    """Test suite for ClaudeClient interface"""

    @pytest.fixture
    def client(self) -> FakeClaudeClient:
        return FakeClaudeClient()

    @pytest.mark.asyncio
    async def test_send_message_basic(self, client: FakeClaudeClient):
        """Test basic message sending"""
        messages = [
            ClaudeMessage(role="user", content="Hello")
        ]

        response = await client.send_message(messages)

        assert response.content == "Test response"
        assert response.model == "claude-3-5-sonnet-20241022"
        assert response.stop_reason == "end_turn"
        assert client.call_count == 1

    @pytest.mark.asyncio
    async def test_send_message_with_system_prompt(self, client: FakeClaudeClient):
        """Test sending message with system prompt"""
        messages = [ClaudeMessage(role="user", content="Hello")]
        system_prompt = "You are a helpful assistant."

        await client.send_message(messages, system_prompt=system_prompt)

        assert client.last_system_prompt == system_prompt

    @pytest.mark.asyncio
    async def test_send_message_with_conversation_history(
        self,
        client: FakeClaudeClient
    ):
        """Test sending message with conversation history"""
        messages = [
            ClaudeMessage(role="user", content="What is 2+2?"),
            ClaudeMessage(role="assistant", content="4"),
            ClaudeMessage(role="user", content="What about 3+3?")
        ]

        await client.send_message(messages)

        assert len(client.last_messages) == 3
        assert client.last_messages[0].content == "What is 2+2?"

    @pytest.mark.asyncio
    async def test_send_message_stream(self, client: FakeClaudeClient):
        """Test streaming message response"""
        messages = [ClaudeMessage(role="user", content="Hello")]

        chunks = []
        async for chunk in client.send_message_stream(messages):
            chunks.append(chunk)

        assert chunks == ["Test ", "streaming ", "response"]
        assert client.call_count == 1

    @pytest.mark.asyncio
    async def test_response_usage_tracking(self, client: FakeClaudeClient):
        """Test that response includes usage information"""
        messages = [ClaudeMessage(role="user", content="Hello")]

        response = await client.send_message(messages)

        assert "input_tokens" in response.usage
        assert "output_tokens" in response.usage
        assert response.usage["input_tokens"] == 100
        assert response.usage["output_tokens"] == 50


class TestClaudeMessageDataClass:
    """Test suite for ClaudeMessage data class"""

    def test_create_message(self):
        """Test creating a ClaudeMessage"""
        msg = ClaudeMessage(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_to_dict(self):
        """Test converting message to dict"""
        msg = ClaudeMessage(role="assistant", content="Hi there!")

        msg_dict = msg.to_dict()

        assert msg_dict == {"role": "assistant", "content": "Hi there!"}


class TestClaudeResponseDataClass:
    """Test suite for ClaudeResponse data class"""

    def test_create_response(self):
        """Test creating a ClaudeResponse"""
        response = ClaudeResponse(
            content="Test response",
            model="claude-3-5-sonnet-20241022",
            stop_reason="end_turn",
            usage={"input_tokens": 100, "output_tokens": 50}
        )

        assert response.content == "Test response"
        assert response.model == "claude-3-5-sonnet-20241022"
        assert response.stop_reason == "end_turn"
        assert response.usage["input_tokens"] == 100
