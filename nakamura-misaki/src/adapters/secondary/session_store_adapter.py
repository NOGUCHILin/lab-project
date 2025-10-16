"""JSON-based session repository implementation"""

import json
from pathlib import Path

from ...domain.models.session import SessionInfo
from ...domain.repositories.session_repository import SessionRepository


class JsonSessionRepository(SessionRepository):
    """JSON file-based session storage"""

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True, parents=True)

    def _get_user_session_file(self, user_id: str) -> Path:
        """Get user session file path"""
        return self.base_path / f"user_{user_id}_sessions.json"

    async def save(self, session: SessionInfo) -> None:
        """Save session"""
        session_file = self._get_user_session_file(session.user_id)

        # Load existing sessions
        sessions = await self.get_all_for_user(session.user_id)

        # Update session
        sessions[session.session_id] = session

        # Convert to dict format
        sessions_dict = {sid: s.to_dict() for sid, s in sessions.items()}

        # Save to file
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(sessions_dict, f, indent=2, ensure_ascii=False)

    async def get_by_id(
        self, user_id: str, session_id: str
    ) -> SessionInfo | None:
        """Get session by ID"""
        sessions = await self.get_all_for_user(user_id)
        return sessions.get(session_id)

    async def get_latest(self, user_id: str) -> SessionInfo | None:
        """Get latest active session"""
        sessions = await self.get_all_for_user(user_id)

        if not sessions:
            return None

        # Filter active sessions and get latest
        active_sessions = [s for s in sessions.values() if s.is_active]

        if not active_sessions:
            return None

        return max(active_sessions, key=lambda s: s.last_active)

    async def get_all_for_user(self, user_id: str) -> dict[str, SessionInfo]:
        """Get all sessions for user"""
        session_file = self._get_user_session_file(user_id)

        if not session_file.exists():
            return {}

        try:
            with open(session_file, encoding="utf-8") as f:
                data = json.load(f)
                return {sid: SessionInfo.from_dict(s) for sid, s in data.items()}
        except Exception as e:
            print(f"⚠️ Session load error: {e}")
            return {}

    async def cleanup_expired(self, timeout_hours: int = 24) -> None:
        """Cleanup expired sessions"""
        session_files = self.base_path.glob("user_*_sessions.json")

        for session_file in session_files:
            try:
                with open(session_file, encoding="utf-8") as f:
                    sessions_dict = json.load(f)

                updated = False
                for session_id, session_data in sessions_dict.items():
                    session = SessionInfo.from_dict(session_data)
                    if session.is_expired(timeout_hours) and session.is_active:
                        sessions_dict[session_id]["is_active"] = False
                        updated = True
                        print(f"🕐 Session expired: {session.user_id}/{session_id}")

                if updated:
                    with open(session_file, "w", encoding="utf-8") as f:
                        json.dump(sessions_dict, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"⚠️ Session cleanup error: {e}")
