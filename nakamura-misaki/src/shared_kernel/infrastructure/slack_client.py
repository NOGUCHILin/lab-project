"""SlackClient interface - Shared infrastructure abstraction"""

from abc import ABC, abstractmethod


class SlackClient(ABC):
    """Slack API client interface

    Shared abstraction for Slack API communication across contexts.
    Concrete implementations provided in Infrastructure layer.

    This interface enables:
    - Dependency injection in Application layer
    - Easy mocking for tests
    - Multiple implementations (real API, mock, etc.)
    """

    @abstractmethod
    async def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: str | None = None
    ) -> str:
        """Send a message to Slack channel

        Args:
            channel: Slack channel ID (e.g., "C12345")
            text: Message text content
            thread_ts: Optional thread timestamp for threading

        Returns:
            Message timestamp (ts) for the sent message
        """
        pass

    @abstractmethod
    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> None:
        """Add a reaction emoji to a message

        Args:
            channel: Slack channel ID
            timestamp: Message timestamp (ts)
            emoji: Emoji name without colons (e.g., "eyes", "white_check_mark")
        """
        pass
