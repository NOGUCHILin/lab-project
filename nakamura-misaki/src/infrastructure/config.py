"""Application configuration"""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration"""

    port: int
    slack_bot_token: str
    nakamura_user_id: str
    debug: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables"""
        return cls(
            port=int(os.getenv("PORT", "8010")),
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            nakamura_user_id=os.getenv("NAKAMURA_USER_ID", ""),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    def validate(self) -> None:
        """Validate required configuration"""
        if not self.slack_bot_token:
            raise RuntimeError("SLACK_BOT_TOKEN environment variable is required")
        if not self.nakamura_user_id:
            raise RuntimeError("NAKAMURA_USER_ID environment variable is required")
