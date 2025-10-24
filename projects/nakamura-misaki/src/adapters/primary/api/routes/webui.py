"""Web UI API Routes - Real data from PostgreSQL

Provides real data from PostgreSQL database for the Web UI dashboard.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from .....contexts.conversations.infrastructure.repositories.postgresql_conversation_repository import (
    PostgreSQLConversationRepository,
)
from .....contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository,
)
from .....infrastructure.repositories.postgresql_slack_user_repository import PostgreSQLSlackUserRepository


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


class PromptResponse(BaseModel):
    name: str
    system_prompt: str
    description: str
    version: str
    created_at: str
    updated_at: str


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
async def list_users(request: Request) -> list[UserResponse]:
    """List all users (from database cache, synced every hour)"""
    db_manager = request.app.state.db_manager

    async with db_manager.session() as session:
        repo = PostgreSQLSlackUserRepository(session)
        users = await repo.find_all_active()

        return [
            UserResponse(
                user_id=user.user_id,
                name=user.name,
                real_name=user.real_name or "",
                display_name=user.display_name or user.name,
                email=user.email or "",
                is_admin=user.is_admin,
                is_bot=user.is_bot,
                created_at=user.slack_created_at.isoformat(),
            )
            for user in users
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


@router.get("/admin/prompts", response_model=list[PromptResponse])
async def list_prompts() -> list[PromptResponse]:
    """List all prompts (read from JSON files)"""
    # Path to prompts directory (relative to src/)
    prompts_dir = Path(__file__).parents[5] / "src" / "infrastructure" / "config" / "prompts"

    if not prompts_dir.exists():
        raise HTTPException(status_code=500, detail="Prompts directory not found")

    prompts = []

    for json_file in prompts_dir.glob("*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            # Extract metadata for created_at/updated_at
            metadata = data.get("metadata", {})
            created_at = metadata.get("created_at", "2025-01-01")
            updated_at = metadata.get("updated_at", created_at)

            # Convert to ISO datetime format if needed
            if not created_at.endswith("Z") and "T" not in created_at:
                created_at = f"{created_at}T00:00:00Z"
            if not updated_at.endswith("Z") and "T" not in updated_at:
                updated_at = f"{updated_at}T00:00:00Z"

            prompts.append(
                PromptResponse(
                    name=data["name"],
                    system_prompt=data["system_prompt"],
                    description=data.get("description", ""),
                    version=data.get("version", "1.0.0"),
                    created_at=created_at,
                    updated_at=updated_at,
                )
            )
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"⚠️ Failed to load prompt {json_file.name}: {e}")
            continue

    return prompts
