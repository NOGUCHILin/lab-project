"""FastAPI application entry point - Nakamura-Misaki v2.0

Fixed: Initialize app.state with Slack configuration for signature verification.
Fixed: Initialize slack_event_handler from DI container for message processing.
Feature: Database caching for Slack users with periodic background sync.
"""

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slack_sdk.web.async_client import AsyncWebClient

from .adapters.primary.api.routes import router
from .adapters.primary.dependencies import get_slack_adapter
from .adapters.secondary.slack_adapter import SlackAdapter
from .domain.services.slack_user_sync_service import SlackUserSyncService
from .infrastructure.config import AppConfig
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.logging import setup_logging
from .infrastructure.repositories.postgresql_slack_user_repository import PostgreSQLSlackUserRepository

# Load configuration
config = AppConfig.from_env()
config.validate()

# Setup logging
setup_logging(debug=config.debug)


async def _periodic_user_sync(db_manager: DatabaseManager, slack_token: str) -> None:
    """Background task: Sync Slack users every hour"""
    sync_interval = 3600  # 1 hour in seconds

    while True:
        try:
            print("🔄 Starting periodic Slack user sync...")
            async with db_manager.session() as session:
                slack_adapter = SlackAdapter(token=slack_token)
                slack_user_repo = PostgreSQLSlackUserRepository(session)
                sync_service = SlackUserSyncService(slack_adapter, slack_user_repo)

                result = await sync_service.sync_users()

                # Commit the transaction
                await session.commit()

                if result["status"] == "success":
                    print(f"✅ User sync completed: {result['synced_count']} users synced")
                else:
                    print(f"⚠️ User sync failed: {result.get('message', 'unknown error')}")

        except Exception as e:
            print(f"❌ Error in periodic user sync: {e}")

        await asyncio.sleep(sync_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Nakamura-Misaki v2.0 (FastAPI + Hexagonal Architecture)")
    print(f"📍 API: http://localhost:{config.port}")
    print(f"📖 Docs: http://localhost:{config.port}/docs")
    print("")

    # Initialize database
    print("🗄️  Initializing database connection...")
    db_manager = DatabaseManager(config.database_url, echo=config.debug)
    app.state.db_manager = db_manager

    # Initialize Slack client
    slack_client = AsyncWebClient(token=config.slack_bot_token)
    app.state.slack_client = slack_client

    # Initialize app.state with configuration (for routes)
    app.state.slack_signing_secret = config.slack_signing_secret
    app.state.slack_token = config.slack_bot_token
    app.state.anthropic_api_key = config.anthropic_api_key
    app.state.database_url = config.database_url
    app.state.conversation_ttl_hours = config.conversation_ttl_hours

    print("✅ Application state initialized")

    # End DND mode on startup
    slack = get_slack_adapter()
    dnd_result = await slack.end_dnd()
    if dnd_result.get("ok"):
        print("✅ おやすみモード解除完了")
    else:
        print(f"⚠️ おやすみモード解除失敗: {dnd_result.get('error', 'unknown')}")

    # Initial user sync on startup
    print("🔄 Running initial Slack user sync...")
    try:
        async with db_manager.session() as session:
            slack_adapter = SlackAdapter(token=config.slack_bot_token)
            slack_user_repo = PostgreSQLSlackUserRepository(session)
            sync_service = SlackUserSyncService(slack_adapter, slack_user_repo)

            result = await sync_service.sync_users()
            await session.commit()

            if result["status"] == "success":
                print(f"✅ Initial user sync completed: {result['synced_count']} users synced")
            else:
                print(f"⚠️ Initial user sync failed: {result.get('message', 'unknown error')}")
    except Exception as e:
        print(f"❌ Error in initial user sync: {e}")

    # Start background user sync task
    sync_task = asyncio.create_task(_periodic_user_sync(db_manager, config.slack_bot_token))
    print("✅ Started periodic user sync task (1 hour interval)")

    yield

    # Shutdown
    print("👋 Shutting down Nakamura-Misaki...")
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass
    await db_manager.close()


# Create FastAPI app
app = FastAPI(
    title="Nakamura-Misaki",
    description="Multi-user Claude Code Agent for Slack",
    version="2.0.0-fastapi",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "nakamura-misaki", "version": "2.0.0"}


def main():
    """Run the application"""
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",  # Listen on localhost only (Tailscale proxies to localhost)
        port=config.port,
        reload=config.debug,
        log_level="debug" if config.debug else "info",
    )


if __name__ == "__main__":
    main()
