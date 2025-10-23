"""FastAPI application entry point - Nakamura-Misaki v2.0

Fixed: Initialize app.state with Slack configuration for signature verification.
Fixed: Initialize slack_event_handler from DI container for message processing.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slack_sdk.web.async_client import AsyncWebClient

from .adapters.primary.api.routes import router
from .adapters.primary.dependencies import get_slack_adapter
from .infrastructure.config import AppConfig
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.logging import setup_logging

# Load configuration
config = AppConfig.from_env()
config.validate()

# Setup logging
setup_logging(debug=config.debug)


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

    yield

    # Shutdown
    print("👋 Shutting down Nakamura-Misaki...")
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
