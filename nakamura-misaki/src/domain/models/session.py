"""Session domain model"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class WorkspaceLimits:
    """Workspace resource limits"""

    max_disk_mb: int = 100
    max_files: int = 1000
    max_sessions: int = 10
    session_timeout_hours: int = 24


@dataclass
class SessionInfo:
    """Session information domain model"""

    user_id: str
    session_id: str
    created_at: datetime
    last_active: datetime
    title: str = ""
    message_count: int = 0
    workspace_path: str = ""
    claude_options: dict | None = None
    is_active: bool = True
    message_history: list[dict] | None = None  # Anthropic Context Compaction用

    def __post_init__(self) -> None:
        if self.claude_options is None:
            self.claude_options = {}
        if self.message_history is None:
            self.message_history = []

    @classmethod
    def create_new(cls, user_id: str, workspace_path: Path) -> SessionInfo:
        """Create new session"""
        now = datetime.now()
        return cls(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            created_at=now,
            last_active=now,
            title=f"Session {now.strftime('%m/%d %H:%M')}",
            workspace_path=str(workspace_path),
        )

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_active = datetime.now()
        self.message_count += 1

    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if session is expired"""
        timeout = timedelta(hours=timeout_hours)
        return datetime.now() - self.last_active > timeout

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_active"] = self.last_active.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> SessionInfo:
        """Restore from dictionary"""
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data["last_active"], str):
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        return cls(**data)
