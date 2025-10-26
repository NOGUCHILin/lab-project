"""Get Team Workload Use Case"""

from datetime import date

from ...domain.repositories.daily_summary_repository import DailySummaryRepository
from ..dto.analytics_dto import TeamWorkloadDTO


class GetTeamWorkloadUseCase:
    """Use case for getting current team workload distribution"""

    def __init__(self, daily_summary_repository: DailySummaryRepository):
        self._daily_summary_repo = daily_summary_repository

    async def execute(self, workload_date: date | None = None) -> TeamWorkloadDTO:
        """Get team workload for a specific date

        Args:
            workload_date: Date to get workload for (default: today)

        Returns:
            TeamWorkloadDTO with team workload information
        """
        if workload_date is None:
            workload_date = date.today()

        # Get all user summaries for the date (exclude team-wide summaries)
        all_summaries = await self._daily_summary_repo.find_by_date_range(
            start_date=workload_date,
            end_date=workload_date,
        )

        # Filter for user-specific summaries only (not team-wide)
        user_summaries = [s for s in all_summaries if not s.is_team_summary()]

        # Calculate totals
        total_tasks = sum(s.total_tasks for s in user_summaries)
        total_completed = sum(s.tasks_completed for s in user_summaries)
        total_pending = sum(s.tasks_pending for s in user_summaries)

        # Calculate per-user workloads
        user_workloads: dict[str, int] = {}
        for summary in user_summaries:
            if summary.user_id:
                user_workloads[summary.user_id] = summary.total_tasks

        # Calculate average workload
        average_workload = total_tasks / len(user_workloads) if user_workloads else 0.0

        return TeamWorkloadDTO(
            date=workload_date,
            total_tasks=total_tasks,
            total_completed=total_completed,
            total_pending=total_pending,
            user_workloads=user_workloads,
            average_workload=average_workload,
        )
