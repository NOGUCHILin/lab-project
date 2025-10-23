"""PostgreSQL Conversation Repository Implementation"""

import json
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.conversations.domain.entities.conversation import Conversation
from src.contexts.conversations.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from src.contexts.conversations.domain.value_objects.conversation_id import ConversationId
from src.contexts.conversations.domain.value_objects.message import Message
from src.infrastructure.database.schema import ConversationTable
from src.shared_kernel.domain.value_objects.user_id import UserId


class PostgreSQLConversationRepository(ConversationRepository):
    """PostgreSQL implementation of ConversationRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, conversation: Conversation) -> None:
        """Save conversation"""
        # Check if exists
        stmt = select(ConversationTable).where(ConversationTable.conversation_id == conversation.id.value)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.messages = [self._message_to_dict(msg) for msg in conversation.messages]
            existing.updated_at = conversation.updated_at
            existing.last_message_at = conversation.updated_at
        else:
            # Create new
            conversation_table = ConversationTable(
                conversation_id=conversation.id.value,
                user_id=conversation.user_id.value,
                channel_id=conversation.channel_id,
                messages=[self._message_to_dict(msg) for msg in conversation.messages],
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                last_message_at=conversation.updated_at,
            )
            self._session.add(conversation_table)

        await self._session.flush()

    async def find_by_id(self, conversation_id: ConversationId) -> Conversation | None:
        """Find conversation by ID"""
        stmt = select(ConversationTable).where(ConversationTable.conversation_id == conversation_id.value)
        result = await self._session.execute(stmt)
        conversation_table = result.scalar_one_or_none()

        if conversation_table is None:
            return None

        return self._to_entity(conversation_table)

    async def find_by_user_and_channel(self, user_id: UserId, channel_id: str) -> Conversation | None:
        """Find conversation by user and channel"""
        stmt = (
            select(ConversationTable)
            .where(ConversationTable.user_id == user_id.value)
            .where(ConversationTable.channel_id == channel_id)
            .order_by(ConversationTable.last_message_at.desc())
        )
        result = await self._session.execute(stmt)
        conversation_table = result.scalar_one_or_none()

        if conversation_table is None:
            return None

        return self._to_entity(conversation_table)

    async def delete(self, conversation_id: ConversationId) -> None:
        """Delete conversation"""
        stmt = delete(ConversationTable).where(ConversationTable.conversation_id == conversation_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_expired(self) -> int:
        """Delete all expired conversations"""
        # Find all expired conversations
        current_time = datetime.now(UTC)
        stmt = select(ConversationTable)
        result = await self._session.execute(stmt)
        all_conversations = result.scalars().all()

        deleted_count = 0
        for conv_table in all_conversations:
            conversation = self._to_entity(conv_table)
            if conversation.is_expired(current_time):
                await self.delete(conversation.id)
                deleted_count += 1

        return deleted_count

    async def find_recent(self, limit: int = 50) -> list[Conversation]:
        """Find recent conversations ordered by last_message_at"""
        stmt = select(ConversationTable).order_by(ConversationTable.last_message_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        conversation_tables = result.scalars().all()

        return [self._to_entity(conv_table) for conv_table in conversation_tables]

    def _to_entity(self, conversation_table: ConversationTable) -> Conversation:
        """Convert ConversationTable to Conversation entity"""
        # Handle case where messages might be stored as JSON string
        messages_data = conversation_table.messages
        if isinstance(messages_data, str):
            messages_data = json.loads(messages_data)

        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg.get("timestamp", conversation_table.created_at.isoformat())),
            )
            for msg in messages_data
        ]

        # Calculate expires_at as created_at + 24 hours (default TTL)
        expires_at = conversation_table.created_at + timedelta(hours=24)

        return Conversation(
            id=ConversationId(value=conversation_table.conversation_id),
            user_id=UserId(value=conversation_table.user_id),
            channel_id=conversation_table.channel_id,
            messages=messages,
            created_at=conversation_table.created_at,
            updated_at=conversation_table.updated_at,
            expires_at=expires_at,
        )

    def _message_to_dict(self, message: Message) -> dict:
        """Convert Message to dict for storage"""
        return {
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
        }
