"""Web UI API Routes - Mock endpoints for dashboard

Provides mock data for the Web UI dashboard while real implementations are being developed.
"""

from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel


# Response Models
class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    due_date: str
    status: str
    progress: int
    description: str
    created_by: str
    created_at: str
    updated_at: str


class UserResponse(BaseModel):
    user_id: str
    name: str
    real_name: str
    display_name: str
    email: str
    is_admin: bool
    is_bot: bool
    created_at: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    last_active: str
    title: str
    message_count: int
    is_active: bool


class ErrorLogResponse(BaseModel):
    id: int
    error_hash: str
    message: str
    stack: str | None
    url: str | None
    user_agent: str | None
    context: dict | None
    occurrence_count: int
    first_seen: str
    last_seen: str


router = APIRouter(prefix="/api", tags=["Web UI"])


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks() -> list[TaskResponse]:
    """List all tasks (mock data)"""
    now = datetime.now()
    return [
        TaskResponse(
            id=str(uuid4()),
            user_id="U12345",
            title="nakamura-misaki Web UIの実装",
            due_date=(now + timedelta(hours=2)).isoformat(),
            status="in_progress",
            progress=75,
            description="Next.jsでWeb UIを実装し、統合ダッシュボードに登録する",
            created_by="U12345",
            created_at=(now - timedelta(days=1)).isoformat(),
            updated_at=now.isoformat(),
        ),
        TaskResponse(
            id=str(uuid4()),
            user_id="U12345",
            title="REST APIエンドポイントの追加",
            due_date=(now + timedelta(days=1)).isoformat(),
            status="pending",
            progress=0,
            description="タスク・ユーザー・セッション用のREST APIを実装",
            created_by="U12345",
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
        ),
        TaskResponse(
            id=str(uuid4()),
            user_id="U67890",
            title="デプロイメントパイプラインの確認",
            due_date=(now - timedelta(hours=2)).isoformat(),  # 期限切れ
            status="pending",
            progress=20,
            description="GitHub Actionsのデプロイワークフローをレビュー",
            created_by="U12345",
            created_at=(now - timedelta(days=2)).isoformat(),
            updated_at=(now - timedelta(hours=3)).isoformat(),
        ),
    ]


@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    """List all users (mock data)"""
    now = datetime.now()
    return [
        UserResponse(
            user_id="U12345",
            name="noguchilin",
            real_name="野口凜",
            display_name="野口凜",
            email="noguchilin@example.com",
            is_admin=True,
            is_bot=False,
            created_at=(now - timedelta(days=30)).isoformat(),
        ),
        UserResponse(
            user_id="U67890",
            name="testuser",
            real_name="Test User",
            display_name="Test User",
            email="test@example.com",
            is_admin=False,
            is_bot=False,
            created_at=(now - timedelta(days=15)).isoformat(),
        ),
    ]


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions() -> list[SessionResponse]:
    """List all sessions (mock data)"""
    now = datetime.now()
    return [
        SessionResponse(
            session_id=str(uuid4()),
            user_id="U12345",
            created_at=(now - timedelta(hours=2)).isoformat(),
            last_active=now.isoformat(),
            title="Web UI実装に関する相談",
            message_count=15,
            is_active=True,
        ),
        SessionResponse(
            session_id=str(uuid4()),
            user_id="U12345",
            created_at=(now - timedelta(days=1)).isoformat(),
            last_active=(now - timedelta(hours=5)).isoformat(),
            title="デプロイメント設定のレビュー",
            message_count=8,
            is_active=False,
        ),
        SessionResponse(
            session_id=str(uuid4()),
            user_id="U67890",
            created_at=(now - timedelta(days=2)).isoformat(),
            last_active=(now - timedelta(days=1)).isoformat(),
            title="タスク管理機能について",
            message_count=23,
            is_active=False,
        ),
    ]


@router.get("/logs/errors", response_model=list[ErrorLogResponse])
async def list_error_logs(limit: int = Query(10, ge=1, le=100)) -> list[ErrorLogResponse]:
    """List recent error logs (mock data)"""
    # Return empty list to indicate no errors
    return []
