"""Handoff repository interface"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from ..models.handoff import Handoff


class HandoffRepository(ABC):
    """ハンドオフリポジトリインターフェース"""

    @abstractmethod
    async def create(self, handoff: Handoff) -> Handoff:
        """ハンドオフを作成

        Args:
            handoff: 作成するHandoff

        Returns:
            作成されたHandoff
        """
        pass

    @abstractmethod
    async def get(self, handoff_id: UUID) -> Handoff | None:
        """ハンドオフIDで取得

        Args:
            handoff_id: ハンドオフID

        Returns:
            Handoff または None
        """
        pass

    @abstractmethod
    async def list_by_to_user(self, user_id: str) -> list[Handoff]:
        """引き継ぎ先ユーザーIDでハンドオフ一覧取得（未完了のみ）

        Args:
            user_id: ユーザーID

        Returns:
            Handoff一覧（引き継ぎ予定日時順）
        """
        pass

    @abstractmethod
    async def list_pending_reminders(self, before: datetime) -> list[Handoff]:
        """リマインダー送信対象のハンドオフ一覧取得

        Args:
            before: この日時より前の引き継ぎ予定（通常は現在時刻+10分）

        Returns:
            Handoff一覧（reminded_at IS NULL かつ未完了）
        """
        pass

    @abstractmethod
    async def mark_reminded(self, handoff_id: UUID) -> None:
        """リマインダー送信済みにする

        Args:
            handoff_id: ハンドオフID
        """
        pass

    @abstractmethod
    async def complete(self, handoff_id: UUID) -> Handoff:
        """ハンドオフを完了にする

        Args:
            handoff_id: ハンドオフID

        Returns:
            更新されたHandoff
        """
        pass

    @abstractmethod
    async def list_created_between(
        self, start: datetime, end: datetime
    ) -> list[Handoff]:
        """期間内に作成されたハンドオフ一覧取得（Phase 4用）

        Args:
            start: 開始日時
            end: 終了日時

        Returns:
            Handoff一覧
        """
        pass
