"""E2E Test: Handoff Lifecycle via Slack

ハンドオフ登録 → 一覧取得 → 完了までのフロー
"""

import re
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from anthropic import Anthropic
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.primary.slack_event_handler import SlackEventHandler
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
def slack_handler(async_session):
    """Create Slack event handler"""
    claude_client = Anthropic(api_key="sk-ant-test-key")
    return SlackEventHandler(async_session, claude_client, "xoxb-test-token")


def extract_uuid(text: str) -> UUID | None:
    """Extract UUID from text"""
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    match = re.search(uuid_pattern, text, re.IGNORECASE)
    if match:
        return UUID(match.group(0))
    return None


async def create_test_task(session: AsyncSession, user_id: str) -> UUID:
    """Create test task in database"""
    task_id = uuid4()
    task_table = TaskTable(
        id=task_id,
        user_id=user_id,
        title="Test Task for Handoff",
        description="Test Description",
        status=TaskStatus.IN_PROGRESS.value,
        created_at=datetime.now(),
    )
    session.add(task_table)
    await session.commit()
    return task_id


@pytest.mark.asyncio
async def test_handoff_lifecycle(slack_handler, async_session):
    """Test: Handoff registration → list → completion"""
    from_user = "U01ALICE"
    to_user = "U01BOB"

    # テストタスク作成
    task_id = await create_test_task(async_session, from_user)

    # 1. ハンドオフ登録
    handoff_time = datetime.now() + timedelta(hours=2)
    response = await slack_handler.handle_message(
        user_id=from_user,
        text=f"「API統合50%完了」を @{to_user} に {task_id} 2時間後に引き継ぎ",
    )

    assert response is not None
    assert "✅ ハンドオフを登録しました" in response
    assert "API統合50%完了" in response

    await async_session.commit()

    # 2. ハンドオフ一覧取得（引き継ぎ先ユーザー）
    response = await slack_handler.handle_message(
        user_id=to_user, text="引き継ぎ一覧"
    )

    assert response is not None
    assert "保留中の引き継ぎ一覧" in response
    assert "API統合50%完了" in response

    # ハンドオフIDを抽出
    handoff_id = extract_uuid(response)
    assert handoff_id is not None

    # 3. ハンドオフ完了
    response = await slack_handler.handle_message(
        user_id=to_user, text=f"ハンドオフ {handoff_id} 完了"
    )

    assert response is not None
    assert "✅ ハンドオフを完了しました" in response

    await async_session.commit()

    # 4. 完了後の一覧確認（完了済みは表示されない）
    response = await slack_handler.handle_message(
        user_id=to_user, text="引き継ぎ一覧"
    )

    assert response is not None
    assert "保留中の引き継ぎはありません" in response or "0件" in response


@pytest.mark.asyncio
async def test_handoff_without_task_id(slack_handler):
    """Test: Handoff registration without task ID fails"""
    user_id = "U01ALICE"

    response = await slack_handler.handle_message(
        user_id=user_id, text="@U01BOB に引き継ぎ"
    )

    # タスクIDがないのでエラー
    assert response is not None
    assert "❌" in response or "タスクID" in response


@pytest.mark.asyncio
async def test_handoff_without_to_user(slack_handler, async_session):
    """Test: Handoff registration without to_user fails"""
    user_id = "U01ALICE"

    # テストタスク作成
    task_id = await create_test_task(async_session, user_id)

    response = await slack_handler.handle_message(
        user_id=user_id, text=f"{task_id} を引き継ぎ"
    )

    # 引き継ぎ先ユーザーがないのでエラー
    assert response is not None
    assert "❌" in response or "引き継ぎ先" in response
