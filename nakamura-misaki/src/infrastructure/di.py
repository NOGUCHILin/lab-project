"""Dependency Injection Container

Application全体の依存関係を管理するコンテナ。
"""

from anthropic import Anthropic, AsyncAnthropic
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.primary.slack_event_handler import SlackEventHandlerV5
from src.adapters.secondary.postgresql_conversation_repository import (
    PostgreSQLConversationRepository,
)
from src.adapters.secondary.postgresql_handoff_repository import (
    PostgreSQLHandoffRepository,
)
from src.adapters.secondary.postgresql_note_repository import (
    PostgreSQLNoteRepository,
)
from src.adapters.secondary.postgresql_task_repository import (
    PostgreSQLTaskRepository,
)
from src.application.use_cases.complete_handoff import CompleteHandoffUseCase
from src.application.use_cases.complete_task import CompleteTaskUseCase
from src.application.use_cases.detect_bottleneck import DetectBottleneckUseCase
from src.application.use_cases.query_handoffs_by_user import (
    QueryHandoffsByUserUseCase,
)
from src.application.use_cases.query_team_stats import QueryTeamStatsUseCase
from src.application.use_cases.query_today_tasks import QueryTodayTasksUseCase
from src.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.application.use_cases.register_handoff import RegisterHandoffUseCase
from src.application.use_cases.register_task import RegisterTaskUseCase
from src.application.use_cases.send_handoff_reminder import SendHandoffReminderUseCase
from src.application.use_cases.update_task import UpdateTaskUseCase


class DIContainer:
    """DI Container"""

    def __init__(
        self,
        session: AsyncSession,
        claude_client: Anthropic,
        slack_client: AsyncWebClient,
    ):
        self._session = session
        self._claude_client = claude_client
        self._slack_client = slack_client

        # リポジトリ
        self._note_repository = None
        self._task_repository = None
        self._handoff_repository = None
        self._conversation_repository = None

    # Repository Getters

    @property
    def note_repository(self):
        """Get NoteRepository"""
        if self._note_repository is None:
            self._note_repository = PostgreSQLNoteRepository(
                self._session, self._claude_client
            )
        return self._note_repository

    @property
    def task_repository(self):
        """Get TaskRepository"""
        if self._task_repository is None:
            self._task_repository = PostgreSQLTaskRepository(self._session)
        return self._task_repository

    @property
    def handoff_repository(self):
        """Get HandoffRepository"""
        if self._handoff_repository is None:
            self._handoff_repository = PostgreSQLHandoffRepository(self._session)
        return self._handoff_repository

    @property
    def conversation_repository(self):
        """Get ConversationRepository"""
        if self._conversation_repository is None:
            self._conversation_repository = PostgreSQLConversationRepository(self._session)
        return self._conversation_repository

    # Use Case Builders - Task

    def build_register_task_use_case(self) -> RegisterTaskUseCase:
        """Build RegisterTaskUseCase"""
        return RegisterTaskUseCase(self.task_repository)

    def build_query_today_tasks_use_case(self) -> QueryTodayTasksUseCase:
        """Build QueryTodayTasksUseCase"""
        return QueryTodayTasksUseCase(self.task_repository)

    def build_query_user_tasks_use_case(self) -> QueryUserTasksUseCase:
        """Build QueryUserTasksUseCase"""
        return QueryUserTasksUseCase(self.task_repository)

    def build_complete_task_use_case(self) -> CompleteTaskUseCase:
        """Build CompleteTaskUseCase"""
        return CompleteTaskUseCase(self.task_repository)

    def build_update_task_use_case(self) -> UpdateTaskUseCase:
        """Build UpdateTaskUseCase"""
        return UpdateTaskUseCase(self.task_repository)

    # Use Case Builders - Handoff

    def build_register_handoff_use_case(self) -> RegisterHandoffUseCase:
        """Build RegisterHandoffUseCase"""
        return RegisterHandoffUseCase(self.handoff_repository)

    def build_query_handoffs_by_user_use_case(self) -> QueryHandoffsByUserUseCase:
        """Build QueryHandoffsByUserUseCase"""
        return QueryHandoffsByUserUseCase(self.handoff_repository)

    def build_complete_handoff_use_case(self) -> CompleteHandoffUseCase:
        """Build CompleteHandoffUseCase"""
        return CompleteHandoffUseCase(self.handoff_repository)

    def build_send_handoff_reminder_use_case(self) -> SendHandoffReminderUseCase:
        """Build SendHandoffReminderUseCase"""
        # Slack Client wrapper
        class SlackClientWrapper:
            def __init__(self, client):
                self._client = client

            async def send_dm(self, user_id: str, message: str):
                await self._client.chat_postMessage(
                    channel=user_id,
                    text=message,
                    unfurl_links=False,
                    unfurl_media=False,
                )

        slack_wrapper = SlackClientWrapper(self._slack_client)
        return SendHandoffReminderUseCase(self.handoff_repository, slack_wrapper)

    # Use Case Builders - Team Hub

    def build_detect_bottleneck_use_case(self) -> DetectBottleneckUseCase:
        """Build DetectBottleneckUseCase"""
        return DetectBottleneckUseCase(self.task_repository)

    def build_query_team_stats_use_case(self) -> QueryTeamStatsUseCase:
        """Build QueryTeamStatsUseCase"""
        return QueryTeamStatsUseCase(self.task_repository)

    # SlackEventHandler v5.0.0

    def build_slack_event_handler(
        self, anthropic_api_key: str, conversation_ttl_hours: int = 24
    ) -> SlackEventHandlerV5:
        """Build SlackEventHandlerV5 for v5.0.0.

        Args:
            anthropic_api_key: Anthropic API key
            conversation_ttl_hours: Conversation TTL in hours

        Returns:
            SlackEventHandlerV5: Event handler instance
        """
        # Create AsyncAnthropic client
        anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)

        return SlackEventHandlerV5(
            anthropic_client=anthropic_client,
            slack_client=self._slack_client,
            conversation_repository=self.conversation_repository,
            register_task_use_case=self.build_register_task_use_case(),
            query_user_tasks_use_case=self.build_query_user_tasks_use_case(),
            complete_task_use_case=self.build_complete_task_use_case(),
            update_task_use_case=self.build_update_task_use_case(),
            register_handoff_use_case=self.build_register_handoff_use_case(),
            query_handoffs_use_case=self.build_query_handoffs_by_user_use_case(),
            complete_handoff_use_case=self.build_complete_handoff_use_case(),
            conversation_ttl_hours=conversation_ttl_hours,
        )
