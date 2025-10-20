"""PostgreSQL Conversation Repository for Personal Tasks Context"""

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.personal_tasks.domain.models.conversation import Conversation, Message
from src.contexts.personal_tasks.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from src.infrastructure.database.schema import ConversationTable


class PostgreSQLConversationRepository(ConversationRepository):
    """PostgreSQL implementation of ConversationRepository for Personal Tasks context"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, conversation: Conversation) -> None:
        """Save conversation"""
        # Check if exists
        stmt = select(ConversationTable).where(
            ConversationTable.conversation_id == conversation.id
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        # Serialize messages to JSON
        messages_json = json.dumps([
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation.messages
        ])

        if existing:
            # Update
            existing.user_id = conversation.user_id
            existing.channel_id = conversation.channel_id
            existing.messages = messages_json
            existing.updated_at = conversation.updated_at
            # Note: expires_at is not stored in DB, calculated from created_at
        else:
            # Insert (note: expires_at not stored in DB, calculated from created_at)
            new_conv = ConversationTable(
                conversation_id=conversation.id,
                user_id=conversation.user_id,
                channel_id=conversation.channel_id,
                messages=messages_json,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
            self._session.add(new_conv)

        await self._session.flush()

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Get conversation by ID"""
        stmt = select(ConversationTable).where(
            ConversationTable.conversation_id == conversation_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Deserialize messages from JSON
        messages_data = json.loads(model.messages)
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in messages_data
        ]

        # Calculate expires_at as created_at + 24 hours (default TTL)
        expires_at = model.created_at + timedelta(hours=24)

        return Conversation(
            id=model.conversation_id,
            user_id=model.user_id,
            channel_id=model.channel_id,
            messages=messages,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=expires_at,
        )

    async def get_by_user_and_channel(
        self, user_id: str, channel_id: str
    ) -> Conversation | None:
        """Get conversation by user_id and channel_id"""
        stmt = select(ConversationTable).where(
            ConversationTable.user_id == user_id,
            ConversationTable.channel_id == channel_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Deserialize messages from JSON
        messages_data = json.loads(model.messages)
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in messages_data
        ]

        # Calculate expires_at as created_at + 24 hours (default TTL)
        expires_at = model.created_at + timedelta(hours=24)

        return Conversation(
            id=model.conversation_id,
            user_id=model.user_id,
            channel_id=model.channel_id,
            messages=messages,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=expires_at,
        )

    async def delete(self, conversation_id: UUID) -> None:
        """Delete a conversation"""
        stmt = delete(ConversationTable).where(
            ConversationTable.conversation_id == conversation_id
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_expired(self) -> int:
        """Delete expired conversations (older than 24 hours)"""
        current_time = datetime.now(UTC)
        expiry_threshold = current_time - timedelta(hours=24)

        # Delete conversations where created_at is older than 24 hours
        stmt = delete(ConversationTable).where(
            ConversationTable.created_at <= expiry_threshold
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount  # type: ignore[no-any-return]
