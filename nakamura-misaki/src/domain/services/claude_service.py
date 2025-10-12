"""Claude interaction domain service"""

from abc import ABC, abstractmethod


class ClaudeService(ABC):
    """Claude Code interaction service interface"""

    @abstractmethod
    async def send_message(
        self,
        user_id: str,
        message: str,
        workspace_path: str,
        session_id: str | None = None,
        continue_conversation: bool = False,
    ) -> str:
        """Send message to Claude and get response"""
        pass
