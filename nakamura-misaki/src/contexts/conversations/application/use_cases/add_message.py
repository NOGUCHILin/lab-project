"""Add Message Use Case"""

from dataclasses import dataclass

from src.contexts.conversations.domain.entities.conversation import Conversation
from src.contexts.conversations.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from src.contexts.conversations.domain.value_objects.conversation_id import ConversationId
from src.contexts.conversations.domain.value_objects.message import Message


@dataclass
class AddMessageCommand:
    """Add message command"""

    conversation_id: str
    role: str
    content: str


class AddMessageUseCase:
    """Add message to conversation use case"""

    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    async def execute(self, command: AddMessageCommand) -> Conversation:
        """Execute add message use case"""
        conversation_id = ConversationId.from_string(command.conversation_id)
        conversation = await self._conversation_repository.find_by_id(conversation_id)

        if not conversation:
            raise ValueError(f"Conversation not found: {command.conversation_id}")

        # Create message
        if command.role == "user":
            message = Message.user(command.content)
        elif command.role == "assistant":
            message = Message.assistant(command.content)
        else:
            raise ValueError(f"Invalid role: {command.role}")

        # Add message to conversation
        conversation.add_message(message)

        # Save conversation
        await self._conversation_repository.save(conversation)

        return conversation
