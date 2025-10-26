"""Detect Bottleneck Use Case"""

from datetime import date

from ...domain.repositories.daily_summary_repository import DailySummaryRepository
from ..dto.analytics_dto import BottleneckResultDTO


class DetectBottleneckUseCase:
    """Use case for detecting bottlenecks in team workflow"""

    def __init__(
        self,
        daily_summary_repository: DailySummaryRepository,
        workload_threshold: int = 10,
    ):
        """Initialize use case

        Args:
            daily_summary_repository: Repository for daily summaries
            workload_threshold: Number of pending tasks to consider a bottleneck (default: 10)
        """
        self._daily_summary_repo = daily_summary_repository
        self._workload_threshold = workload_threshold

    async def execute(self, check_date: date | None = None) -> BottleneckResultDTO:
        """Detect users with excessive workload (bottlenecks)

        Args:
            check_date: Date to check for bottlenecks (default: today)

        Returns:
            BottleneckResultDTO with detection results
        """
        if check_date is None:
            check_date = date.today()

        # Get all user summaries for the date
        all_summaries = await self._daily_summary_repo.find_by_date_range(
            start_date=check_date,
            end_date=check_date,
        )

        # Filter for user-specific summaries with high pending task count
        bottleneck_users: list[str] = []
        for summary in all_summaries:
            if not summary.is_team_summary() and summary.tasks_pending >= self._workload_threshold:
                if summary.user_id:
                    bottleneck_users.append(summary.user_id)

        # Determine if bottlenecks were detected
        detected = len(bottleneck_users) > 0

        # Generate message
        if detected:
            user_list = ", ".join(bottleneck_users)
            message = f"Detected {len(bottleneck_users)} user(s) with {self._workload_threshold}+ pending tasks: {user_list}"
        else:
            message = f"No bottlenecks detected (threshold: {self._workload_threshold} pending tasks)"

        return BottleneckResultDTO(
            detected=detected,
            bottleneck_users=bottleneck_users,
            message=message,
            workload_threshold=self._workload_threshold,
        )
