"""Slack Event Handler for nakamura-misaki v5.0.0

Natural language task management via Claude Agent SDK.
"""

from anthropic import AsyncAnthropic
from slack_sdk.web.async_client import AsyncWebClient

from ...adapters.primary.tools.handoff_tools import (
    CompleteHandoffTool,
    ListHandoffsTool,
    RegisterHandoffTool,
)
from ...adapters.primary.tools.task_tools import (
    CompleteTaskTool,
    ListTasksTool,
    RegisterTaskTool,
    UpdateTaskTool,
)
from ...application.use_cases.complete_handoff import CompleteHandoffUseCase
from ...application.use_cases.complete_task import CompleteTaskUseCase
from ...application.use_cases.query_handoffs_by_user import QueryHandoffsByUserUseCase
from ...application.use_cases.query_user_tasks import QueryUserTasksUseCase
from ...application.use_cases.register_handoff import RegisterHandoffUseCase
from ...application.use_cases.register_task import RegisterTaskUseCase
from ...application.use_cases.update_task import UpdateTaskUseCase
from ...domain.repositories.conversation_repository import ConversationRepository
from ...domain.services.claude_agent_service import ClaudeAgentService
from ...domain.services.conversation_manager import ConversationManager


class SlackEventHandlerV5:
    """Slack Event Handler using Claude Agent SDK for natural language understanding."""

    def __init__(
        self,
        anthropic_client: AsyncAnthropic,
        slack_client: AsyncWebClient,
        conversation_repository: ConversationRepository,
        # Use Cases
        register_task_use_case: RegisterTaskUseCase,
        query_user_tasks_use_case: QueryUserTasksUseCase,
        complete_task_use_case: CompleteTaskUseCase,
        update_task_use_case: UpdateTaskUseCase,
        register_handoff_use_case: RegisterHandoffUseCase,
        query_handoffs_use_case: QueryHandoffsByUserUseCase,
        complete_handoff_use_case: CompleteHandoffUseCase,
        conversation_ttl_hours: int = 24,
    ):
        """Initialize SlackEventHandlerV5.

        Args:
            anthropic_client: Anthropic async client
            slack_client: Slack async client
            conversation_repository: Conversation repository
            register_task_use_case: RegisterTaskUseCase instance
            query_user_tasks_use_case: QueryUserTasksUseCase instance
            complete_task_use_case: CompleteTaskUseCase instance
            update_task_use_case: UpdateTaskUseCase instance
            register_handoff_use_case: RegisterHandoffUseCase instance
            query_handoffs_use_case: QueryHandoffsByUserUseCase instance
            complete_handoff_use_case: CompleteHandoffUseCase instance
            conversation_ttl_hours: Conversation TTL in hours (default 24)
        """
        self._anthropic_client = anthropic_client
        self._slack_client = slack_client

        # Use Cases (stored for tool initialization per user)
        self._register_task_use_case = register_task_use_case
        self._query_user_tasks_use_case = query_user_tasks_use_case
        self._complete_task_use_case = complete_task_use_case
        self._update_task_use_case = update_task_use_case
        self._register_handoff_use_case = register_handoff_use_case
        self._query_handoffs_use_case = query_handoffs_use_case
        self._complete_handoff_use_case = complete_handoff_use_case

        # Conversation Manager
        self._conversation_manager = ConversationManager(
            repository=conversation_repository,
            ttl_hours=conversation_ttl_hours,
        )

    async def handle_message(
        self, user_id: str, text: str, channel_id: str
    ) -> str:
        """Handle Slack message with Claude Agent.

        Args:
            user_id: Slack User ID
            text: Message text
            channel_id: Slack Channel ID

        Returns:
            Response message text
        """
        # Get or create conversation (without initial message)
        # process_message will add the user message
        conversation = await self._conversation_manager.get_or_create(
            user_id=user_id,
            channel_id=channel_id,
            initial_message=None,
        )

        # Build tools for this user
        tools = self._build_tools_for_user(user_id)

        # Create Claude Agent Service
        claude_agent = ClaudeAgentService(
            anthropic_client=self._anthropic_client,
            tools=tools,
        )

        # Process message (adds user message + assistant response)
        response_text = await claude_agent.process_message(
            conversation=conversation,
            user_message=text,
        )

        # Save updated conversation
        await self._conversation_manager.save(conversation)

        return response_text

    def _build_tools_for_user(self, user_id: str) -> list:
        """Build tool instances for a specific user.

        Args:
            user_id: Slack User ID

        Returns:
            list: Tool instances
        """
        return [
            # Task Tools
            RegisterTaskTool(
                register_task_use_case=self._register_task_use_case,
                user_id=user_id,
            ),
            ListTasksTool(
                query_user_tasks_use_case=self._query_user_tasks_use_case,
                user_id=user_id,
            ),
            CompleteTaskTool(
                complete_task_use_case=self._complete_task_use_case,
                query_user_tasks_use_case=self._query_user_tasks_use_case,
                user_id=user_id,
            ),
            UpdateTaskTool(
                update_task_use_case=self._update_task_use_case,
                user_id=user_id,
            ),
            # Handoff Tools
            RegisterHandoffTool(
                register_handoff_use_case=self._register_handoff_use_case,
                user_id=user_id,
            ),
            ListHandoffsTool(
                query_handoffs_use_case=self._query_handoffs_use_case,
                user_id=user_id,
            ),
            CompleteHandoffTool(
                complete_handoff_use_case=self._complete_handoff_use_case,
                user_id=user_id,
            ),
        ]
