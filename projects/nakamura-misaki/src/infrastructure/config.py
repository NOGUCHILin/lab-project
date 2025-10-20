"""Application configuration"""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration"""

    port: int
    slack_bot_token: str
    slack_signing_secret: str
    anthropic_api_key: str
    database_url: str
    nakamura_user_id: str
    conversation_ttl_hours: int = 24
    debug: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables"""
        return cls(
            port=int(os.getenv("PORT", "8010")),
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            database_url=os.getenv("DATABASE_URL", ""),
            nakamura_user_id=os.getenv("NAKAMURA_USER_ID", ""),
            conversation_ttl_hours=int(os.getenv("CONVERSATION_TTL_HOURS", "24")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    def validate(self) -> None:
        """Validate required configuration"""
        if not self.slack_bot_token:
            raise RuntimeError("SLACK_BOT_TOKEN environment variable is required")
        if not self.slack_signing_secret:
            raise RuntimeError("SLACK_SIGNING_SECRET environment variable is required")
        if not self.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is required")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL environment variable is required")
        if not self.nakamura_user_id:
            raise RuntimeError("NAKAMURA_USER_ID environment variable is required")
