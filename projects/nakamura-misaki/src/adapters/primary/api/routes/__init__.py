"""API Route Modules"""

from fastapi import APIRouter

from . import slack, webui

# Create unified router for main.py compatibility
router = APIRouter()
router.include_router(slack.router, prefix="/webhook", tags=["Slack"])
router.include_router(webui.router, tags=["Web UI"])

__all__ = ["slack", "webui", "router"]
