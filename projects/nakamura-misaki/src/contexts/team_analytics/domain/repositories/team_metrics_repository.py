"""Team Metrics Repository Interface"""

from abc import ABC, abstractmethod
from datetime import date

from ..entities.team_metric import TeamMetric
from ..value_objects.metric_type import MetricType


class TeamMetricsRepository(ABC):
    """Repository interface for TeamMetric aggregate"""

    @abstractmethod
    async def save(self, team_metric: TeamMetric) -> None:
        """Save a team metric

        Args:
            team_metric: TeamMetric to save
        """
        pass

    @abstractmethod
    async def find_by_date_and_type(
        self,
        metric_date: date,
        metric_type: MetricType,
    ) -> list[TeamMetric]:
        """Find team metrics by date and type

        Args:
            metric_date: Date of the metric
            metric_type: Type of metric

        Returns:
            List of TeamMetric objects (may be multiple for same date/type)
        """
        pass

    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        metric_type: MetricType | None = None,
    ) -> list[TeamMetric]:
        """Find team metrics within a date range

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            metric_type: Optional metric type filter

        Returns:
            List of TeamMetric objects
        """
        pass

    @abstractmethod
    async def find_latest_by_type(self, metric_type: MetricType) -> TeamMetric | None:
        """Find the most recent metric of a specific type

        Args:
            metric_type: Type of metric

        Returns:
            Latest TeamMetric if found, None otherwise
        """
        pass
