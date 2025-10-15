"""Conversation repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models.conversation import Conversation


class ConversationRepository(ABC):
    """会話履歴リポジトリインターフェース.

    会話履歴の永続化・取得を管理します。
    """

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        """会話履歴を保存（新規作成または更新）.

        Args:
            conversation: 保存するConversation

        Returns:
            保存されたConversation
        """
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """会話IDで取得.

        Args:
            conversation_id: 会話ID

        Returns:
            Conversation または None
        """
        pass

    @abstractmethod
    async def get_by_user_and_channel(
        self, user_id: str, channel_id: str
    ) -> Conversation | None:
        """ユーザーIDとチャンネルIDで最新の会話を取得.

        Args:
            user_id: ユーザーID
            channel_id: チャンネルID

        Returns:
            Conversation または None（存在しないまたは期限切れの場合）
        """
        pass

    @abstractmethod
    async def delete(self, conversation_id: UUID) -> None:
        """会話履歴を削除.

        Args:
            conversation_id: 会話ID
        """
        pass

    @abstractmethod
    async def delete_expired(self, ttl_hours: int) -> int:
        """期限切れの会話履歴を削除.

        Args:
            ttl_hours: TTL（時間）

        Returns:
            削除された会話数
        """
        pass
