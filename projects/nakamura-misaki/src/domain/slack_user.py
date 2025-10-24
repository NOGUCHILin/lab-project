"""SlackUser Entity - Shared Kernel for caching Slack user data"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SlackUser:
    """Slack user entity cached from Slack API"""

    user_id: str
    name: str
    real_name: str | None
    display_name: str | None
    email: str | None
    is_admin: bool
    is_bot: bool
    deleted: bool
    slack_created_at: datetime  # Timestamp from Slack API (user creation date)
    synced_at: datetime  # Last sync timestamp from Slack API
    created_at: datetime  # First cached timestamp in our DB
    updated_at: datetime  # Last updated timestamp in our DB
