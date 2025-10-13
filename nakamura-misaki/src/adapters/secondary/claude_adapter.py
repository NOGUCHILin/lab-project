"""Claude Agent SDK adapter"""

from typing import List

try:
    from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query

    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    ClaudeAgentOptions = None
    query = None
    create_sdk_mcp_server = None

from ...domain.repositories.prompt_repository import PromptRepository
from ...domain.services.claude_service import ClaudeService


class ClaudeAgentAdapter(ClaudeService):
    """Claude Agent SDK implementation"""

    def __init__(
        self, prompt_repository: PromptRepository, task_tools=None, slack_tools=None
    ):
        """
        Args:
            prompt_repository: プロンプト設定リポジトリ
            task_tools: TaskTools instance for custom tools
            slack_tools: SlackTools instance for custom tools
        """
        self.prompt_repository = prompt_repository
        self.task_tools = task_tools
        self.slack_tools = slack_tools
        self.mcp_servers = {}  # 辞書形式に変更

        # Register custom tools as MCP servers
        if CLAUDE_AVAILABLE and create_sdk_mcp_server:
            if task_tools:
                task_server = create_sdk_mcp_server(
                    "task-management", task_tools.get_tools()
                )
                self.mcp_servers["task-management"] = task_server  # 辞書に追加

            if slack_tools:
                slack_server = create_sdk_mcp_server(
                    "slack-reader", slack_tools.get_tools()
                )
                self.mcp_servers["slack-reader"] = slack_server  # 辞書に追加

    async def send_message(
        self,
        user_id: str,
        message: str,
        workspace_path: str,
        session_id: str | None = None,
        continue_conversation: bool = False,
        is_dm: bool = False,
        saved_notes: str = "",
    ) -> str:
        """Send message to Claude Code"""
        if not CLAUDE_AVAILABLE or query is None or ClaudeAgentOptions is None:
            return f"Claude Code SDK is not available. Input: {message}"

        # ユーザーに適したプロンプトを取得
        prompt_config = await self.prompt_repository.get_for_user(user_id)

        # タスクコンテキストを動的に生成
        task_context = await self._generate_task_context(user_id)

        # Anthropic推奨: すべてのコンテキスト変数を埋め込む
        system_prompt = prompt_config.system_prompt
        system_prompt = system_prompt.replace("{user_id}", user_id)
        system_prompt = system_prompt.replace("{workspace_path}", workspace_path)
        system_prompt = system_prompt.replace(
            "{channel_type}", "DM" if is_dm else "Channel Mention"
        )
        system_prompt = system_prompt.replace("{task_context}", task_context)
        system_prompt = system_prompt.replace("{saved_notes}", saved_notes)

        options = ClaudeAgentOptions(
            cwd=workspace_path,
            system_prompt=system_prompt,  # 動的コンテキスト含む
            allowed_tools=["Read"],  # Read-only by default
            permission_mode="default",  # Changed from 'auto' (not supported)
            resume=session_id if continue_conversation else None,
            continue_conversation=continue_conversation,
            mcp_servers=self.mcp_servers if self.mcp_servers else None,
        )

        collected: List[str] = []

        try:
            async for reply in query(prompt=message, options=options):
                block_type = type(reply).__name__

                if block_type == "AssistantMessage" and hasattr(reply, "content"):
                    for block in getattr(reply, "content", []):
                        text = getattr(block, "text", "")
                        if text:
                            collected.append(text)

                if block_type == "ResultMessage":
                    break

        except Exception as exc:
            return f"Claude request error: {exc}"

        return "".join(collected) if collected else "No response received"

    async def _generate_task_context(self, user_id: str) -> str:
        """Generate dynamic task context for system prompt"""
        if not self.task_tools:
            return "タスクツールが利用できません"

        try:
            # Get pending and in-progress tasks for user
            from ...domain.models.task import TaskStatus

            pending_tasks = await self.task_tools.task_service.get_user_tasks(
                user_id, TaskStatus.PENDING
            )
            in_progress_tasks = await self.task_tools.task_service.get_user_tasks(
                user_id, TaskStatus.IN_PROGRESS
            )

            if not pending_tasks and not in_progress_tasks:
                return "現在タスクはありません"

            context_parts = []

            if pending_tasks:
                context_parts.append(f"### 未着手タスク ({len(pending_tasks)}件)")
                for task in pending_tasks[:5]:  # Limit to 5
                    due_str = task.due_date.strftime("%m/%d %H:%M")
                    context_parts.append(f"- [{task.id[:8]}] {task.title} (期限: {due_str})")

            if in_progress_tasks:
                context_parts.append(f"### 進行中タスク ({len(in_progress_tasks)}件)")
                for task in in_progress_tasks[:5]:  # Limit to 5
                    due_str = task.due_date.strftime("%m/%d %H:%M")
                    context_parts.append(
                        f"- [{task.id[:8]}] {task.title} (進捗: {task.progress}%, 期限: {due_str})"
                    )

            return "\n".join(context_parts)

        except Exception as e:
            return f"タスク情報取得エラー: {str(e)}"
