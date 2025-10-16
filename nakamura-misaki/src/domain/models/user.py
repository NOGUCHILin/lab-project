"""User domain model"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .session import WorkspaceLimits


@dataclass
class UserConfig:
    """User configuration domain model"""

    user_id: str
    display_name: str = ""
    workspace_limits: WorkspaceLimits | None = None
    allowed_tools: list[str] | None = None
    auto_continue_session: bool = True
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.workspace_limits is None:
            self.workspace_limits = WorkspaceLimits()
        if self.allowed_tools is None:
            self.allowed_tools = ["Read"]  # Read-only by default
        if self.created_at is None:
            self.created_at = datetime.now()
