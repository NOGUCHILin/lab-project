"""PostgreSQL implementation of TeamMetricsRepository"""

from datetime import date

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import TeamMetricTable

from ...domain.entities.team_metric import TeamMetric
from ...domain.repositories.team_metrics_repository import TeamMetricsRepository
from ...domain.value_objects.metric_type import MetricType


class PostgreSQLTeamMetricsRepository(TeamMetricsRepository):
    """PostgreSQL implementation of TeamMetricsRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, team_metric: TeamMetric) -> None:
        """Save a team metric"""
        table_obj = TeamMetricTable(
            id=team_metric.id,
            date=team_metric.date,
            metric_type=team_metric.metric_type.value,
            metric_value=team_metric.metric_value,
            metadata=team_metric.metadata,
            created_at=team_metric.created_at,
        )
        self._session.add(table_obj)
        await self._session.flush()

    async def find_by_date_and_type(
        self,
        metric_date: date,
        metric_type: MetricType,
    ) -> list[TeamMetric]:
        """Find team metrics by date and type"""
        stmt = select(TeamMetricTable).where(
            and_(
                TeamMetricTable.date == metric_date,
                TeamMetricTable.metric_type == metric_type.value,
            )
        )

        result = await self._session.execute(stmt)
        table_objs = result.scalars().all()

        return [self._to_entity(obj) for obj in table_objs]

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        metric_type: MetricType | None = None,
    ) -> list[TeamMetric]:
        """Find team metrics within a date range"""
        stmt = select(TeamMetricTable).where(
            and_(
                TeamMetricTable.date >= start_date,
                TeamMetricTable.date <= end_date,
            )
        )

        # Apply metric type filter if provided
        if metric_type is not None:
            stmt = stmt.where(TeamMetricTable.metric_type == metric_type.value)

        stmt = stmt.order_by(TeamMetricTable.date, TeamMetricTable.metric_type)

        result = await self._session.execute(stmt)
        table_objs = result.scalars().all()

        return [self._to_entity(obj) for obj in table_objs]

    async def find_latest_by_type(self, metric_type: MetricType) -> TeamMetric | None:
        """Find the most recent metric of a specific type"""
        stmt = (
            select(TeamMetricTable)
            .where(TeamMetricTable.metric_type == metric_type.value)
            .order_by(desc(TeamMetricTable.date), desc(TeamMetricTable.created_at))
            .limit(1)
        )

        result = await self._session.execute(stmt)
        table_obj = result.scalar_one_or_none()

        if table_obj is None:
            return None

        return self._to_entity(table_obj)

    def _to_entity(self, table_obj: TeamMetricTable) -> TeamMetric:
        """Convert table object to domain entity"""
        return TeamMetric(
            id=table_obj.id,
            date=table_obj.date,
            metric_type=MetricType.from_string(table_obj.metric_type),
            metric_value=table_obj.metric_value,
            metadata=table_obj.metadata,
            created_at=table_obj.created_at,
        )
