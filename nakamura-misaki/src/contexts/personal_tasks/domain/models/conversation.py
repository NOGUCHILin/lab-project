"""Conversation domain model - Personal Tasks Context"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Message:
    """Message value object

    Represents a single message in a conversation between user and assistant.
    Immutable value object.

    Attributes:
        role: Message role ("user" or "assistant")
        content: Message content text
        timestamp: When the message was created
    """

    role: str
    content: str
    timestamp: datetime

    @classmethod
    def user(cls, content: str) -> "Message":
        """Factory method to create a user message

        Args:
            content: User message content

        Returns:
            New Message instance with role="user"
        """
        return cls(
            role="user",
            content=content,
            timestamp=datetime.now(UTC)
        )

    @classmethod
    def assistant(cls, content: str) -> "Message":
        """Factory method to create an assistant message

        Args:
            content: Assistant message content

        Returns:
            New Message instance with role="assistant"
        """
        return cls(
            role="assistant",
            content=content,
            timestamp=datetime.now(UTC)
        )

    def to_dict(self) -> dict[str, str]:
        """Convert message to dict format for Claude API

        Returns:
            Dict with "role" and "content" keys (timestamp excluded)
        """
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class Conversation:
    """Conversation aggregate root - Personal Tasks Context

    Represents a conversation context between a user and the AI assistant.
    Manages message history and conversation lifecycle.

    Attributes:
        id: Unique identifier for the conversation
        user_id: Slack user ID who owns this conversation
        channel_id: Slack channel ID where conversation occurs
        messages: List of messages in chronological order
        created_at: When the conversation was created
        updated_at: When the conversation was last updated
        expires_at: When the conversation expires (for cleanup)

    Business Rules:
        - Conversations expire after a configurable TTL (default 24 hours)
        - Messages are stored in chronological order
        - Expired conversations should be cleaned up
    """

    id: UUID
    user_id: str
    channel_id: str
    messages: list[Message]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    @classmethod
    def create(
        cls,
        user_id: str,
        channel_id: str,
        ttl_hours: int = 24,
        messages: list[Message] | None = None
    ) -> "Conversation":
        """Factory method to create a new Conversation

        Args:
            user_id: Slack user ID
            channel_id: Slack channel ID
            ttl_hours: Time-to-live in hours (default 24)
            messages: Initial messages (optional)

        Returns:
            New Conversation instance
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=ttl_hours)

        return cls(
            id=uuid4(),
            user_id=user_id,
            channel_id=channel_id,
            messages=messages or [],
            created_at=now,
            updated_at=now,
            expires_at=expires_at
        )

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation

        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def is_expired(self) -> bool:
        """Check if conversation has expired

        Returns:
            True if current time >= expires_at, False otherwise
        """
        return datetime.now(UTC) >= self.expires_at

    def get_messages_for_api(self) -> list[dict[str, str]]:
        """Get messages formatted for Claude API

        Returns:
            List of message dicts with "role" and "content" keys
        """
        return [msg.to_dict() for msg in self.messages]

    def __eq__(self, other: object) -> bool:
        """Conversations are equal if they have the same ID"""
        if not isinstance(other, Conversation):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets/dicts"""
        return hash(self.id)
