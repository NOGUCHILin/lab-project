"""Message Value Object"""

from dataclasses import dataclass
from datetime import UTC, datetime


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
    def user(cls, content: str, timestamp: datetime | None = None) -> "Message":
        """Factory method to create a user message

        Args:
            content: User message content
            timestamp: Optional timestamp (defaults to now)

        Returns:
            New Message instance with role="user"
        """
        return cls(
            role="user",
            content=content,
            timestamp=timestamp or datetime.now(UTC),
        )

    @classmethod
    def assistant(cls, content: str, timestamp: datetime | None = None) -> "Message":
        """Factory method to create an assistant message

        Args:
            content: Assistant message content
            timestamp: Optional timestamp (defaults to now)

        Returns:
            New Message instance with role="assistant"
        """
        return cls(
            role="assistant",
            content=content,
            timestamp=timestamp or datetime.now(UTC),
        )

    def to_dict(self) -> dict[str, str]:
        """Convert message to dict format for Claude API

        Returns:
            Dict with "role" and "content" keys (timestamp excluded)
        """
        return {"role": self.role, "content": self.content}
