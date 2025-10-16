"""Conversation domain model for managing chat history with Claude."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum


class MessageRole(str, Enum):
    """Message role for Claude API."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class Message:
    """Immutable message value object.

    Represents a single message in a conversation.
    Follows Claude Messages API format.
    """

    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        """Validate message."""
        if not self.content:
            raise ValueError("Message content cannot be empty")

        # Convert string to enum if needed
        if isinstance(self.role, str):
            object.__setattr__(self, "role", MessageRole(self.role))

    def to_dict(self) -> dict[str, str]:
        """Convert to Claude API format.

        Returns:
            dict: {"role": "user"|"assistant", "content": "..."}
        """
        return {"role": self.role.value, "content": self.content}


@dataclass
class Conversation:
    """Conversation entity for managing chat history.

    Stores conversation history between user and assistant.
    Supports TTL-based expiration for session management.
    """

    conversation_id: uuid.UUID
    user_id: str
    channel_id: str
    messages: list[Message]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_message_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate conversation."""
        if not self.user_id:
            raise ValueError("Conversation user_id cannot be empty")
        if not self.channel_id:
            raise ValueError("Conversation channel_id cannot be empty")

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.

        Args:
            message: Message to add

        Side effects:
            - Appends message to messages list
            - Updates updated_at timestamp
            - Updates last_message_at timestamp
        """
        self.messages.append(message)
        now = datetime.now(UTC)
        self.updated_at = now
        self.last_message_at = now

    def is_expired(self, ttl_hours: int) -> bool:
        """Check if conversation has expired based on TTL.

        Args:
            ttl_hours: Time-to-live in hours (e.g., 24)

        Returns:
            bool: True if conversation is expired, False otherwise
        """
        now = datetime.now(UTC)
        expiration_time = self.last_message_at + timedelta(hours=ttl_hours)
        return now > expiration_time

    def get_messages_for_claude_api(self) -> list[dict[str, str]]:
        """Get messages formatted for Claude API.

        Returns:
            list[dict]: List of messages in Claude API format
                [{"role": "user", "content": "..."}, ...]
        """
        return [message.to_dict() for message in self.messages]

    def __eq__(self, other: object) -> bool:
        """Compare conversations by conversation_id."""
        if not isinstance(other, Conversation):
            return False
        return self.conversation_id == other.conversation_id

    def __hash__(self) -> int:
        """Hash by conversation_id."""
        return hash(self.conversation_id)
