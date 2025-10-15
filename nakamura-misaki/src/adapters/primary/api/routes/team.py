"""REST API for Team Management

Provides team-wide statistics and bottleneck detection.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session

router = APIRouter()


# Response Models
class TeamTasksResponse(BaseModel):
    """チーム全体のタスクレスポンス"""

    total_tasks: int
    tasks_by_user: dict[str, int]
    # TODO: 詳細な実装


class TeamStatsResponse(BaseModel):
    """チーム統計レスポンス"""

    week_start: str
    week_end: str
    completion_rate: float
    total_handoffs: int
    # TODO: 詳細な実装


class BottleneckResponse(BaseModel):
    """ボトルネック検出レスポンス"""

    type: str
    severity: str
    message: str
    # TODO: 詳細な実装


@router.get("/tasks", response_model=TeamTasksResponse)
async def get_team_tasks(session: AsyncSession = Depends(get_db_session)):
    """チーム全体のタスクを取得

    Args:
        session: データベースセッション

    Returns:
        チーム全体のタスク情報
    """
    # TODO: DetectBottleneckUseCase, QueryTeamStatsUseCaseの実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/stats", response_model=TeamStatsResponse)
async def get_team_stats(session: AsyncSession = Depends(get_db_session)):
    """チーム統計を取得

    Args:
        session: データベースセッション

    Returns:
        チーム統計情報
    """
    # TODO: QueryTeamStatsUseCaseの実装
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/bottlenecks", response_model=list[BottleneckResponse])
async def get_bottlenecks(session: AsyncSession = Depends(get_db_session)):
    """ボトルネック検出

    Args:
        session: データベースセッション

    Returns:
        検出されたボトルネック一覧
    """
    # TODO: DetectBottleneckUseCaseの実装
    raise HTTPException(status_code=501, detail="Not implemented")
