"""FastAPI Application Factory

Creates and configures the FastAPI application with all routes.
"""

import logging
import os

from anthropic import Anthropic
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .routes import admin, handoffs, slack, tasks, team

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application

    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title="nakamura-misaki v4.0.0 API",
        description="Task management AI assistant with Kusanagi Motoko personality",
        version="4.0.0",
    )

    # グローバル状態（起動時に初期化）
    app.state.slack_signing_secret = None
    app.state.database_url = None
    app.state.slack_token = None
    app.state.anthropic_api_key = None
    app.state.async_session_maker = None

    @app.on_event("startup")
    async def startup():
        """サーバー起動時の初期化"""
        # Configure logging
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(f"Logging configured: level={log_level}")
        logger.info("Starting nakamura-misaki API server v4.0.0")

        # 環境変数読み込み
        app.state.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        app.state.database_url = os.getenv("DATABASE_URL")
        app.state.slack_token = os.getenv("SLACK_BOT_TOKEN")
        app.state.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # 環境変数バリデーション
        if not app.state.slack_signing_secret:
            logger.error("SLACK_SIGNING_SECRET is not set")
            raise RuntimeError("SLACK_SIGNING_SECRET is not set")
        if not app.state.database_url:
            logger.error("DATABASE_URL is not set")
            raise RuntimeError("DATABASE_URL is not set")
        if not app.state.slack_token:
            logger.error("SLACK_BOT_TOKEN is not set")
            raise RuntimeError("SLACK_BOT_TOKEN is not set")
        if not app.state.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY is not set")
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        logger.info("Environment variables validated")

        # データベース接続
        logger.info(f"Connecting to database: {app.state.database_url.split('@')[1] if '@' in app.state.database_url else 'localhost'}")
        engine = create_async_engine(app.state.database_url, echo=False)
        app.state.async_session_maker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("Database connection established")

        logger.info("✅ nakamura-misaki API server started successfully")

    @app.get("/health")
    async def health():
        """ヘルスチェック"""
        return {"status": "ok", "service": "nakamura-misaki", "version": "4.0.0"}

    # ルート登録
    app.include_router(slack.router, prefix="/webhook", tags=["Slack"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(handoffs.router, prefix="/api/handoffs", tags=["Handoffs"])
    app.include_router(team.router, prefix="/api/team", tags=["Team"])
    app.include_router(admin.router, prefix="/admin", tags=["Admin UI"])

    return app


# Create module-level app instance for uvicorn
app = create_app()
