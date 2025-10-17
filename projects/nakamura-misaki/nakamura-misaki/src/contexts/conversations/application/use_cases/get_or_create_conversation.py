"""Get or Create Conversation Use Case"""

from dataclasses import dataclass

from src.contexts.conversations.domain.entities.conversation import Conversation
from src.contexts.conversations.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from src.shared_kernel.domain.value_objects.user_id import UserId


@dataclass
class GetOrCreateConversationCommand:
    """Get or create conversation command"""

    user_id: str
    channel_id: str
    ttl_hours: int = 24


class GetOrCreateConversationUseCase:
    """Get or create conversation use case"""

    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    async def execute(self, command: GetOrCreateConversationCommand) -> Conversation:
        """Execute get or create conversation use case"""
        user_id = UserId(value=command.user_id)

        # Try to find existing conversation
        conversation = await self._conversation_repository.find_by_user_and_channel(
            user_id, command.channel_id
        )

        # If conversation exists and not expired, return it
        if conversation and not conversation.is_expired():
            return conversation

        # If expired, delete it
        if conversation and conversation.is_expired():
            await self._conversation_repository.delete(conversation.id)

        # Create new conversation
        new_conversation = Conversation.create(
            user_id=user_id,
            channel_id=command.channel_id,
            ttl_hours=command.ttl_hours,
        )

        await self._conversation_repository.save(new_conversation)
        return new_conversation
