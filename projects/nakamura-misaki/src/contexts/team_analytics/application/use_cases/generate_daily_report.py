"""Generate Daily Report Use Case"""

from datetime import date

from ...domain.entities.daily_summary import DailySummary
from ...domain.repositories.daily_summary_repository import DailySummaryRepository
from ..dto.analytics_dto import DailySummaryDTO


class GenerateDailyReportUseCase:
    """Use case for generating a daily team report"""

    def __init__(self, daily_summary_repository: DailySummaryRepository):
        self._daily_summary_repo = daily_summary_repository

    async def execute(self, report_date: date, summary_text: str | None = None) -> DailySummaryDTO:
        """Generate or update daily team report

        Args:
            report_date: Date of the report
            summary_text: Optional summary text for the report

        Returns:
            DailySummaryDTO with the generated report
        """
        # Get all user summaries for the date to calculate team totals
        user_summaries = await self._daily_summary_repo.find_by_date_range(
            start_date=report_date,
            end_date=report_date,
        )

        # Filter user-specific summaries (exclude team-wide if it exists)
        user_summaries = [s for s in user_summaries if not s.is_team_summary()]

        # Calculate team totals
        total_completed = sum(s.tasks_completed for s in user_summaries)
        total_pending = sum(s.tasks_pending for s in user_summaries)

        # Check if team summary already exists
        existing_summary = await self._daily_summary_repo.find_team_summary_by_date(report_date)

        if existing_summary:
            # Update with new summary text if provided
            team_summary = DailySummary.create(
                date=report_date,
                user_id=None,  # Team-wide summary
                tasks_completed=total_completed,
                tasks_pending=total_pending,
                summary_text=summary_text or existing_summary.summary_text,
            )
        else:
            # Create new team summary
            team_summary = DailySummary.create(
                date=report_date,
                user_id=None,  # Team-wide summary
                tasks_completed=total_completed,
                tasks_pending=total_pending,
                summary_text=summary_text,
            )

        # Save the team summary
        await self._daily_summary_repo.save(team_summary)

        # Return DTO
        return DailySummaryDTO(
            id=team_summary.id,
            date=team_summary.date,
            user_id=team_summary.user_id,
            tasks_completed=team_summary.tasks_completed,
            tasks_pending=team_summary.tasks_pending,
            summary_text=team_summary.summary_text,
            completion_rate=team_summary.completion_rate,
        )
