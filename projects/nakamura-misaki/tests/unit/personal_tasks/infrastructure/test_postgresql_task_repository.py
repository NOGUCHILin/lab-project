"""Unit tests for PostgreSQL Task Repository"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.contexts.personal_tasks.domain.models.task import Task
from src.contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository,
    TaskModel,
)
from src.shared_kernel.domain.value_objects.task_status import TaskStatus


@pytest.fixture
async def engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(TaskModel.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncSession:
    """Create database session"""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def repository(session: AsyncSession) -> PostgreSQLTaskRepository:
    """Create repository instance"""
    return PostgreSQLTaskRepository(session=session)


@pytest.mark.asyncio
async def test_save_and_get_by_id(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test saving and retrieving a task"""
    task = Task.create(
        title="Test Task",
        assignee_user_id="U123",
        creator_user_id="U456",
        description="Test description"
    )

    await repository.save(task)
    await session.commit()

    retrieved = await repository.get_by_id(task.id)

    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == "Test Task"
    assert retrieved.assignee_user_id == "U123"
    assert retrieved.creator_user_id == "U456"
    assert retrieved.description == "Test description"
    assert retrieved.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository: PostgreSQLTaskRepository):
    """Test getting non-existent task returns None"""
    result = await repository.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_save_updates_existing_task(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test that save updates existing task"""
    task = Task.create("Original Title", "U123", "U123")
    await repository.save(task)
    await session.commit()

    # Update task
    task.update(title="Updated Title")
    await repository.save(task)
    await session.commit()

    retrieved = await repository.get_by_id(task.id)
    assert retrieved.title == "Updated Title"


@pytest.mark.asyncio
async def test_list_by_user(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test listing tasks by user"""
    task1 = Task.create("Task 1", "U123", "U123")
    task2 = Task.create("Task 2", "U123", "U123")
    task3 = Task.create("Task 3", "U456", "U456")

    await repository.save(task1)
    await repository.save(task2)
    await repository.save(task3)
    await session.commit()

    results = await repository.list_by_user("U123")

    assert len(results) == 2
    titles = {t.title for t in results}
    assert titles == {"Task 1", "Task 2"}


@pytest.mark.asyncio
async def test_list_by_user_with_status_filter(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test listing tasks by user with status filter"""
    task1 = Task.create("Task 1", "U123", "U123")
    task2 = Task.create("Task 2", "U123", "U123")
    task2.complete()

    await repository.save(task1)
    await repository.save(task2)
    await session.commit()

    results = await repository.list_by_user("U123", status=TaskStatus.PENDING)

    assert len(results) == 1
    assert results[0].title == "Task 1"
    assert results[0].status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_list_due_today(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test listing tasks due today"""
    today = datetime.now(UTC)
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    task_today = Task.create("Due Today", "U123", "U123", due_at=today)
    task_tomorrow = Task.create("Due Tomorrow", "U123", "U123", due_at=tomorrow)
    task_yesterday = Task.create("Due Yesterday", "U123", "U123", due_at=yesterday)

    await repository.save(task_today)
    await repository.save(task_tomorrow)
    await repository.save(task_yesterday)
    await session.commit()

    results = await repository.list_due_today("U123")

    assert len(results) == 1
    assert results[0].title == "Due Today"


@pytest.mark.asyncio
async def test_list_overdue(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test listing overdue tasks"""
    now = datetime.now(UTC)
    future = now + timedelta(days=1)
    past1 = now - timedelta(hours=1)
    past2 = now - timedelta(days=2)

    task_future = Task.create("Future", "U123", "U123", due_at=future)
    task_past1 = Task.create("Overdue 1", "U123", "U123", due_at=past1)
    task_past2 = Task.create("Overdue 2", "U123", "U123", due_at=past2)

    await repository.save(task_future)
    await repository.save(task_past1)
    await repository.save(task_past2)
    await session.commit()

    results = await repository.list_overdue("U123")

    assert len(results) == 2
    titles = {t.title for t in results}
    assert titles == {"Overdue 1", "Overdue 2"}


@pytest.mark.asyncio
async def test_delete(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test deleting a task"""
    task = Task.create("Test Task", "U123", "U123")
    await repository.save(task)
    await session.commit()

    await repository.delete(task.id)
    await session.commit()

    retrieved = await repository.get_by_id(task.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_completed_task_persistence(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test that completed task persists correctly"""
    task = Task.create("Test Task", "U123", "U123")
    task.complete()

    await repository.save(task)
    await session.commit()

    retrieved = await repository.get_by_id(task.id)

    assert retrieved.status == TaskStatus.COMPLETED
    assert retrieved.completed_at is not None


@pytest.mark.asyncio
async def test_task_with_due_date_persistence(
    repository: PostgreSQLTaskRepository,
    session: AsyncSession
):
    """Test that task with due date persists correctly"""
    due_date = datetime.now(UTC) + timedelta(days=7)
    task = Task.create("Test Task", "U123", "U123", due_at=due_date)

    await repository.save(task)
    await session.commit()

    retrieved = await repository.get_by_id(task.id)

    assert retrieved.due_at is not None
    # Compare dates (ignore microseconds and timezone - SQLite loses timezone info)
    assert retrieved.due_at.replace(microsecond=0, tzinfo=None) == due_date.replace(microsecond=0, tzinfo=None)
