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
# New Personal Tasks context repositories
from src.contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository as NewPostgreSQLTaskRepository,
)
# New Personal Tasks context use cases
from src.contexts.personal_tasks.application.use_cases.complete_task import CompleteTaskUseCase
from src.contexts.personal_tasks.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.contexts.personal_tasks.application.use_cases.query_due_tasks import QueryDueTasksUseCase
from src.contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from src.contexts.personal_tasks.application.use_cases.update_task import UpdateTaskUseCase


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
        self._task_repository = None
        self._conversation_repository = None

    # Repository Getters

    @property
    def task_repository(self):
        """Get TaskRepository (Personal Tasks context)"""
        if self._task_repository is None:
            self._task_repository = NewPostgreSQLTaskRepository(self._session)
        return self._task_repository

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

    def build_query_user_tasks_use_case(self) -> QueryUserTasksUseCase:
        """Build QueryUserTasksUseCase"""
        return QueryUserTasksUseCase(self.task_repository)

    def build_complete_task_use_case(self) -> CompleteTaskUseCase:
        """Build CompleteTaskUseCase"""
        return CompleteTaskUseCase(self.task_repository)

    def build_update_task_use_case(self) -> UpdateTaskUseCase:
        """Build UpdateTaskUseCase"""
        return UpdateTaskUseCase(self.task_repository)

    def build_query_due_tasks_use_case(self) -> QueryDueTasksUseCase:
        """Build QueryDueTasksUseCase"""
        return QueryDueTasksUseCase(self.task_repository)

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
            conversation_ttl_hours=conversation_ttl_hours,
        )
