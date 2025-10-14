"""Task repository interface"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from ..models.task import Task, TaskStatus


class TaskRepository(ABC):
    """タスクリポジトリインターフェース"""

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """タスクを作成

        Args:
            task: 作成するTask

        Returns:
            作成されたTask
        """
        pass

    @abstractmethod
    async def get(self, task_id: UUID) -> Task | None:
        """タスクIDで取得

        Args:
            task_id: タスクID

        Returns:
            Task または None
        """
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """タスクを更新

        Args:
            task: 更新するTask

        Returns:
            更新されたTask
        """
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> None:
        """タスクを削除

        Args:
            task_id: タスクID
        """
        pass

    @abstractmethod
    async def list_by_user(
        self, user_id: str, status: TaskStatus | None = None
    ) -> list[Task]:
        """ユーザーIDでタスク一覧取得

        Args:
            user_id: ユーザーID
            status: フィルタリングするステータス（None = 全て）

        Returns:
            Task一覧（期限順）
        """
        pass

    @abstractmethod
    async def list_due_today(self, user_id: str) -> list[Task]:
        """今日が期限のタスク一覧取得

        Args:
            user_id: ユーザーID

        Returns:
            Task一覧（期限順）
        """
        pass

    @abstractmethod
    async def list_all(self, status: TaskStatus | None = None) -> list[Task]:
        """全タスク一覧取得（Phase 4用）

        Args:
            status: フィルタリングするステータス（None = 全て）

        Returns:
            Task一覧
        """
        pass

    @abstractmethod
    async def list_overdue(self) -> list[Task]:
        """期限切れタスク一覧取得（Phase 4用）

        Returns:
            Task一覧
        """
        pass

    @abstractmethod
    async def list_stale(self, days: int) -> list[Task]:
        """長期停滞タスク一覧取得（Phase 4用）

        Args:
            days: 更新されていない日数

        Returns:
            Task一覧
        """
        pass

    @abstractmethod
    async def list_created_between(
        self, start: datetime, end: datetime
    ) -> list[Task]:
        """期間内に作成されたタスク一覧取得（Phase 4用）

        Args:
            start: 開始日時
            end: 終了日時

        Returns:
            Task一覧
        """
        pass
