"""Session Model - Bridge pattern for Conversation migration

DEPRECATION NOTICE:
This module is a temporary bridge to support legacy code during the migration
to the new Bounded Context architecture. New code should use:
    src.contexts.conversations.domain.entities.conversation.Conversation

This bridge will be removed in a future version after complete migration.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class SessionInfo:
    """Session information - Legacy bridge for Conversation entity

    This class maintains backward compatibility with code expecting SessionInfo
    while we migrate to the new Conversation-based architecture.

    Attributes:
        session_id: Unique session identifier
        user_id: User identifier
        workspace_path: Path to user's workspace
        message_history: List of messages (role, content pairs)
        message_count: Number of messages in session
        created_at: Session creation timestamp
        last_active: Last activity timestamp
        is_active: Whether session is still active
    """

    session_id: str
    user_id: str
    workspace_path: Path
    message_history: list[dict[str, str]] = field(default_factory=list)
    message_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_active: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True

    @classmethod
    def create_new(cls, user_id: str, workspace_path: Path) -> "SessionInfo":
        """Create a new session

        Args:
            user_id: User identifier
            workspace_path: Path to user's workspace

        Returns:
            New SessionInfo instance
        """
        session_id = str(uuid.uuid4())
        return cls(
            session_id=session_id,
            user_id=user_id,
            workspace_path=workspace_path,
            message_history=[],
            message_count=0,
            created_at=datetime.now(UTC),
            last_active=datetime.now(UTC),
            is_active=True,
        )

    def update_activity(self) -> None:
        """Update last activity timestamp and increment message count"""
        self.last_active = datetime.now(UTC)
        self.message_count += 1

    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if session has expired

        Args:
            timeout_hours: Timeout threshold in hours

        Returns:
            True if session is expired, False otherwise
        """
        expiry_time = self.last_active + timedelta(hours=timeout_hours)
        return datetime.now(UTC) >= expiry_time

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "workspace_path": str(self.workspace_path),
            "message_history": self.message_history,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionInfo":
        """Create SessionInfo from dictionary

        Args:
            data: Dictionary representation of session

        Returns:
            SessionInfo instance
        """
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            workspace_path=Path(data["workspace_path"]),
            message_history=data.get("message_history", []),
            message_count=data.get("message_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"]),
            is_active=data.get("is_active", True),
        )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"SessionInfo(session_id={self.session_id[:8]}..., "
            f"user_id={self.user_id}, "
            f"message_count={self.message_count}, "
            f"is_active={self.is_active})"
        )
