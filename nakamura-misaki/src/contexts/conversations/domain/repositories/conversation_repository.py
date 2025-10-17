"""Conversation Repository Interface"""

from abc import ABC, abstractmethod

from src.contexts.conversations.domain.entities.conversation import Conversation
from src.contexts.conversations.domain.value_objects.conversation_id import ConversationId
from src.shared_kernel.domain.value_objects.user_id import UserId


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
    def save(self, conversation: Conversation) -> None:
        """Save a conversation (create or update)

        Args:
            conversation: Conversation entity to persist
        """
        pass

    @abstractmethod
    def find_by_id(self, conversation_id: ConversationId) -> Conversation | None:
        """Get conversation by ID

        Args:
            conversation_id: Conversation unique identifier

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_user_and_channel(
        self, user_id: UserId, channel_id: str
    ) -> Conversation | None:
        """Get active conversation for user in channel

        Args:
            user_id: User ID
            channel_id: Channel ID

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, conversation_id: ConversationId) -> None:
        """Delete a conversation

        Args:
            conversation_id: Conversation ID to delete
        """
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        """Delete all expired conversations

        Returns:
            Number of conversations deleted
        """
        pass
