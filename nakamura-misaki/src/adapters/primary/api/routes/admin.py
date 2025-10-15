"""Admin UI endpoints

Provides web interface for team management dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, session: AsyncSession = Depends(get_db_session)
):
    """Admin Dashboard UI

    Args:
        request: FastAPI Request
        session: データベースセッション

    Returns:
        HTML dashboard
    """
    # TODO: Jinja2テンプレートの実装
    raise HTTPException(status_code=501, detail="Admin UI not implemented")
