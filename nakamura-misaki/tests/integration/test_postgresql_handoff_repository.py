"""Integration tests for PostgreSQLHandoffRepository"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.secondary.postgresql_handoff_repository import (
    PostgreSQLHandoffRepository,
)
from src.domain.models.handoff import Handoff
from src.infrastructure.database.schema import Base, HandoffTable


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
    return PostgreSQLHandoffRepository(async_session)


@pytest.mark.asyncio
async def test_create_handoff(repository, async_session):
    """Test create handoff"""
    handoff = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=datetime.now() + timedelta(hours=2),
    )

    created_handoff = await repository.create(handoff)
    await async_session.commit()

    assert created_handoff.id == handoff.id
    assert created_handoff.progress_note == "Task is 50% complete"

    # Verify saved in database
    stmt = select(HandoffTable).where(HandoffTable.id == handoff.id)
    result = await async_session.execute(stmt)
    handoff_table = result.scalar_one_or_none()

    assert handoff_table is not None
    assert handoff_table.from_user_id == "user_123"
    assert handoff_table.to_user_id == "user_456"


@pytest.mark.asyncio
async def test_get_handoff(repository, async_session):
    """Test get handoff by ID"""
    handoff = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Task is 50% complete",
        handoff_at=datetime.now() + timedelta(hours=2),
    )

    await repository.create(handoff)
    await async_session.commit()

    retrieved_handoff = await repository.get(handoff.id)

    assert retrieved_handoff is not None
    assert retrieved_handoff.id == handoff.id
    assert retrieved_handoff.progress_note == "Task is 50% complete"


@pytest.mark.asyncio
async def test_list_by_to_user(repository, async_session):
    """Test list handoffs by to_user_id"""
    handoff1 = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Handoff 1",
        handoff_at=datetime.now() + timedelta(hours=2),
    )
    handoff2 = Handoff(
        task_id=uuid4(),
        from_user_id="user_789",
        to_user_id="user_456",
        progress_note="Handoff 2",
        handoff_at=datetime.now() + timedelta(hours=3),
    )
    handoff3 = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_999",
        progress_note="Handoff 3",
        handoff_at=datetime.now() + timedelta(hours=4),
    )

    await repository.create(handoff1)
    await repository.create(handoff2)
    await repository.create(handoff3)
    await async_session.commit()

    handoffs = await repository.list_by_to_user("user_456")

    assert len(handoffs) == 2
    assert all(h.to_user_id == "user_456" for h in handoffs)


@pytest.mark.asyncio
async def test_list_by_to_user_excludes_completed(repository, async_session):
    """Test list_by_to_user excludes completed handoffs"""
    handoff1 = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Pending handoff",
        handoff_at=datetime.now() + timedelta(hours=2),
    )
    handoff2 = Handoff(
        task_id=uuid4(),
        from_user_id="user_789",
        to_user_id="user_456",
        progress_note="Completed handoff",
        handoff_at=datetime.now() + timedelta(hours=3),
        completed_at=datetime.now(),
    )

    await repository.create(handoff1)
    await repository.create(handoff2)
    await async_session.commit()

    handoffs = await repository.list_by_to_user("user_456")

    assert len(handoffs) == 1
    assert handoffs[0].progress_note == "Pending handoff"


@pytest.mark.asyncio
async def test_list_pending_reminders(repository, async_session):
    """Test list pending reminders"""
    now = datetime.now()
    past = now - timedelta(minutes=15)
    future = now + timedelta(minutes=15)

    handoff1 = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Needs reminder",
        handoff_at=past,
    )
    handoff2 = Handoff(
        task_id=uuid4(),
        from_user_id="user_789",
        to_user_id="user_456",
        progress_note="Future handoff",
        handoff_at=future,
    )
    handoff3 = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_999",
        progress_note="Already reminded",
        handoff_at=past,
        reminded_at=now,
    )

    await repository.create(handoff1)
    await repository.create(handoff2)
    await repository.create(handoff3)
    await async_session.commit()

    # Check reminders before now + 5 minutes
    check_time = now + timedelta(minutes=5)
    handoffs = await repository.list_pending_reminders(check_time)

    assert len(handoffs) == 1
    assert handoffs[0].progress_note == "Needs reminder"


@pytest.mark.asyncio
async def test_mark_reminded(repository, async_session):
    """Test mark reminded"""
    handoff = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Test handoff",
        handoff_at=datetime.now() + timedelta(hours=2),
    )

    await repository.create(handoff)
    await async_session.commit()

    assert handoff.reminded_at is None

    await repository.mark_reminded(handoff.id)
    await async_session.commit()

    # Verify reminded_at is set
    retrieved_handoff = await repository.get(handoff.id)
    assert retrieved_handoff.reminded_at is not None


@pytest.mark.asyncio
async def test_complete_handoff(repository, async_session):
    """Test complete handoff"""
    handoff = Handoff(
        task_id=uuid4(),
        from_user_id="user_123",
        to_user_id="user_456",
        progress_note="Test handoff",
        handoff_at=datetime.now() + timedelta(hours=2),
    )

    await repository.create(handoff)
    await async_session.commit()

    assert handoff.completed_at is None

    completed_handoff = await repository.complete(handoff.id)
    await async_session.commit()

    assert completed_handoff.completed_at is not None

    # Verify in database
    retrieved_handoff = await repository.get(handoff.id)
    assert retrieved_handoff.completed_at is not None


@pytest.mark.asyncio
async def test_complete_nonexistent_handoff(repository):
    """Test complete nonexistent handoff raises error"""
    nonexistent_id = uuid4()

    with pytest.raises(ValueError, match="Handoff not found"):
        await repository.complete(nonexistent_id)
