"""Slack Event Handler for nakamura-misaki v4.0.0

Task management and Handoff management via Slack messages.
"""

import os
from typing import TYPE_CHECKING

from anthropic import Anthropic
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.primary import (
    HandoffCommandParser,
    HandoffResponseFormatter,
    TaskCommandParser,
    TaskResponseFormatter,
)
from src.application.dto import CreateHandoffDTO, CreateTaskDTO
from src.infrastructure.di import DIContainer

if TYPE_CHECKING:
    pass


class SlackEventHandler:
    """Slack Event Handler for Task/Handoff commands"""

    def __init__(
        self,
        session: AsyncSession,
        claude_client: Anthropic,
        slack_token: str,
    ):
        # Slack Client
        self._slack_client = AsyncWebClient(token=slack_token)

        # DI Container
        self._container = DIContainer(session, claude_client, self._slack_client)

        # Parsers
        self._task_parser = TaskCommandParser()
        self._handoff_parser = HandoffCommandParser()

        # Formatters
        self._task_formatter = TaskResponseFormatter()
        self._handoff_formatter = HandoffResponseFormatter()

    async def handle_message(self, user_id: str, text: str) -> str:
        """メッセージを解析して適切なコマンドを実行

        Args:
            user_id: Slack User ID
            text: メッセージテキスト

        Returns:
            応答メッセージ
        """
        # タスクコマンド判定
        task_cmd = self._task_parser.parse(text, user_id)
        if task_cmd:
            return await self._handle_task_command(task_cmd)

        # ハンドオフコマンド判定
        handoff_cmd = self._handoff_parser.parse(text, user_id)
        if handoff_cmd:
            return await self._handle_handoff_command(handoff_cmd)

        # 通常のチャット（既存のClaude Agent処理）
        return None  # None = 通常処理へフォールバック

    async def _handle_task_command(self, cmd) -> str:
        """タスクコマンド処理"""
        if cmd.command_type == "register":
            # タスク登録
            use_case = self._container.build_register_task_use_case()
            dto = CreateTaskDTO(
                user_id=cmd.user_id,
                title=cmd.title or "無題のタスク",
                description=cmd.description or "",
                due_at=cmd.due_at,
            )
            task = await use_case.execute(dto)
            return self._task_formatter.format_task_created(task)

        elif cmd.command_type == "list":
            # タスク一覧取得
            if cmd.status:
                use_case = self._container.build_query_user_tasks_use_case()
                tasks = await use_case.execute(cmd.user_id, status=cmd.status)
            else:
                use_case = self._container.build_query_today_tasks_use_case()
                tasks = await use_case.execute(cmd.user_id)

            return self._task_formatter.format_task_list(tasks)

        elif cmd.command_type == "complete":
            # タスク完了
            if not cmd.task_id:
                return "❌ タスクIDを指定してください"

            use_case = self._container.build_complete_task_use_case()
            task = await use_case.execute(cmd.task_id)
            return self._task_formatter.format_task_completed(task)

        return "❌ 不明なタスクコマンドです"

    async def _handle_handoff_command(self, cmd) -> str:
        """ハンドオフコマンド処理"""
        if cmd.command_type == "register":
            # ハンドオフ登録
            if not cmd.task_id:
                return "❌ タスクIDを指定してください"
            if not cmd.to_user_id:
                return "❌ 引き継ぎ先ユーザーを指定してください（例: @username）"

            use_case = self._container.build_register_handoff_use_case()
            dto = CreateHandoffDTO(
                task_id=cmd.task_id,
                from_user_id=cmd.user_id,
                to_user_id=cmd.to_user_id,
                progress_note=cmd.progress_note or "進捗メモなし",
                handoff_at=cmd.handoff_at,
            )
            handoff = await use_case.execute(dto)
            return self._handoff_formatter.format_handoff_created(handoff)

        elif cmd.command_type == "list":
            # ハンドオフ一覧取得
            use_case = self._container.build_query_handoffs_by_user_use_case()
            handoffs = await use_case.execute(cmd.user_id)
            return self._handoff_formatter.format_handoff_list(handoffs)

        elif cmd.command_type == "complete":
            # ハンドオフ完了
            if not cmd.handoff_id:
                return "❌ ハンドオフIDを指定してください"

            use_case = self._container.build_complete_handoff_use_case()
            handoff = await use_case.execute(cmd.handoff_id)
            return self._handoff_formatter.format_handoff_completed(handoff)

        return "❌ 不明なハンドオフコマンドです"
