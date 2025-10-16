"""Session repository interface (port)"""

from abc import ABC, abstractmethod

from ..models.session import SessionInfo


class SessionRepository(ABC):
    """Session persistence interface"""

    @abstractmethod
    async def save(self, session: SessionInfo) -> None:
        """Save session"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str, session_id: str) -> SessionInfo | None:
        """Get session by ID"""
        pass

    @abstractmethod
    async def get_latest(self, user_id: str) -> SessionInfo | None:
        """Get latest active session"""
        pass

    @abstractmethod
    async def get_all_for_user(self, user_id: str) -> dict[str, SessionInfo]:
        """Get all sessions for user"""
        pass

    @abstractmethod
    async def cleanup_expired(self, timeout_hours: int = 24) -> None:
        """Cleanup expired sessions"""
        pass
