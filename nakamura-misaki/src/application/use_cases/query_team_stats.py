"""QueryTeamStatsUseCase - チーム統計取得"""


from src.domain.models.team_stats import TeamStats
from src.domain.repositories.task_repository import TaskRepository


class QueryTeamStatsUseCase:
    """チーム統計取得ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, days: int = 7) -> TeamStats:
        """チーム統計を取得

        Args:
            days: 何日間の統計を取得するか（デフォルト: 7日）
        """
        # TODO: 統計データの取得実装
        # 暫定的にダミーデータ返却
        return TeamStats(
            total_tasks=0,
            completed_tasks=0,
            in_progress_tasks=0,
            overdue_tasks=0,
            completion_rate=0.0,
            member_task_counts={},
            member_completion_counts={},
        )
