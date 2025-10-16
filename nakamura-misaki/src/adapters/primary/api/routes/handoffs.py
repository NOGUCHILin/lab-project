"""REST API for Handoff Management

Provides RESTful endpoints for handoff operations.
"""

import logging
from datetime import datetime

from anthropic import Anthropic
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import CreateHandoffDTO
from src.infrastructure.di import DIContainer

from ..dependencies import get_db_session

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Models
class HandoffCreate(BaseModel):
    """ハンドオフ作成リクエスト"""

    task_id: str
    from_user_id: str
    to_user_id: str
    progress_note: str
    handoff_at: datetime | None = None


class HandoffResponse(BaseModel):
    """ハンドオフレスポンス"""

    handoff_id: str
    task_id: str
    from_user_id: str
    to_user_id: str
    progress_note: str
    handoff_at: datetime
    completed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=HandoffResponse)
async def create_handoff(
    handoff_data: HandoffCreate, session: AsyncSession = Depends(get_db_session)
):
    """ハンドオフを作成

    Args:
        handoff_data: ハンドオフ作成データ
        session: データベースセッション

    Returns:
        作成されたハンドオフ
    """
    logger.info(
        f"Creating handoff: task_id={handoff_data.task_id}, "
        f"from={handoff_data.from_user_id}, to={handoff_data.to_user_id}"
    )

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)
    use_case = container.build_register_handoff_use_case()

    dto = CreateHandoffDTO(
        task_id=handoff_data.task_id,
        from_user_id=handoff_data.from_user_id,
        to_user_id=handoff_data.to_user_id,
        progress_note=handoff_data.progress_note,
        handoff_at=handoff_data.handoff_at,
    )

    handoff = await use_case.execute(dto)
    logger.info(f"Handoff created successfully: handoff_id={handoff.handoff_id}")
    return HandoffResponse.model_validate(handoff)


@router.get("", response_model=list[HandoffResponse])
async def list_handoffs(
    user_id: str, session: AsyncSession = Depends(get_db_session)
):
    """ハンドオフ一覧を取得

    Args:
        user_id: ユーザーID
        session: データベースセッション

    Returns:
        ハンドオフ一覧
    """
    logger.info(f"Listing handoffs: user={user_id}")

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)
    use_case = container.build_query_handoffs_by_user_use_case()

    handoffs = await use_case.execute(user_id)
    logger.info(f"Handoffs retrieved: count={len(handoffs)}")
    return [HandoffResponse.model_validate(handoff) for handoff in handoffs]


@router.post("/{handoff_id}/complete", response_model=HandoffResponse)
async def complete_handoff(
    handoff_id: str, session: AsyncSession = Depends(get_db_session)
):
    """ハンドオフを完了

    Args:
        handoff_id: ハンドオフID
        session: データベースセッション

    Returns:
        完了したハンドオフ
    """
    logger.info(f"Completing handoff: handoff_id={handoff_id}")

    # TODO: Anthropic/Slack clientを適切に取得
    claude_client = Anthropic()
    slack_client = AsyncWebClient()

    container = DIContainer(session, claude_client, slack_client)
    use_case = container.build_complete_handoff_use_case()

    handoff = await use_case.execute(handoff_id)
    logger.info(f"Handoff completed successfully: handoff_id={handoff_id}")
    return HandoffResponse.model_validate(handoff)
