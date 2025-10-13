"""Chat command handler"""

from dataclasses import dataclass
from pathlib import Path

from ...domain.models.session import SessionInfo
from ...domain.repositories.session_repository import SessionRepository
from ...domain.services.claude_service import ClaudeService
from ...infrastructure.context_manager import ContextManager
from ...infrastructure.note_store import NoteStore


@dataclass
class ChatCommand:
    """Chat command"""

    user_id: str
    message: str
    workspace_path: str
    is_dm: bool = False  # Anthropic Context Engineering: チャネルタイプ情報


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
        self.context_manager = ContextManager()  # Anthropic Context Compaction

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

        # Anthropic Structured Note-Taking: Initialize note store
        note_store = NoteStore(command.workspace_path)

        # Anthropic Context Compaction: メッセージ履歴に追加
        if session.message_history is None:
            session.message_history = []

        session.message_history.append({
            "role": "user",
            "content": command.message
        })

        # Anthropic Context Compaction: 必要に応じてコンテキスト圧縮
        compressed_history, was_compressed = await self.context_manager.compress_if_needed(
            command.user_id, session.message_history
        )

        if was_compressed:
            # 圧縮された履歴を保存
            session.message_history = compressed_history
            print(f"✂️ User {command.user_id}: Context compressed")

        # Anthropic Structured Note-Taking: 過去のノートを取得
        saved_notes = await note_store.retrieve_notes(command.user_id, limit=5)

        # Determine if we should continue conversation
        continue_conversation = session.message_count > 0

        # Send message to Claude
        response = await self.claude_service.send_message(
            user_id=command.user_id,
            message=command.message,
            workspace_path=command.workspace_path,
            session_id=session.session_id if continue_conversation else None,
            continue_conversation=continue_conversation,
            is_dm=command.is_dm,  # Anthropic Context Engineering: チャネルタイプを渡す
            saved_notes=saved_notes,  # Anthropic Structured Note-Taking: セッション間記憶
        )

        # Anthropic Context Compaction: Claudeの応答を履歴に追加
        session.message_history.append({
            "role": "assistant",
            "content": response
        })

        # Update session
        session.update_activity()
        await self.session_repository.save(session)

        return ChatCommandResult(response=response, session_id=session.session_id)
