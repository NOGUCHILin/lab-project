"""Chat command handler"""

from dataclasses import dataclass
from pathlib import Path

from ...domain.models.session import SessionInfo
from ...domain.repositories.session_repository import SessionRepository
from ...domain.services.claude_service import ClaudeService


@dataclass
class ChatCommand:
    """Chat command"""

    user_id: str
    message: str
    workspace_path: str


@dataclass
class ChatCommandResult:
    """Chat command result"""

    response: str
    session_id: str


class ChatCommandHandler:
    """Chat command handler"""

    def __init__(
        self,
        claude_service: ClaudeService,
        session_repository: SessionRepository,
    ) -> None:
        self.claude_service = claude_service
        self.session_repository = session_repository

    async def handle(self, command: ChatCommand) -> ChatCommandResult:
        """Handle chat command"""
        # Get or create session
        session = await self.session_repository.get_latest(command.user_id)

        if session is None:
            # Create new session
            session = SessionInfo.create_new(
                command.user_id, Path(command.workspace_path)
            )
            await self.session_repository.save(session)

        # Determine if we should continue conversation
        continue_conversation = session.message_count > 0

        # Send message to Claude
        response = await self.claude_service.send_message(
            user_id=command.user_id,
            message=command.message,
            workspace_path=command.workspace_path,
            session_id=session.session_id if continue_conversation else None,
            continue_conversation=continue_conversation,
        )

        # Update session
        session.update_activity()
        await self.session_repository.save(session)

        return ChatCommandResult(response=response, session_id=session.session_id)
