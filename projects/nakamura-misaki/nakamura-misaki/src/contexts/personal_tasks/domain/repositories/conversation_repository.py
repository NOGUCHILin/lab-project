"""Conversation Repository interface - Domain layer"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models.conversation import Conversation


class ConversationRepository(ABC):
    """Repository interface for Conversation aggregate

    Defines persistence operations for Conversation entities.
    Implementations are provided in the Infrastructure layer.

    This interface follows Repository pattern from DDD:
    - Domain layer defines the interface
    - Infrastructure layer provides concrete implementation
    - Application layer depends on this abstraction
    """

    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """Save a conversation (create or update)

        Args:
            conversation: Conversation entity to persist
        """
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Get conversation by ID

        Args:
            conversation_id: Conversation unique identifier

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_user_and_channel(
        self,
        user_id: str,
        channel_id: str
    ) -> Conversation | None:
        """Get active conversation for user in channel

        Args:
            user_id: Slack user ID
            channel_id: Slack channel ID

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, conversation_id: UUID) -> None:
        """Delete a conversation

        Args:
            conversation_id: Conversation ID to delete
        """
        pass

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete all expired conversations

        Returns:
            Number of conversations deleted
        """
        pass
