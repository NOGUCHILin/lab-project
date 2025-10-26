"""Daily Summary Entity"""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DailySummary:
    """Daily summary of user's task activity"""

    id: UUID
    date: date
    user_id: str | None
    tasks_completed: int
    tasks_pending: int
    summary_text: str | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        summary_date: date,
        user_id: str | None,
        tasks_completed: int,
        tasks_pending: int,
        summary_text: str | None = None,
    ) -> "DailySummary":
        """Create a new daily summary

        Args:
            summary_date: Date of the summary
            user_id: User ID (None for team-wide summary)
            tasks_completed: Number of tasks completed
            tasks_pending: Number of tasks pending
            summary_text: Optional summary text

        Returns:
            DailySummary instance

        Raises:
            ValueError: If tasks_completed or tasks_pending is negative
        """
        if tasks_completed < 0:
            raise ValueError("tasks_completed cannot be negative")
        if tasks_pending < 0:
            raise ValueError("tasks_pending cannot be negative")

        return cls(
            id=uuid4(),
            date=summary_date,
            user_id=user_id,
            tasks_completed=tasks_completed,
            tasks_pending=tasks_pending,
            summary_text=summary_text,
            created_at=datetime.now(),
        )

    @property
    def total_tasks(self) -> int:
        """Calculate total number of tasks"""
        return self.tasks_completed + self.tasks_pending

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate (0.0 to 1.0)"""
        if self.total_tasks == 0:
            return 0.0
        return self.tasks_completed / self.total_tasks

    def is_team_summary(self) -> bool:
        """Check if this is a team-wide summary (not user-specific)"""
        return self.user_id is None
