"""PostgreSQL implementation of HandoffRepository"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.handoff import Handoff
from ...domain.repositories.handoff_repository import HandoffRepository
from ...infrastructure.database.schema import HandoffTable

if TYPE_CHECKING:
    pass


class PostgreSQLHandoffRepository(HandoffRepository):
    """PostgreSQL implementation of HandoffRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, handoff: Handoff) -> Handoff:
        """ハンドオフを作成"""
        handoff_table = HandoffTable(
            id=handoff.id,
            task_id=handoff.task_id,
            from_user_id=handoff.from_user_id,
            to_user_id=handoff.to_user_id,
            progress_note=handoff.progress_note,
            handoff_at=handoff.handoff_at,
            reminded_at=handoff.reminded_at,
            completed_at=handoff.completed_at,
            created_at=handoff.created_at,
        )

        self._session.add(handoff_table)
        await self._session.flush()

        return handoff

    async def get(self, handoff_id: UUID) -> Handoff | None:
        """ハンドオフIDで取得"""
        stmt = select(HandoffTable).where(HandoffTable.id == handoff_id)
        result = await self._session.execute(stmt)
        handoff_table = result.scalar_one_or_none()

        if handoff_table is None:
            return None

        return self._map_to_entity(handoff_table)

    async def list_by_to_user(self, user_id: str) -> list[Handoff]:
        """引き継ぎ先ユーザーIDでハンドオフ一覧取得（保留中のみ）"""
        stmt = (
            select(HandoffTable)
            .where(HandoffTable.to_user_id == user_id)
            .where(HandoffTable.completed_at.is_(None))
            .order_by(HandoffTable.handoff_at.asc())
        )

        result = await self._session.execute(stmt)
        handoff_tables = result.scalars().all()

        return [self._map_to_entity(ht) for ht in handoff_tables]

    async def list_pending_reminders(self, before: datetime) -> list[Handoff]:
        """リマインダー送信が必要なハンドオフ一覧取得"""
        stmt = (
            select(HandoffTable)
            .where(HandoffTable.handoff_at <= before)
            .where(HandoffTable.reminded_at.is_(None))
            .where(HandoffTable.completed_at.is_(None))
            .order_by(HandoffTable.handoff_at.asc())
        )

        result = await self._session.execute(stmt)
        handoff_tables = result.scalars().all()

        return [self._map_to_entity(ht) for ht in handoff_tables]

    async def mark_reminded(self, handoff_id: UUID) -> None:
        """リマインダー送信済みとしてマーク"""
        stmt = select(HandoffTable).where(HandoffTable.id == handoff_id)
        result = await self._session.execute(stmt)
        handoff_table = result.scalar_one_or_none()

        if handoff_table:
            handoff_table.reminded_at = datetime.now()
            await self._session.flush()

    async def complete(self, handoff_id: UUID) -> Handoff:
        """ハンドオフを完了"""
        stmt = select(HandoffTable).where(HandoffTable.id == handoff_id)
        result = await self._session.execute(stmt)
        handoff_table = result.scalar_one_or_none()

        if handoff_table is None:
            raise ValueError(f"Handoff not found: {handoff_id}")

        handoff_table.completed_at = datetime.now()
        await self._session.flush()

        return self._map_to_entity(handoff_table)

    async def list_created_between(
        self, start: datetime, end: datetime
    ) -> list[Handoff]:
        """期間内に作成されたハンドオフ一覧取得（Phase 4用）"""
        stmt = (
            select(HandoffTable)
            .where(HandoffTable.created_at >= start)
            .where(HandoffTable.created_at < end)
            .order_by(HandoffTable.created_at.desc())
        )

        result = await self._session.execute(stmt)
        handoff_tables = result.scalars().all()

        return [self._map_to_entity(ht) for ht in handoff_tables]

    def _map_to_entity(self, handoff_table: HandoffTable) -> Handoff:
        """TableモデルからDomainモデルに変換"""
        return Handoff(
            id=handoff_table.id,
            task_id=handoff_table.task_id,
            from_user_id=handoff_table.from_user_id,
            to_user_id=handoff_table.to_user_id,
            progress_note=handoff_table.progress_note,
            handoff_at=handoff_table.handoff_at,
            reminded_at=handoff_table.reminded_at,
            completed_at=handoff_table.completed_at,
            created_at=handoff_table.created_at,
        )
