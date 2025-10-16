"""DetectBottleneckUseCase - ボトルネック検出"""

from src.domain.models.bottleneck import Bottleneck
from src.domain.repositories.task_repository import TaskRepository


class DetectBottleneckUseCase:
    """ボトルネック検出ユースケース"""

    TASK_CONCENTRATION_THRESHOLD = 5  # タスク集中しきい値
    OVERDUE_THRESHOLD = 3  # 期限切れしきい値
    STALE_THRESHOLD = 2  # 放置しきい値

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self) -> list[Bottleneck]:
        """ボトルネックを検出"""
        bottlenecks = []

        # タスク集中検出
        task_concentration = await self._detect_task_concentration()
        bottlenecks.extend(task_concentration)

        # 期限切れタスク検出
        overdue_bottlenecks = await self._detect_overdue_tasks()
        bottlenecks.extend(overdue_bottlenecks)

        # 放置タスク検出
        stale_bottlenecks = await self._detect_stale_tasks()
        bottlenecks.extend(stale_bottlenecks)

        return bottlenecks

    async def _detect_task_concentration(self) -> list[Bottleneck]:
        """タスク集中検出"""
        # TODO: ユーザー別タスク数カウント実装
        # 暫定的に空リスト返却
        return []

    async def _detect_overdue_tasks(self) -> list[Bottleneck]:
        """期限切れタスク検出"""
        # TODO: 各ユーザーの期限切れタスク数カウント
        # 暫定的に空リスト返却
        return []

    async def _detect_stale_tasks(self) -> list[Bottleneck]:
        """放置タスク検出"""
        # TODO: 各ユーザーの放置タスク数カウント
        # 暫定的に空リスト返却
        return []
