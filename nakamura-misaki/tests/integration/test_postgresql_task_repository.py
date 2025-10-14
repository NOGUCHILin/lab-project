"""Integration tests for PostgreSQLTaskRepository"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.secondary.postgresql_task_repository import (
    PostgreSQLTaskRepository,
)
from src.domain.models.task import Task, TaskStatus
from src.infrastructure.database.schema import Base, TaskTable


@pytest.fixture
async def async_engine():
    """Create async engine for testing"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """Create async session for testing"""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
def repository(async_session):
    """Create repository instance"""
    return PostgreSQLTaskRepository(async_session)


@pytest.mark.asyncio
async def test_create_task(repository, async_session):
    """Test create task"""
    task = Task(
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.PENDING,
        due_at=datetime.now() + timedelta(days=1),
    )

    created_task = await repository.create(task)
    await async_session.commit()

    assert created_task.id == task.id
    assert created_task.title == "Test task"

    # Verify saved in database
    stmt = select(TaskTable).where(TaskTable.id == task.id)
    result = await async_session.execute(stmt)
    task_table = result.scalar_one_or_none()

    assert task_table is not None
    assert task_table.title == "Test task"
    assert task_table.status == TaskStatus.PENDING.value


@pytest.mark.asyncio
async def test_get_task(repository, async_session):
    """Test get task by ID"""
    task = Task(
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.PENDING,
    )

    await repository.create(task)
    await async_session.commit()

    retrieved_task = await repository.get(task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.title == "Test task"


@pytest.mark.asyncio
async def test_update_task(repository, async_session):
    """Test update task"""
    task = Task(
        user_id="user_456",
        title="Original title",
        description="Original description",
        status=TaskStatus.PENDING,
    )

    await repository.create(task)
    await async_session.commit()

    task.title = "Updated title"
    task.status = TaskStatus.IN_PROGRESS

    updated_task = await repository.update(task)
    await async_session.commit()

    assert updated_task.title == "Updated title"
    assert updated_task.status == TaskStatus.IN_PROGRESS

    # Verify updated in database
    retrieved_task = await repository.get(task.id)
    assert retrieved_task.title == "Updated title"
    assert retrieved_task.status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_task(repository, async_session):
    """Test delete task"""
    task = Task(
        user_id="user_456",
        title="Test task",
        description="Test description",
        status=TaskStatus.PENDING,
    )

    await repository.create(task)
    await async_session.commit()

    await repository.delete(task.id)
    await async_session.commit()

    # Verify deleted
    stmt = select(TaskTable).where(TaskTable.id == task.id)
    result = await async_session.execute(stmt)
    task_table = result.scalar_one_or_none()

    assert task_table is None


@pytest.mark.asyncio
async def test_list_by_user(repository, async_session):
    """Test list tasks by user"""
    task1 = Task(
        user_id="user_456",
        title="Task 1",
        status=TaskStatus.PENDING,
    )
    task2 = Task(
        user_id="user_456",
        title="Task 2",
        status=TaskStatus.IN_PROGRESS,
    )
    task3 = Task(
        user_id="user_999",
        title="Task 3",
        status=TaskStatus.PENDING,
    )

    await repository.create(task1)
    await repository.create(task2)
    await repository.create(task3)
    await async_session.commit()

    tasks = await repository.list_by_user("user_456")

    assert len(tasks) == 2
    assert all(t.user_id == "user_456" for t in tasks)


@pytest.mark.asyncio
async def test_list_by_user_with_status_filter(repository, async_session):
    """Test list tasks by user with status filter"""
    task1 = Task(
        user_id="user_456",
        title="Task 1",
        status=TaskStatus.PENDING,
    )
    task2 = Task(
        user_id="user_456",
        title="Task 2",
        status=TaskStatus.IN_PROGRESS,
    )
    task3 = Task(
        user_id="user_456",
        title="Task 3",
        status=TaskStatus.COMPLETED,
    )

    await repository.create(task1)
    await repository.create(task2)
    await repository.create(task3)
    await async_session.commit()

    pending_tasks = await repository.list_by_user("user_456", status="pending")

    assert len(pending_tasks) == 1
    assert pending_tasks[0].status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_list_due_today(repository, async_session):
    """Test list tasks due today"""
    today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    task1 = Task(
        user_id="user_456",
        title="Due today",
        status=TaskStatus.PENDING,
        due_at=today,
    )
    task2 = Task(
        user_id="user_456",
        title="Due tomorrow",
        status=TaskStatus.PENDING,
        due_at=tomorrow,
    )
    task3 = Task(
        user_id="user_456",
        title="Due yesterday",
        status=TaskStatus.PENDING,
        due_at=yesterday,
    )

    await repository.create(task1)
    await repository.create(task2)
    await repository.create(task3)
    await async_session.commit()

    tasks = await repository.list_due_today("user_456")

    assert len(tasks) == 1
    assert tasks[0].title == "Due today"


@pytest.mark.asyncio
async def test_list_overdue(repository, async_session):
    """Test list overdue tasks"""
    now = datetime.now()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    task1 = Task(
        user_id="user_456",
        title="Overdue task",
        status=TaskStatus.PENDING,
        due_at=past,
    )
    task2 = Task(
        user_id="user_456",
        title="Future task",
        status=TaskStatus.PENDING,
        due_at=future,
    )
    task3 = Task(
        user_id="user_456",
        title="Completed overdue",
        status=TaskStatus.COMPLETED,
        due_at=past,
    )

    await repository.create(task1)
    await repository.create(task2)
    await repository.create(task3)
    await async_session.commit()

    tasks = await repository.list_overdue("user_456")

    assert len(tasks) == 1
    assert tasks[0].title == "Overdue task"


@pytest.mark.asyncio
async def test_list_stale(repository, async_session):
    """Test list stale tasks"""
    now = datetime.now()
    old = now - timedelta(days=10)
    recent = now - timedelta(days=2)

    task1 = Task(
        user_id="user_456",
        title="Stale task",
        status=TaskStatus.IN_PROGRESS,
        created_at=old,
    )
    task2 = Task(
        user_id="user_456",
        title="Recent task",
        status=TaskStatus.IN_PROGRESS,
        created_at=recent,
    )
    task3 = Task(
        user_id="user_456",
        title="Stale but completed",
        status=TaskStatus.COMPLETED,
        created_at=old,
    )

    await repository.create(task1)
    await repository.create(task2)
    await repository.create(task3)
    await async_session.commit()

    tasks = await repository.list_stale("user_456", days=7)

    assert len(tasks) == 1
    assert tasks[0].title == "Stale task"
