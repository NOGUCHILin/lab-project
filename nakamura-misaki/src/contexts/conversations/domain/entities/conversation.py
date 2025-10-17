"""Conversation Entity"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.contexts.conversations.domain.value_objects.conversation_id import ConversationId
from src.contexts.conversations.domain.value_objects.message import Message
from src.shared_kernel.domain.value_objects.user_id import UserId


@dataclass
class Conversation:
    """Conversation aggregate root - Conversations Context

    Represents a conversation context between a user and the AI assistant.
    Manages message history and conversation lifecycle.

    Attributes:
        id: Unique identifier for the conversation
        user_id: User ID who owns this conversation
        channel_id: Channel ID where conversation occurs
        messages: List of messages in chronological order
        created_at: When the conversation was created
        updated_at: When the conversation was last updated
        expires_at: When the conversation expires (for cleanup)

    Business Rules:
        - Conversations expire after a configurable TTL (default 24 hours)
        - Messages are stored in chronological order
        - Expired conversations should be cleaned up
    """

    id: ConversationId
    user_id: UserId
    channel_id: str
    messages: list[Message]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        channel_id: str,
        ttl_hours: int = 24,
        messages: list[Message] | None = None,
    ) -> "Conversation":
        """Factory method to create a new Conversation

        Args:
            user_id: User ID
            channel_id: Channel ID (e.g., Slack channel)
            ttl_hours: Time-to-live in hours (default 24)
            messages: Initial messages (optional)

        Returns:
            New Conversation instance
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=ttl_hours)

        return cls(
            id=ConversationId.generate(),
            user_id=user_id,
            channel_id=channel_id,
            messages=messages or [],
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
        )

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation

        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def is_expired(self, current_time: datetime | None = None) -> bool:
        """Check if conversation has expired

        Args:
            current_time: Optional time to check against (defaults to now)

        Returns:
            True if current time >= expires_at, False otherwise
        """
        check_time = current_time or datetime.now(UTC)
        return check_time >= self.expires_at

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
