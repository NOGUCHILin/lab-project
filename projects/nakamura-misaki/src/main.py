"""FastAPI application entry point - Nakamura-Misaki v2.0"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .adapters.primary.api.routes import router
from .adapters.primary.dependencies import get_slack_adapter
from .infrastructure.config import AppConfig
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

    # End DND mode on startup
    slack = get_slack_adapter()
    dnd_result = await slack.end_dnd()
    if dnd_result.get("ok"):
        print("✅ おやすみモード解除完了")
    else:
        print(f"⚠️ おやすみモード解除失敗: {dnd_result.get('error', 'unknown')}")

    yield

    # Shutdown (if needed)
    print("👋 Shutting down Nakamura-Misaki...")


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


def main():
    """Run the application"""
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=config.port,
        reload=config.debug,
        log_level="debug" if config.debug else "info",
    )


if __name__ == "__main__":
    main()
