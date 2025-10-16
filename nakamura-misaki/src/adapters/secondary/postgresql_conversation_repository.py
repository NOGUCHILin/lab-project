"""PostgreSQL implementation of ConversationRepository."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.conversation import Conversation, Message, MessageRole
from ...domain.repositories.conversation_repository import ConversationRepository
from ...infrastructure.database.schema import ConversationTable


class PostgreSQLConversationRepository(ConversationRepository):
    """PostgreSQL implementation of ConversationRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, conversation: Conversation) -> Conversation:
        """会話履歴を保存（新規作成または更新）."""
        # Check if exists
        stmt = select(ConversationTable).where(
            ConversationTable.conversation_id == conversation.conversation_id
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.messages = [msg.to_dict() for msg in conversation.messages]
            existing.updated_at = conversation.updated_at
            existing.last_message_at = conversation.last_message_at
        else:
            # Create new
            conversation_table = ConversationTable(
                conversation_id=conversation.conversation_id,
                user_id=conversation.user_id,
                channel_id=conversation.channel_id,
                messages=[msg.to_dict() for msg in conversation.messages],
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                last_message_at=conversation.last_message_at,
            )
            self._session.add(conversation_table)

        await self._session.flush()
        return conversation

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """会話IDで取得."""
        stmt = select(ConversationTable).where(
            ConversationTable.conversation_id == conversation_id
        )
        result = await self._session.execute(stmt)
        conversation_table = result.scalar_one_or_none()

        if conversation_table is None:
            return None

        return self._map_to_entity(conversation_table)

    async def get_by_user_and_channel(
        self, user_id: str, channel_id: str
    ) -> Conversation | None:
        """ユーザーIDとチャンネルIDで最新の会話を取得."""
        stmt = (
            select(ConversationTable)
            .where(ConversationTable.user_id == user_id)
            .where(ConversationTable.channel_id == channel_id)
            .order_by(ConversationTable.last_message_at.desc())
        )
        result = await self._session.execute(stmt)
        conversation_table = result.scalar_one_or_none()

        if conversation_table is None:
            return None

        return self._map_to_entity(conversation_table)

    async def delete(self, conversation_id: UUID) -> None:
        """会話履歴を削除."""
        stmt = delete(ConversationTable).where(
            ConversationTable.conversation_id == conversation_id
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_expired(self, ttl_hours: int) -> int:
        """期限切れの会話履歴を削除."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=ttl_hours)

        stmt = delete(ConversationTable).where(
            ConversationTable.last_message_at < cutoff_time
        )
        result = await self._session.execute(stmt)
        await self._session.flush()

        return result.rowcount  # type: ignore

    def _map_to_entity(self, conversation_table: ConversationTable) -> Conversation:
        """Map ConversationTable to Conversation entity."""
        messages = [
            Message(
                role=MessageRole(msg["role"]),
                content=msg["content"],
            )
            for msg in conversation_table.messages
        ]

        return Conversation(
            conversation_id=conversation_table.conversation_id,
            user_id=conversation_table.user_id,
            channel_id=conversation_table.channel_id,
            messages=messages,
            created_at=conversation_table.created_at,
            updated_at=conversation_table.updated_at,
            last_message_at=conversation_table.last_message_at,
        )
