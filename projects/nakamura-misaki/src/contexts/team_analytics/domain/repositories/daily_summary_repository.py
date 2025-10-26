"""Daily Summary Repository Interface"""

from abc import ABC, abstractmethod
from datetime import date

from ..entities.daily_summary import DailySummary


class DailySummaryRepository(ABC):
    """Repository interface for DailySummary aggregate"""

    @abstractmethod
    async def save(self, daily_summary: DailySummary) -> None:
        """Save or update a daily summary

        Args:
            daily_summary: DailySummary to save
        """
        pass

    @abstractmethod
    async def find_by_date_and_user(self, summary_date: date, user_id: str | None) -> DailySummary | None:
        """Find daily summary by date and user

        Args:
            summary_date: Date of the summary
            user_id: User ID (None for team-wide summary)

        Returns:
            DailySummary if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        user_id: str | None = None,
    ) -> list[DailySummary]:
        """Find daily summaries within a date range

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            user_id: Optional user ID filter (None for team-wide summaries)

        Returns:
            List of DailySummary objects
        """
        pass

    @abstractmethod
    async def find_team_summary_by_date(self, summary_date: date) -> DailySummary | None:
        """Find team-wide summary for a specific date

        Args:
            summary_date: Date of the summary

        Returns:
            Team-wide DailySummary if found, None otherwise
        """
        pass
