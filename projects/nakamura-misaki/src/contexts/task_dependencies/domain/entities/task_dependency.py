"""
TaskDependency Entity

タスク間の依存関係を表すDomainエンティティ
Immutable（一度作成したら変更不可）
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from ..value_objects.dependency_type import DependencyType


@dataclass(frozen=True)
class TaskDependency:
    """タスク依存関係エンティティ

    Attributes:
        id: 依存関係ID
        blocking_task_id: ブロッキングタスクID（このタスクが完了しないと次に進めない）
        blocked_task_id: ブロックされたタスクID（前のタスクが完了するまで開始できない）
        dependency_type: 依存関係タイプ
        created_at: 作成日時
    """

    id: UUID
    blocking_task_id: UUID
    blocked_task_id: UUID
    dependency_type: DependencyType
    created_at: datetime

    @classmethod
    def create(
        cls,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
        dependency_type: DependencyType = DependencyType.BLOCKS,
    ) -> "TaskDependency":
        """新しいタスク依存関係を作成

        Args:
            blocking_task_id: ブロッキングタスクID
            blocked_task_id: ブロックされたタスクID
            dependency_type: 依存関係タイプ（デフォルト: BLOCKS）

        Returns:
            新しいTaskDependencyインスタンス

        Raises:
            ValueError: 自己依存の場合（blocking_task_id == blocked_task_id）
        """
        # バリデーション: 自己依存チェック
        if blocking_task_id == blocked_task_id:
            raise ValueError("Task cannot depend on itself")

        now = datetime.now(UTC).replace(tzinfo=None)

        return cls(
            id=uuid4(),
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=dependency_type,
            created_at=now,
        )

    @classmethod
    def reconstruct(
        cls,
        id: UUID,
        blocking_task_id: UUID,
        blocked_task_id: UUID,
        dependency_type: DependencyType,
        created_at: datetime,
    ) -> "TaskDependency":
        """DBから復元（Repositoryパターン用）

        Args:
            id: 依存関係ID
            blocking_task_id: ブロッキングタスクID
            blocked_task_id: ブロックされたタスクID
            dependency_type: 依存関係タイプ
            created_at: 作成日時

        Returns:
            復元されたTaskDependencyインスタンス
        """
        return cls(
            id=id,
            blocking_task_id=blocking_task_id,
            blocked_task_id=blocked_task_id,
            dependency_type=dependency_type,
            created_at=created_at,
        )

    def __eq__(self, other: object) -> bool:
        """等価性比較（IDベース）"""
        if not isinstance(other, TaskDependency):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """ハッシュ値（IDベース）"""
        return hash(self.id)

    def __str__(self) -> str:
        """文字列表現"""
        return (
            f"TaskDependency(id={str(self.id)[:8]}..., "
            f"blocking={str(self.blocking_task_id)[:8]}..., "
            f"blocked={str(self.blocked_task_id)[:8]}..., "
            f"type={self.dependency_type.value})"
        )
