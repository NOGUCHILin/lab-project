"""PostgreSQL implementation of TaskRepository"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.task import Task, TaskStatus
from ...domain.repositories.task_repository import TaskRepository
from ...infrastructure.database.schema import TaskTable

if TYPE_CHECKING:
    pass


class PostgreSQLTaskRepository(TaskRepository):
    """PostgreSQL implementation of TaskRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, task: Task) -> Task:
        """タスクを作成"""
        task_table = TaskTable(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
        )

        self._session.add(task_table)
        await self._session.flush()

        return task

    async def get(self, task_id: UUID) -> Task | None:
        """タスクIDで取得"""
        stmt = select(TaskTable).where(TaskTable.id == task_id)
        result = await self._session.execute(stmt)
        task_table = result.scalar_one_or_none()

        if task_table is None:
            return None

        return self._map_to_entity(task_table)

    async def update(self, task: Task) -> Task:
        """タスクを更新"""
        stmt = select(TaskTable).where(TaskTable.id == task.id)
        result = await self._session.execute(stmt)
        task_table = result.scalar_one_or_none()

        if task_table is None:
            raise ValueError(f"Task not found: {task.id}")

        task_table.title = task.title
        task_table.description = task.description
        task_table.status = task.status.value
        task_table.due_at = task.due_at
        task_table.completed_at = task.completed_at

        await self._session.flush()

        return task

    async def delete(self, task_id: UUID) -> None:
        """タスクを削除"""
        stmt = select(TaskTable).where(TaskTable.id == task_id)
        result = await self._session.execute(stmt)
        task_table = result.scalar_one_or_none()

        if task_table:
            await self._session.delete(task_table)

    async def list_by_user(
        self, user_id: str, status: str | None = None, limit: int = 100
    ) -> list[Task]:
        """ユーザーIDでタスク一覧取得"""
        stmt = select(TaskTable).where(TaskTable.user_id == user_id)

        if status:
            stmt = stmt.where(TaskTable.status == status)

        stmt = stmt.order_by(TaskTable.created_at.desc()).limit(limit)

        result = await self._session.execute(stmt)
        task_tables = result.scalars().all()

        return [self._map_to_entity(tt) for tt in task_tables]

    async def list_due_today(self, user_id: str) -> list[Task]:
        """今日期限のタスク一覧取得"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        stmt = (
            select(TaskTable)
            .where(TaskTable.user_id == user_id)
            .where(TaskTable.due_at >= today_start)
            .where(TaskTable.due_at < today_end)
            .where(TaskTable.status != TaskStatus.COMPLETED.value)
            .order_by(TaskTable.due_at.asc())
        )

        result = await self._session.execute(stmt)
        task_tables = result.scalars().all()

        return [self._map_to_entity(tt) for tt in task_tables]

    async def list_all(self, status: TaskStatus | None = None) -> list[Task]:
        """全タスク一覧取得（Phase 4用）"""
        stmt = select(TaskTable)

        if status:
            stmt = stmt.where(TaskTable.status == status.value)

        stmt = stmt.order_by(TaskTable.created_at.desc())

        result = await self._session.execute(stmt)
        task_tables = result.scalars().all()

        return [self._map_to_entity(tt) for tt in task_tables]

    async def list_overdue(self) -> list[Task]:
        """期限切れタスク一覧取得（Phase 4用）"""
        now = datetime.now()

        stmt = (
            select(TaskTable)
            .where(TaskTable.due_at < now)
            .where(TaskTable.status != TaskStatus.COMPLETED.value)
            .where(TaskTable.status != TaskStatus.CANCELLED.value)
            .order_by(TaskTable.due_at.asc())
        )

        result = await self._session.execute(stmt)
        task_tables = result.scalars().all()

        return [self._map_to_entity(tt) for tt in task_tables]

    async def list_stale(self, days: int) -> list[Task]:
        """長期停滞タスク一覧取得（Phase 4用）"""
        cutoff_date = datetime.now() - timedelta(days=days)

        stmt = (
            select(TaskTable)
            .where(TaskTable.created_at < cutoff_date)
            .where(TaskTable.status == TaskStatus.IN_PROGRESS.value)
            .order_by(TaskTable.created_at.asc())
        )

        result = await self._session.execute(stmt)
        task_tables = result.scalars().all()

        return [self._map_to_entity(tt) for tt in task_tables]

    async def list_created_between(
        self, start: datetime, end: datetime
    ) -> list[Task]:
        """期間内に作成されたタスク一覧取得（Phase 4用）"""
        stmt = (
            select(TaskTable)
            .where(TaskTable.created_at >= start)
            .where(TaskTable.created_at < end)
            .order_by(TaskTable.created_at.desc())
        )

        result = await self._session.execute(stmt)
        task_tables = result.scalars().all()

        return [self._map_to_entity(tt) for tt in task_tables]

    def _map_to_entity(self, task_table: TaskTable) -> Task:
        """TableモデルからDomainモデルに変換"""
        return Task(
            id=task_table.id,
            user_id=task_table.user_id,
            title=task_table.title,
            description=task_table.description,
            status=TaskStatus(task_table.status),
            due_at=task_table.due_at,
            completed_at=task_table.completed_at,
            created_at=task_table.created_at,
        )
