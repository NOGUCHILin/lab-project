"""ClaudeClient interface - Shared infrastructure abstraction"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class ClaudeMessage:
    """Message for Claude API

    Represents a single message in Claude conversation format.

    Attributes:
        role: Message role ("user" or "assistant")
        content: Message content text
    """

    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dict format for Claude API

        Returns:
            Dict with "role" and "content" keys
        """
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class ClaudeResponse:
    """Response from Claude API

    Represents a complete response from Claude.

    Attributes:
        content: Response content text
        model: Model used for generation
        stop_reason: Why the generation stopped
        usage: Token usage information
    """

    content: str
    model: str
    stop_reason: str
    usage: dict[str, int]


class ClaudeClient(ABC):
    """Claude API client interface

    Shared abstraction for Claude API communication across contexts.
    Concrete implementations provided in Infrastructure layer.

    This interface enables:
    - Dependency injection in Application layer
    - Easy mocking for tests
    - Multiple implementations (real API, mock, etc.)
    """

    @abstractmethod
    async def send_message(
        self,
        messages: list[ClaudeMessage],
        system_prompt: str | None = None
    ) -> ClaudeResponse:
        """Send message to Claude and get complete response

        Args:
            messages: List of messages (conversation history + new message)
            system_prompt: Optional system prompt

        Returns:
            ClaudeResponse with content and metadata
        """
        pass

    @abstractmethod
    async def send_message_stream(
        self,
        messages: list[ClaudeMessage],
        system_prompt: str | None = None
    ) -> AsyncIterator[str]:
        """Send message to Claude and stream response

        Args:
            messages: List of messages (conversation history + new message)
            system_prompt: Optional system prompt

        Yields:
            Response content chunks as they arrive
        """
        # This is an abstract async generator, implementation in subclasses
        if False:  # pragma: no cover
            yield ""
