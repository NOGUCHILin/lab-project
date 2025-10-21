"""ConversationManager domain service.

Manages conversation sessions with TTL-based expiration.
Handles conversation lifecycle: creation, message addition, history retrieval.
"""

from uuid import uuid4

from ..models.conversation import Conversation, Message
from ..repositories.conversation_repository import ConversationRepository


class ConversationManager:
    """会話セッション管理ドメインサービス.

    責務:
    - 会話の取得または新規作成
    - メッセージ追加
    - 会話履歴取得（Claude API形式）
    - 期限切れ会話のクリーンアップ
    """

    def __init__(self, repository: ConversationRepository, ttl_hours: int = 24):
        """Initialize ConversationManager.

        Args:
            repository: ConversationRepository implementation
            ttl_hours: Time-to-live for conversations in hours (default: 24)
        """
        self._repository = repository
        self._ttl_hours = ttl_hours

    async def get_or_create(
        self, user_id: str, channel_id: str, initial_message: str | None = None
    ) -> Conversation:
        """会話を取得または新規作成.

        既存の会話が期限内であればそれを返し、
        期限切れまたは存在しない場合は新規作成する。

        Args:
            user_id: ユーザーID
            channel_id: チャンネルID
            initial_message: 初回メッセージ（新規作成時のみ使用、Noneの場合は空で作成）

        Returns:
            Conversation: 取得または作成された会話
        """
        # Try to get existing conversation
        existing = await self._repository.get_by_user_and_channel(user_id, channel_id)

        if existing and not existing.is_expired(self._ttl_hours):
            return existing

        # Create new conversation
        messages = []
        if initial_message:
            messages = [Message.user(content=initial_message)]

        conversation = Conversation(
            conversation_id=uuid4(),
            user_id=user_id,
            channel_id=channel_id,
            messages=messages,
        )

        await self._repository.save(conversation)
        return conversation

    async def add_user_message(
        self, user_id: str, channel_id: str, message: str
    ) -> None:
        """ユーザーメッセージを追加.

        Args:
            user_id: ユーザーID
            channel_id: チャンネルID
            message: メッセージ内容
        """
        conversation = await self._repository.get_by_user_and_channel(
            user_id, channel_id
        )

        if not conversation:
            raise ValueError(
                f"No conversation found for user_id={user_id}, channel_id={channel_id}"
            )

        conversation.add_message(Message.user(content=message))
        await self._repository.save(conversation)

    async def add_assistant_message(
        self, user_id: str, channel_id: str, message: str
    ) -> None:
        """アシスタントメッセージを追加.

        Args:
            user_id: ユーザーID
            channel_id: チャンネルID
            message: メッセージ内容
        """
        conversation = await self._repository.get_by_user_and_channel(
            user_id, channel_id
        )

        if not conversation:
            raise ValueError(
                f"No conversation found for user_id={user_id}, channel_id={channel_id}"
            )

        conversation.add_message(Message.assistant(content=message))
        await self._repository.save(conversation)

    async def get_conversation_history(
        self, user_id: str, channel_id: str
    ) -> list[dict[str, str]]:
        """会話履歴を取得（Claude API形式）.

        Args:
            user_id: ユーザーID
            channel_id: チャンネルID

        Returns:
            list[dict]: Claude Messages API形式のメッセージ一覧
                [{"role": "user"|"assistant", "content": "..."}]
        """
        conversation = await self._repository.get_by_user_and_channel(
            user_id, channel_id
        )

        if not conversation:
            return []

        return conversation.get_messages_for_claude_api()

    async def save(self, conversation: Conversation) -> Conversation:
        """会話を保存.

        Args:
            conversation: 保存する会話

        Returns:
            Conversation: 保存された会話
        """
        return await self._repository.save(conversation)

    async def cleanup_expired(self) -> int:
        """期限切れの会話を削除.

        Returns:
            int: 削除された会話の数
        """
        return await self._repository.delete_expired(ttl_hours=self._ttl_hours)
