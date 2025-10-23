"""Web UI API Routes - Real data from PostgreSQL

Provides real data from PostgreSQL database for the Web UI dashboard.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from .....contexts.conversations.infrastructure.repositories.postgresql_conversation_repository import (
    PostgreSQLConversationRepository,
)
from .....contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository,
)
from ...dependencies import get_slack_adapter


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
async def list_tasks(request: Request) -> list[TaskResponse]:
    """List all tasks (real data from PostgreSQL)"""
    db_manager = request.app.state.db_manager

    async with db_manager.session() as session:
        repo = PostgreSQLTaskRepository(session)
        tasks = await repo.find_all()

        return [
            TaskResponse(
                id=str(task.id),
                user_id=task.assignee_user_id,
                title=task.title,
                due_date=task.due_at.isoformat() if task.due_at else "",
                status=task.status.value,
                progress=0,  # TODO: 進捗率の計算ロジック追加
                description=task.description or "",
                created_by=task.creator_user_id,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
            )
            for task in tasks
        ]


@router.get("/users", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    """List all users (real data from Slack API)"""
    slack = get_slack_adapter()

    try:
        users_result = await slack.users_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users from Slack: {str(e)}")

    if not users_result.get("ok"):
        error = users_result.get("error", "unknown")
        raise HTTPException(status_code=500, detail=f"Slack API error: {error}")

    members = users_result.get("members", [])

    return [
        UserResponse(
            user_id=user["id"],
            name=user.get("name", ""),
            real_name=user.get("real_name", ""),
            display_name=user.get("profile", {}).get("display_name", "") or user.get("name", ""),
            email=user.get("profile", {}).get("email", ""),
            is_admin=user.get("is_admin", False),
            is_bot=user.get("is_bot", False),
            created_at=datetime.fromtimestamp(user.get("updated", 0), tz=UTC).isoformat(),
        )
        for user in members
        if not user.get("deleted", False)
    ]


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(request: Request, limit: int = Query(50, ge=1, le=100)) -> list[SessionResponse]:
    """List all sessions (real data from conversations table)"""
    db_manager = request.app.state.db_manager

    async with db_manager.session() as session:
        repo = PostgreSQLConversationRepository(session)
        conversations = await repo.find_recent(limit=limit)

        return [
            SessionResponse(
                session_id=str(conv.id.value),
                user_id=conv.user_id.value,
                created_at=conv.created_at.isoformat(),
                last_active=conv.updated_at.isoformat(),
                title=f"Conversation in #{conv.channel_id}",
                message_count=len(conv.messages),
                is_active=(datetime.now(UTC) - conv.updated_at).total_seconds() < 3600,
            )
            for conv in conversations
        ]


@router.get("/logs/errors", response_model=list[ErrorLogResponse])
async def list_error_logs(limit: int = Query(10, ge=1, le=100)) -> list[ErrorLogResponse]:
    """List recent error logs (mock data)"""
    # Return empty list to indicate no errors
    return []
