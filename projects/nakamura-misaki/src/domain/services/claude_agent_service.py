"""Claude Agent Service for natural language task management.

This service acts as the orchestrator for Claude Tool Use API integration,
managing conversation flow and tool execution.
"""

import logging
import time
from datetime import datetime
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types import Message as AnthropicMessage

from ...adapters.primary.tools.base_tool import BaseTool
from ...contexts.personal_tasks.domain.models.conversation import Conversation, Message, MessageRole
from ...infrastructure.metrics import get_metrics

logger = logging.getLogger(__name__)
metrics = get_metrics()

SYSTEM_PROMPT_TEMPLATE = """
あなたは中村美咲というタスク管理AIアシスタントです。草薙素子のような冷静で効率的な性格で、ユーザーのタスク管理をサポートします。

# あなたの役割

- ユーザーの自然な日本語メッセージからタスク操作の意図を理解する
- 適切なToolを呼び出してタスクを管理する
- 簡潔で的確な応答を返す

# Tool使用ガイドライン

1. **タスク登録**: 「〜をやる」「〜を作る」「〜までに〜」等の表現からタスク登録意図を検出
2. **タスク確認**: 「今日のタスク」「タスク一覧」等でlist_tasksを呼び出し
3. **タスク完了**: 「〜終わった」「〜完了」等でcomplete_taskを呼び出し
4. **タスク更新**: タスクの内容変更やタスクを他のユーザーに引き継ぐ場合はupdate_taskを呼び出し
5. **曖昧な識別子**: ユーザーがタスクを「あのレポート」等と表現した場合、list_tasksで候補を確認してから操作
6. **日時解釈**: 「明日」「来週」「3日後」等を適切にISO 8601形式に変換
7. **雑談対応**: タスク関連でない雑談にも自然に応答（Toolは呼ばない）

# 応答スタイル

- 簡潔（1-2文）
- 草薙素子風の口調（「了解した」「把握した」「確認する」等）
- タスク操作結果を明確に伝える

# 現在時刻

{current_time}
"""


class ClaudeAgentService:
    """Claude Agent Service for managing conversation with Tool Use."""

    def __init__(
        self,
        anthropic_client: AsyncAnthropic,
        tools: list[BaseTool],
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
    ):
        """Initialize ClaudeAgentService.

        Args:
            anthropic_client: Anthropic async client
            tools: List of available tools
            model: Claude model to use
            max_tokens: Maximum tokens for response
        """
        self._client = anthropic_client
        self._tools = tools
        self._tool_map = {tool.name: tool for tool in tools}
        self.model = model
        self._max_tokens = max_tokens

    async def process_message(
        self, conversation: Conversation, user_message: str
    ) -> str:
        """Process user message and return assistant response.

        This method:
        1. Adds user message to conversation
        2. Calls Claude API with conversation history and tools
        3. Handles tool use if requested by Claude
        4. Returns final text response

        Args:
            conversation: Conversation entity (will be mutated)
            user_message: User's message text

        Returns:
            str: Assistant's response text
        """
        # Add user message to conversation
        conversation.add_message(Message.user(content=user_message))

        # Build messages for Claude API
        messages = self._build_messages(conversation)

        # Build tool definitions
        tool_definitions = [tool.to_tool_definition() for tool in self._tools]

        # Build system prompt
        system_prompt = self._build_system_prompt()

        # Call Claude API
        start_time = time.time()
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=self._max_tokens,
            system=system_prompt,
            messages=messages,
            tools=tool_definitions,
        )
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Log Claude API call
        logger.info(
            "Claude API call completed",
            extra={
                "model": self.model,
                "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "response_time_ms": elapsed_ms,
                "tool_count": len(tool_definitions),
            },
        )

        # Record metrics
        metrics.increment("claude_api_calls")
        metrics.increment("claude_input_tokens", response.usage.input_tokens)
        metrics.increment("claude_output_tokens", response.usage.output_tokens)
        metrics.record_time("claude_api_response_time", elapsed_ms)

        # Handle tool use if present
        if response.stop_reason == "tool_use":
            return await self._handle_tool_use(conversation, response)

        # Extract text response
        response_text = self._extract_text_from_response(response)

        # Add assistant response to conversation
        conversation.add_message(Message.assistant(content=response_text))

        return response_text

    async def _handle_tool_use(
        self, conversation: Conversation, response: AnthropicMessage
    ) -> str:
        """Handle tool use from Claude response.

        Args:
            conversation: Current conversation
            response: Claude response with tool_use

        Returns:
            str: Final assistant response after tool execution
        """
        # Extract tool use blocks
        tool_use_blocks = [
            block for block in response.content if block.type == "tool_use"
        ]

        # Execute tools and collect results
        tool_results = []
        for tool_use in tool_use_blocks:
            tool_name = tool_use.name
            tool_input = tool_use.input
            tool_id = tool_use.id

            # Execute tool
            tool_start = time.time()
            tool = self._tool_map.get(tool_name)
            if tool:
                result = await tool.execute(**tool_input)
                success = True
            else:
                result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                success = False
            tool_elapsed_ms = int((time.time() - tool_start) * 1000)

            # Log tool execution
            logger.info(
                f"Tool executed: {tool_name}",
                extra={
                    "tool_name": tool_name,
                    "tool_id": tool_id,
                    "success": success,
                    "execution_time_ms": tool_elapsed_ms,
                },
            )

            # Record metrics
            metrics.increment(f"tool_executions.{tool_name}")
            metrics.record_time(f"tool_execution_time.{tool_name}", tool_elapsed_ms)
            if not success:
                metrics.record_error(f"tool_error.{tool_name}")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": str(result),
                }
            )

        # Build messages with tool results
        messages = self._build_messages(conversation)

        # Add assistant's tool use response
        messages.append({"role": "assistant", "content": response.content})

        # Add tool results
        messages.append({"role": "user", "content": tool_results})

        # Call Claude again with tool results
        system_prompt = self._build_system_prompt()
        tool_definitions = [tool.to_tool_definition() for tool in self._tools]

        final_response = await self._client.messages.create(
            model=self.model,
            max_tokens=self._max_tokens,
            system=system_prompt,
            messages=messages,
            tools=tool_definitions,
        )

        # Extract final text response
        response_text = self._extract_text_from_response(final_response)

        # Add assistant response to conversation (skip if empty)
        if response_text:
            conversation.add_message(Message.assistant(content=response_text))

        return response_text

    def _build_messages(self, conversation: Conversation) -> list[dict[str, Any]]:
        """Build messages array for Claude API from conversation history.

        Args:
            conversation: Conversation entity

        Returns:
            list: Messages in Claude API format
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages
        ]

    def _build_system_prompt(self) -> str:
        """Build system prompt with current time.

        Returns:
            str: System prompt with current time injected
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return SYSTEM_PROMPT_TEMPLATE.format(current_time=current_time)

    def _extract_text_from_response(self, response: AnthropicMessage) -> str:
        """Extract text content from Claude response.

        Args:
            response: Claude API response

        Returns:
            str: Extracted text content
        """
        text_blocks = [
            block.text for block in response.content if block.type == "text"
        ]
        return " ".join(text_blocks) if text_blocks else ""
