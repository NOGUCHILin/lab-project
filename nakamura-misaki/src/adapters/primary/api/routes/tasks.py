"""REST API for Task Management

Provides RESTful endpoints for CRUD operations on tasks.
"""

import logging
from datetime import datetime

from anthropic import Anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import CreateTaskDTO, UpdateTaskDTO
from src.domain.models import TaskStatus
from src.infrastructure.di import DIContainer

from ..dependencies import get_db_session

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Models
class TaskCreate(BaseModel):
    """タスク作成リクエスト"""

    user_id: str
    title: str
    description: str | None = None
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    """タスク更新リクエスト"""

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None


class TaskResponse(BaseModel):
    """タスクレスポンス"""

    task_id: str
    user_id: str
    title: str
    description: str
    status: TaskStatus
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate, session: AsyncSession = Depends(get_db_session)
):
    """タスクを作成

    Args:
        task_data: タスク作成データ
        session: データベースセッション

    Returns:
        作成されたタスク
    """
    logger.info(f"Creating task: user={task_data.user_id}, title={task_data.title}")

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)
    use_case = container.build_register_task_use_case()

    dto = CreateTaskDTO(
        user_id=task_data.user_id,
        title=task_data.title,
        description=task_data.description or "",
        due_at=task_data.due_at,
    )

    task = await use_case.execute(dto)
    logger.info(f"Task created successfully: task_id={task.task_id}")
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, session: AsyncSession = Depends(get_db_session)):
    """タスクを取得

    Args:
        task_id: タスクID
        session: データベースセッション

    Returns:
        タスク詳細
    """
    # TODO: 実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str,
    status: TaskStatus | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    """タスク一覧を取得

    Args:
        user_id: ユーザーID
        status: タスクステータス（フィルタ）
        session: データベースセッション

    Returns:
        タスク一覧
    """
    logger.info(f"Listing tasks: user={user_id}, status={status}")

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)

    if status:
        use_case = container.build_query_user_tasks_use_case()
        tasks = await use_case.execute(user_id, status=status)
    else:
        use_case = container.build_query_today_tasks_use_case()
        tasks = await use_case.execute(user_id)

    logger.info(f"Tasks retrieved: count={len(tasks)}")
    return [TaskResponse.model_validate(task) for task in tasks]


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """タスクを更新

    Args:
        task_id: タスクID
        task_data: 更新データ
        session: データベースセッション

    Returns:
        更新されたタスク
    """
    logger.info(f"Updating task: task_id={task_id}, updates={task_data.model_dump(exclude_none=True)}")

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)
    use_case = container.build_update_task_use_case()

    dto = UpdateTaskDTO(
        task_id=task_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        due_at=task_data.due_at,
    )

    task = await use_case.execute(dto)
    logger.info(f"Task updated successfully: task_id={task_id}")
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str, session: AsyncSession = Depends(get_db_session)
):
    """タスクを完了

    Args:
        task_id: タスクID
        session: データベースセッション

    Returns:
        完了したタスク
    """
    logger.info(f"Completing task: task_id={task_id}")

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)
    use_case = container.build_complete_task_use_case()

    task = await use_case.execute(task_id)
    logger.info(f"Task completed successfully: task_id={task_id}")
    return TaskResponse.model_validate(task)
