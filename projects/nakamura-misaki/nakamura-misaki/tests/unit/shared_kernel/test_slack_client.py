"""Unit tests for SlackClient interface"""

import pytest

from src.shared_kernel.infrastructure.slack_client import SlackClient


class FakeSlackClient(SlackClient):
    """Fake implementation for testing interface"""

    def __init__(self):
        self.sent_messages = []
        self.reactions_added = []

    async def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: str | None = None
    ) -> str:
        """Fake implementation that records sent messages"""
        self.sent_messages.append({
            "channel": channel,
            "text": text,
            "thread_ts": thread_ts
        })
        return "1234567890.123456"  # Fake timestamp

    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> None:
        """Fake implementation that records reactions"""
        self.reactions_added.append({
            "channel": channel,
            "timestamp": timestamp,
            "emoji": emoji
        })


class TestSlackClientInterface:
    """Test suite for SlackClient interface"""

    @pytest.fixture
    def client(self) -> FakeSlackClient:
        return FakeSlackClient()

    @pytest.mark.asyncio
    async def test_send_message_to_channel(self, client: FakeSlackClient):
        """Test sending a message to a channel"""
        ts = await client.send_message(
            channel="C12345",
            text="Hello, world!"
        )

        assert ts == "1234567890.123456"
        assert len(client.sent_messages) == 1
        assert client.sent_messages[0]["channel"] == "C12345"
        assert client.sent_messages[0]["text"] == "Hello, world!"
        assert client.sent_messages[0]["thread_ts"] is None

    @pytest.mark.asyncio
    async def test_send_message_in_thread(self, client: FakeSlackClient):
        """Test sending a message in a thread"""
        ts = await client.send_message(
            channel="C12345",
            text="Reply in thread",
            thread_ts="1234567890.000000"
        )

        assert ts == "1234567890.123456"
        assert len(client.sent_messages) == 1
        assert client.sent_messages[0]["thread_ts"] == "1234567890.000000"

    @pytest.mark.asyncio
    async def test_send_multiple_messages(self, client: FakeSlackClient):
        """Test sending multiple messages"""
        await client.send_message("C12345", "Message 1")
        await client.send_message("C12345", "Message 2")
        await client.send_message("C67890", "Message 3")

        assert len(client.sent_messages) == 3
        assert client.sent_messages[0]["text"] == "Message 1"
        assert client.sent_messages[1]["text"] == "Message 2"
        assert client.sent_messages[2]["channel"] == "C67890"

    @pytest.mark.asyncio
    async def test_add_reaction(self, client: FakeSlackClient):
        """Test adding a reaction to a message"""
        await client.add_reaction(
            channel="C12345",
            timestamp="1234567890.123456",
            emoji="eyes"
        )

        assert len(client.reactions_added) == 1
        assert client.reactions_added[0]["channel"] == "C12345"
        assert client.reactions_added[0]["timestamp"] == "1234567890.123456"
        assert client.reactions_added[0]["emoji"] == "eyes"

    @pytest.mark.asyncio
    async def test_add_multiple_reactions(self, client: FakeSlackClient):
        """Test adding multiple reactions"""
        await client.add_reaction("C12345", "1234567890.123456", "eyes")
        await client.add_reaction("C12345", "1234567890.123456", "white_check_mark")

        assert len(client.reactions_added) == 2
        assert client.reactions_added[0]["emoji"] == "eyes"
        assert client.reactions_added[1]["emoji"] == "white_check_mark"

    @pytest.mark.asyncio
    async def test_send_message_and_add_reaction(self, client: FakeSlackClient):
        """Test typical workflow: send message then add reaction"""
        # Send message
        ts = await client.send_message("C12345", "Processing...")

        # Add reaction to indicate completion
        await client.add_reaction("C12345", ts, "white_check_mark")

        assert len(client.sent_messages) == 1
        assert len(client.reactions_added) == 1
        assert client.reactions_added[0]["timestamp"] == ts
