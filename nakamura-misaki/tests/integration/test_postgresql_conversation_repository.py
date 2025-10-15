"""Integration tests for PostgreSQLConversationRepository.

Following TDD: Red -> Green -> Refactor
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.secondary.postgresql_conversation_repository import (
    PostgreSQLConversationRepository,
)
from src.domain.models.conversation import Conversation, Message, MessageRole
from src.infrastructure.database.schema import Base, ConversationTable


@pytest.fixture
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """Create async session for testing."""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
def repository(async_session):
    """Create repository instance."""
    return PostgreSQLConversationRepository(async_session)


@pytest.mark.asyncio
async def test_save_new_conversation(repository, async_session):
    """Should save a new conversation to database."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=[Message(role=MessageRole.USER, content="こんにちは")],
    )

    saved_conversation = await repository.save(conversation)
    await async_session.commit()

    assert saved_conversation.conversation_id == conversation.conversation_id
    assert saved_conversation.user_id == "U5D0CJKMH"
    assert len(saved_conversation.messages) == 1

    # Verify saved in database
    stmt = select(ConversationTable).where(
        ConversationTable.conversation_id == conversation.conversation_id
    )
    result = await async_session.execute(stmt)
    conversation_table = result.scalar_one_or_none()

    assert conversation_table is not None
    assert conversation_table.user_id == "U5D0CJKMH"
    assert conversation_table.channel_id == "C1234567890"
    assert len(conversation_table.messages) == 1


@pytest.mark.asyncio
async def test_save_update_existing_conversation(repository, async_session):
    """Should update an existing conversation."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=[Message(role=MessageRole.USER, content="初回メッセージ")],
    )

    # Save initial
    await repository.save(conversation)
    await async_session.commit()

    # Add message and update
    conversation.add_message(Message(role=MessageRole.ASSISTANT, content="返信"))
    updated_conversation = await repository.save(conversation)
    await async_session.commit()

    assert len(updated_conversation.messages) == 2

    # Verify in database
    stmt = select(ConversationTable).where(
        ConversationTable.conversation_id == conversation.conversation_id
    )
    result = await async_session.execute(stmt)
    conversation_table = result.scalar_one_or_none()

    assert conversation_table is not None
    assert len(conversation_table.messages) == 2


@pytest.mark.asyncio
async def test_get_by_id(repository, async_session):
    """Should get conversation by conversation_id."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=[Message(role=MessageRole.USER, content="test")],
    )

    await repository.save(conversation)
    await async_session.commit()

    retrieved = await repository.get_by_id(conversation.conversation_id)

    assert retrieved is not None
    assert retrieved.conversation_id == conversation.conversation_id
    assert retrieved.user_id == "U5D0CJKMH"
    assert len(retrieved.messages) == 1


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository):
    """Should return None when conversation not found."""
    non_existent_id = uuid4()
    retrieved = await repository.get_by_id(non_existent_id)

    assert retrieved is None


@pytest.mark.asyncio
async def test_get_by_user_and_channel(repository, async_session):
    """Should get latest conversation by user_id and channel_id."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=[Message(role=MessageRole.USER, content="test")],
    )

    await repository.save(conversation)
    await async_session.commit()

    retrieved = await repository.get_by_user_and_channel("U5D0CJKMH", "C1234567890")

    assert retrieved is not None
    assert retrieved.user_id == "U5D0CJKMH"
    assert retrieved.channel_id == "C1234567890"


@pytest.mark.asyncio
async def test_get_by_user_and_channel_not_found(repository):
    """Should return None when no conversation found."""
    retrieved = await repository.get_by_user_and_channel("U999999", "C999999")

    assert retrieved is None


@pytest.mark.asyncio
async def test_delete(repository, async_session):
    """Should delete conversation."""
    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=[Message(role=MessageRole.USER, content="test")],
    )

    await repository.save(conversation)
    await async_session.commit()

    await repository.delete(conversation.conversation_id)
    await async_session.commit()

    # Verify deleted
    retrieved = await repository.get_by_id(conversation.conversation_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_expired(repository, async_session):
    """Should delete conversations older than TTL."""
    # Create old conversation (25 hours ago)
    old_time = datetime.now(timezone.utc) - timedelta(hours=25)
    old_conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=[Message(role=MessageRole.USER, content="old")],
        last_message_at=old_time,
    )

    # Create recent conversation
    recent_conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C9999999999",
        messages=[Message(role=MessageRole.USER, content="recent")],
    )

    await repository.save(old_conversation)
    await repository.save(recent_conversation)
    await async_session.commit()

    # Delete expired (TTL = 24 hours)
    deleted_count = await repository.delete_expired(ttl_hours=24)
    await async_session.commit()

    assert deleted_count == 1

    # Verify old deleted, recent still exists
    assert await repository.get_by_id(old_conversation.conversation_id) is None
    assert await repository.get_by_id(recent_conversation.conversation_id) is not None


@pytest.mark.asyncio
async def test_messages_format_consistency(repository, async_session):
    """Should maintain message format through save/load cycle."""
    messages = [
        Message(role=MessageRole.USER, content="タスク登録して"),
        Message(role=MessageRole.ASSISTANT, content="承知しました"),
        Message(role=MessageRole.USER, content="明日までにレポート"),
    ]

    conversation = Conversation(
        conversation_id=uuid4(),
        user_id="U5D0CJKMH",
        channel_id="C1234567890",
        messages=messages,
    )

    await repository.save(conversation)
    await async_session.commit()

    retrieved = await repository.get_by_id(conversation.conversation_id)

    assert retrieved is not None
    assert len(retrieved.messages) == 3
    assert retrieved.messages[0].role == MessageRole.USER
    assert retrieved.messages[0].content == "タスク登録して"
    assert retrieved.messages[1].role == MessageRole.ASSISTANT
    assert retrieved.messages[1].content == "承知しました"
    assert retrieved.messages[2].role == MessageRole.USER
    assert retrieved.messages[2].content == "明日までにレポート"
