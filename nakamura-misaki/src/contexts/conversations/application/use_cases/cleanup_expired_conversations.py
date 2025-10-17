"""Cleanup Expired Conversations Use Case"""

from src.contexts.conversations.domain.repositories.conversation_repository import (
    ConversationRepository,
)


class CleanupExpiredConversationsUseCase:
    """Cleanup expired conversations use case"""

    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    def execute(self) -> int:
        """Execute cleanup expired conversations use case

        Returns:
            Number of conversations deleted
        """
        return self._conversation_repository.delete_expired()
