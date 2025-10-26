"""PostgreSQL implementation of DailySummaryRepository"""

from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import DailySummaryTable

from ...domain.entities.daily_summary import DailySummary
from ...domain.repositories.daily_summary_repository import DailySummaryRepository


class PostgreSQLDailySummaryRepository(DailySummaryRepository):
    """PostgreSQL implementation of DailySummaryRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, daily_summary: DailySummary) -> None:
        """Save or update a daily summary"""
        # Check if summary already exists
        existing = await self._session.get(DailySummaryTable, daily_summary.id)

        if existing:
            # Update existing
            existing.date = daily_summary.date
            existing.user_id = daily_summary.user_id
            existing.tasks_completed = daily_summary.tasks_completed
            existing.tasks_pending = daily_summary.tasks_pending
            existing.summary_text = daily_summary.summary_text
        else:
            # Insert new
            table_obj = DailySummaryTable(
                id=daily_summary.id,
                date=daily_summary.date,
                user_id=daily_summary.user_id,
                tasks_completed=daily_summary.tasks_completed,
                tasks_pending=daily_summary.tasks_pending,
                summary_text=daily_summary.summary_text,
                created_at=daily_summary.created_at,
            )
            self._session.add(table_obj)

        await self._session.flush()

    async def find_by_date_and_user(self, summary_date: date, user_id: str | None) -> DailySummary | None:
        """Find daily summary by date and user"""
        stmt = select(DailySummaryTable).where(
            and_(
                DailySummaryTable.date == summary_date,
                DailySummaryTable.user_id == user_id,
            )
        )
        result = await self._session.execute(stmt)
        table_obj = result.scalar_one_or_none()

        if table_obj is None:
            return None

        return self._to_entity(table_obj)

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        user_id: str | None = None,
    ) -> list[DailySummary]:
        """Find daily summaries within a date range"""
        stmt = select(DailySummaryTable).where(
            and_(
                DailySummaryTable.date >= start_date,
                DailySummaryTable.date <= end_date,
            )
        )

        # Apply user filter if provided
        if user_id is not None:
            stmt = stmt.where(DailySummaryTable.user_id == user_id)

        stmt = stmt.order_by(DailySummaryTable.date)

        result = await self._session.execute(stmt)
        table_objs = result.scalars().all()

        return [self._to_entity(obj) for obj in table_objs]

    async def find_team_summary_by_date(self, summary_date: date) -> DailySummary | None:
        """Find team-wide summary for a specific date"""
        return await self.find_by_date_and_user(summary_date, user_id=None)

    def _to_entity(self, table_obj: DailySummaryTable) -> DailySummary:
        """Convert table object to domain entity"""
        return DailySummary(
            id=table_obj.id,
            date=table_obj.date,
            user_id=table_obj.user_id,
            tasks_completed=table_obj.tasks_completed,
            tasks_pending=table_obj.tasks_pending,
            summary_text=table_obj.summary_text,
            created_at=table_obj.created_at,
        )
