"""E2E Test: Task Lifecycle via Slack

タスク登録 → 一覧取得 → 完了までのフロー
"""

import os
import re
from datetime import datetime
from uuid import UUID

import pytest
from anthropic import Anthropic
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.primary.slack_event_handler import SlackEventHandler
from src.infrastructure.database.schema import Base


@pytest.fixture
async def async_engine():
    """Create async engine for testing"""
    # Use in-memory SQLite for E2E tests
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
    """Mock Claude client (no actual API calls)"""
    # Return dummy client (not used in E2E)
    return None


@pytest.fixture
def mock_slack_token():
    """Mock Slack token"""
    return "xoxb-test-token"


@pytest.fixture
def slack_handler(async_session, mock_claude_client, mock_slack_token):
    """Create Slack event handler"""
    # Mock Anthropic client
    claude_client = Anthropic(api_key="sk-ant-test-key")
    return SlackEventHandler(async_session, claude_client, mock_slack_token)


def extract_task_id(text: str) -> UUID | None:
    """Extract task UUID from response text"""
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    match = re.search(uuid_pattern, text, re.IGNORECASE)
    if match:
        return UUID(match.group(0))
    return None


@pytest.mark.asyncio
async def test_task_lifecycle(slack_handler, async_session):
    """Test: Task registration → list → completion"""
    user_id = "U01TEST"

    # 1. タスク登録
    response = await slack_handler.handle_message(
        user_id=user_id, text="「E2Eテストタスク」を今日やる"
    )

    assert response is not None
    assert "✅ タスクを登録しました" in response
    assert "E2Eテストタスク" in response

    # セッションコミット
    await async_session.commit()

    # 2. タスク一覧取得
    response = await slack_handler.handle_message(user_id=user_id, text="今日のタスクは？")

    assert response is not None
    assert "E2Eテストタスク" in response

    # タスクIDを抽出
    task_id = extract_task_id(response)
    assert task_id is not None

    # 3. タスク完了
    response = await slack_handler.handle_message(
        user_id=user_id, text=f"タスク {task_id} 完了"
    )

    assert response is not None
    assert "✅ タスクを完了しました" in response

    # セッションコミット
    await async_session.commit()

    # 4. 完了後の一覧確認（完了タスクは表示されない）
    response = await slack_handler.handle_message(user_id=user_id, text="今日のタスクは？")

    assert response is not None
    # 完了タスクは今日のタスク一覧から除外される
    assert "該当するタスクはありません" in response or "0件" in response


@pytest.mark.asyncio
async def test_multiple_tasks(slack_handler, async_session):
    """Test: Multiple tasks management"""
    user_id = "U01TEST"

    # 複数タスク登録
    await slack_handler.handle_message(user_id=user_id, text="「タスク1」をやる")
    await slack_handler.handle_message(user_id=user_id, text="「タスク2」をやる")
    await slack_handler.handle_message(user_id=user_id, text="「タスク3」をやる")

    await async_session.commit()

    # タスク一覧取得
    response = await slack_handler.handle_message(user_id=user_id, text="タスク一覧")

    assert response is not None
    assert "タスク1" in response
    assert "タスク2" in response
    assert "タスク3" in response


@pytest.mark.asyncio
async def test_non_task_message(slack_handler):
    """Test: Non-task message returns None (fallback to normal chat)"""
    user_id = "U01TEST"

    response = await slack_handler.handle_message(
        user_id=user_id, text="こんにちは、今日の天気は？"
    )

    # タスク/ハンドオフコマンドではないのでNone
    assert response is None
