"""Team statistics model"""

from dataclasses import dataclass


@dataclass
class TeamStats:
    """チーム統計"""

    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    completion_rate: float
    member_task_counts: dict[str, int]
    member_completion_counts: dict[str, int]

    def __post_init__(self):
        """完了率を計算"""
        if self.total_tasks > 0:
            self.completion_rate = self.completed_tasks / self.total_tasks
        else:
            self.completion_rate = 0.0
