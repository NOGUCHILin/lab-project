"""Note repository interface"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..models.note import Note


class NoteRepository(ABC):
    """ノートリポジトリインターフェース"""

    @abstractmethod
    async def save(self, note: Note) -> Note:
        """ノートを保存（embedding自動生成）

        Args:
            note: 保存するNote

        Returns:
            保存されたNote（embeddingが追加される）
        """
        pass

    @abstractmethod
    async def search(self, query: str, user_id: str, limit: int = 10) -> list[Note]:
        """ノートを意味検索（Vector Search）

        Args:
            query: 検索クエリ
            user_id: ユーザーID
            limit: 取得件数上限

        Returns:
            類似度順のNote一覧
        """
        pass

    @abstractmethod
    async def list_by_session(self, session_id: str) -> list[Note]:
        """セッションIDでノート一覧取得

        Args:
            session_id: セッションID

        Returns:
            Note一覧（作成日時昇順）
        """
        pass

    @abstractmethod
    async def list_by_user(self, user_id: str, limit: int = 100) -> list[Note]:
        """ユーザーIDでノート一覧取得

        Args:
            user_id: ユーザーID
            limit: 取得件数上限

        Returns:
            Note一覧（作成日時降順）
        """
        pass

    @abstractmethod
    async def get(self, note_id: UUID) -> Note | None:
        """ノートIDで取得

        Args:
            note_id: ノートID

        Returns:
            Note または None
        """
        pass

    @abstractmethod
    async def delete(self, note_id: UUID) -> None:
        """ノートを削除

        Args:
            note_id: ノートID
        """
        pass
