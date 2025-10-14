"""Integration tests for PostgreSQLNoteRepository"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.secondary.postgresql_note_repository import (
    PostgreSQLNoteRepository,
)
from src.domain.models.note import Note
from src.infrastructure.database.schema import Base, NoteTable


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
def mock_claude_client():
    """Mock Claude client"""
    client = Mock()
    return client


@pytest.fixture
def repository(async_session, mock_claude_client):
    """Create repository instance"""
    return PostgreSQLNoteRepository(async_session, mock_claude_client)


@pytest.mark.asyncio
async def test_save_note(repository, async_session):
    """Test save note"""
    # Mock embedding generation
    repository._generate_embedding = AsyncMock(return_value=[0.1] * 1024)

    note = Note(
        session_id="session_123",
        user_id="user_456",
        content="Test note content",
        category="decision",
    )

    saved_note = await repository.save(note)
    await async_session.commit()

    assert saved_note.id == note.id
    assert saved_note.embedding is not None
    assert len(saved_note.embedding) == 1024

    # Verify saved in database
    stmt = select(NoteTable).where(NoteTable.id == note.id)
    result = await async_session.execute(stmt)
    note_table = result.scalar_one_or_none()

    assert note_table is not None
    assert note_table.content == "Test note content"
    assert note_table.category == "decision"


@pytest.mark.asyncio
async def test_list_by_session(repository, async_session):
    """Test list notes by session"""
    repository._generate_embedding = AsyncMock(return_value=[0.1] * 1024)

    note1 = Note(
        session_id="session_123",
        user_id="user_456",
        content="Note 1",
        category="decision",
    )
    note2 = Note(
        session_id="session_123",
        user_id="user_456",
        content="Note 2",
        category="general",
    )
    note3 = Note(
        session_id="session_999",
        user_id="user_456",
        content="Note 3",
        category="decision",
    )

    await repository.save(note1)
    await repository.save(note2)
    await repository.save(note3)
    await async_session.commit()

    notes = await repository.list_by_session("session_123")

    assert len(notes) == 2
    assert all(n.session_id == "session_123" for n in notes)


@pytest.mark.asyncio
async def test_list_by_user(repository, async_session):
    """Test list notes by user"""
    repository._generate_embedding = AsyncMock(return_value=[0.1] * 1024)

    note1 = Note(
        session_id="session_123",
        user_id="user_456",
        content="Note 1",
        category="decision",
    )
    note2 = Note(
        session_id="session_789",
        user_id="user_456",
        content="Note 2",
        category="general",
    )
    note3 = Note(
        session_id="session_999",
        user_id="user_999",
        content="Note 3",
        category="decision",
    )

    await repository.save(note1)
    await repository.save(note2)
    await repository.save(note3)
    await async_session.commit()

    notes = await repository.list_by_user("user_456")

    assert len(notes) == 2
    assert all(n.user_id == "user_456" for n in notes)


@pytest.mark.asyncio
async def test_get_note(repository, async_session):
    """Test get note by ID"""
    repository._generate_embedding = AsyncMock(return_value=[0.1] * 1024)

    note = Note(
        session_id="session_123",
        user_id="user_456",
        content="Test note",
        category="decision",
    )

    await repository.save(note)
    await async_session.commit()

    retrieved_note = await repository.get(note.id)

    assert retrieved_note is not None
    assert retrieved_note.id == note.id
    assert retrieved_note.content == "Test note"
    assert retrieved_note.category == "decision"


@pytest.mark.asyncio
async def test_get_nonexistent_note(repository):
    """Test get nonexistent note"""
    from uuid import uuid4

    nonexistent_id = uuid4()
    note = await repository.get(nonexistent_id)

    assert note is None


@pytest.mark.asyncio
async def test_delete_note(repository, async_session):
    """Test delete note"""
    repository._generate_embedding = AsyncMock(return_value=[0.1] * 1024)

    note = Note(
        session_id="session_123",
        user_id="user_456",
        content="Test note",
        category="decision",
    )

    await repository.save(note)
    await async_session.commit()

    await repository.delete(note.id)
    await async_session.commit()

    # Verify deleted
    stmt = select(NoteTable).where(NoteTable.id == note.id)
    result = await async_session.execute(stmt)
    note_table = result.scalar_one_or_none()

    assert note_table is None
