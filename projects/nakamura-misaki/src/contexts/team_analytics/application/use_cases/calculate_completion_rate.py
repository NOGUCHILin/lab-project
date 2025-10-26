"""Calculate Completion Rate Use Case"""

from datetime import date

from ...domain.repositories.daily_summary_repository import DailySummaryRepository
from ..dto.analytics_dto import CompletionRateDTO


class CalculateCompletionRateUseCase:
    """Use case for calculating team completion rate over a date range"""

    def __init__(self, daily_summary_repository: DailySummaryRepository):
        self._daily_summary_repo = daily_summary_repository

    async def execute(self, start_date: date, end_date: date, user_id: str | None = None) -> CompletionRateDTO:
        """Calculate completion rate for a date range

        Args:
            start_date: Start date of the period
            end_date: End date of the period
            user_id: Optional user ID filter (None for team-wide)

        Returns:
            CompletionRateDTO with aggregated statistics

        Raises:
            ValueError: If start_date is after end_date
        """
        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        # Get all daily summaries in the date range
        summaries = await self._daily_summary_repo.find_by_date_range(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
        )

        # Calculate totals
        total_completed = sum(s.tasks_completed for s in summaries)
        total_pending = sum(s.tasks_pending for s in summaries)
        total_tasks = total_completed + total_pending

        # Calculate overall completion rate
        completion_rate = total_completed / total_tasks if total_tasks > 0 else 0.0

        # Calculate daily rates
        daily_rates: list[tuple[date, float]] = []
        for summary in summaries:
            daily_total = summary.tasks_completed + summary.tasks_pending
            daily_rate = summary.tasks_completed / daily_total if daily_total > 0 else 0.0
            daily_rates.append((summary.date, daily_rate))

        return CompletionRateDTO(
            start_date=start_date,
            end_date=end_date,
            total_completed=total_completed,
            total_pending=total_pending,
            completion_rate=completion_rate,
            daily_rates=sorted(daily_rates, key=lambda x: x[0]),
        )
