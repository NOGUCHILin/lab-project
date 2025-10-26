"""Get User Statistics Use Case"""

from datetime import date, timedelta

from ...domain.repositories.daily_summary_repository import DailySummaryRepository
from ..dto.analytics_dto import DailySummaryDTO, UserStatisticsDTO


class GetUserStatisticsUseCase:
    """Use case for getting user task statistics"""

    def __init__(self, daily_summary_repository: DailySummaryRepository):
        self._daily_summary_repo = daily_summary_repository

    async def execute(self, user_id: str, days: int = 30) -> UserStatisticsDTO:
        """Get user statistics for the last N days

        Args:
            user_id: User ID to get statistics for
            days: Number of days to include (default 30)

        Returns:
            UserStatisticsDTO with aggregated user statistics

        Raises:
            ValueError: If days is not positive
        """
        if days <= 0:
            raise ValueError("days must be positive")

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        # Get user's daily summaries
        summaries = await self._daily_summary_repo.find_by_date_range(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
        )

        # Calculate totals
        total_completed = sum(s.tasks_completed for s in summaries)
        total_pending = sum(s.tasks_pending for s in summaries)
        total_tasks = total_completed + total_pending

        # Calculate completion rate
        completion_rate = total_completed / total_tasks if total_tasks > 0 else 0.0

        # Convert summaries to DTOs
        summary_dtos = [
            DailySummaryDTO(
                id=s.id,
                date=s.date,
                user_id=s.user_id,
                tasks_completed=s.tasks_completed,
                tasks_pending=s.tasks_pending,
                summary_text=s.summary_text,
                completion_rate=s.completion_rate,
            )
            for s in summaries
        ]

        return UserStatisticsDTO(
            user_id=user_id,
            total_completed=total_completed,
            total_pending=total_pending,
            completion_rate=completion_rate,
            daily_summaries=sorted(summary_dtos, key=lambda x: x.date),
        )
