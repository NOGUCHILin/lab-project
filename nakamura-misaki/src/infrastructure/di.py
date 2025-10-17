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

# Conversations context use cases
from src.contexts.conversations.application.use_cases.add_message import AddMessageUseCase
from src.contexts.conversations.application.use_cases.cleanup_expired_conversations import (
    CleanupExpiredConversationsUseCase,
)
from src.contexts.conversations.application.use_cases.get_or_create_conversation import (
    GetOrCreateConversationUseCase,
)

# Conversations context repositories
from src.contexts.conversations.infrastructure.repositories.postgresql_conversation_repository import (
    PostgreSQLConversationRepository as NewPostgreSQLConversationRepository,
)

# Handoffs context use cases
from src.contexts.handoffs.application.use_cases.accept_handoff import AcceptHandoffUseCase
from src.contexts.handoffs.application.use_cases.complete_handoff import (
    CompleteHandoffUseCase,
)
from src.contexts.handoffs.application.use_cases.create_handoff import CreateHandoffUseCase
from src.contexts.handoffs.application.use_cases.query_pending_handoffs import (
    QueryPendingHandoffsUseCase,
)
from src.contexts.handoffs.application.use_cases.query_user_handoffs import (
    QueryUserHandoffsUseCase,
)
from src.contexts.handoffs.application.use_cases.send_overdue_reminders import (
    SendOverdueRemindersUseCase,
)

# Handoffs context repositories
from src.contexts.handoffs.infrastructure.repositories.postgresql_handoff_repository import (
    PostgreSQLHandoffRepository,
)

# New Personal Tasks context use cases
from src.contexts.personal_tasks.application.use_cases.complete_task import CompleteTaskUseCase
from src.contexts.personal_tasks.application.use_cases.query_due_tasks import QueryDueTasksUseCase
from src.contexts.personal_tasks.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from src.contexts.personal_tasks.application.use_cases.update_task import UpdateTaskUseCase

# New Personal Tasks context repositories
from src.contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository as NewPostgreSQLTaskRepository,
)

# Workforce Management context
from src.contexts.workforce_management.application.use_cases.suggest_assignees import (
    SuggestAssigneesUseCase,
)
from src.contexts.workforce_management.infrastructure.repositories.postgresql_employee_repository import (
    PostgreSQLEmployeeRepository,
)
from src.contexts.workforce_management.infrastructure.repositories.postgresql_skill_repository import (
    PostgreSQLSkillRepository,
)


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
        self._conversation_repository = None  # Old version
        self._new_conversation_repository = None  # New Conversations Context
        self._handoff_repository = None
        self._employee_repository = None  # Workforce Management
        self._skill_repository = None  # Workforce Management

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

    @property
    def handoff_repository(self):
        """Get HandoffRepository (Handoffs context)"""
        if self._handoff_repository is None:
            self._handoff_repository = PostgreSQLHandoffRepository(self._session)
        return self._handoff_repository

    @property
    def new_conversation_repository(self):
        """Get ConversationRepository (Conversations context - new version)"""
        if self._new_conversation_repository is None:
            self._new_conversation_repository = NewPostgreSQLConversationRepository(self._session)
        return self._new_conversation_repository

    @property
    def employee_repository(self):
        """Get EmployeeRepository (Workforce Management context)"""
        if self._employee_repository is None:
            self._employee_repository = PostgreSQLEmployeeRepository(self._session)
        return self._employee_repository

    @property
    def skill_repository(self):
        """Get SkillRepository (Workforce Management context)"""
        if self._skill_repository is None:
            self._skill_repository = PostgreSQLSkillRepository(self._session)
        return self._skill_repository

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

    # Use Case Builders - Handoff

    def build_create_handoff_use_case(self) -> CreateHandoffUseCase:
        """Build CreateHandoffUseCase"""
        return CreateHandoffUseCase(self.handoff_repository)

    def build_accept_handoff_use_case(self) -> AcceptHandoffUseCase:
        """Build AcceptHandoffUseCase"""
        return AcceptHandoffUseCase(self.handoff_repository)

    def build_complete_handoff_use_case(self) -> CompleteHandoffUseCase:
        """Build CompleteHandoffUseCase"""
        return CompleteHandoffUseCase(self.handoff_repository)

    def build_query_pending_handoffs_use_case(self) -> QueryPendingHandoffsUseCase:
        """Build QueryPendingHandoffsUseCase"""
        return QueryPendingHandoffsUseCase(self.handoff_repository)

    def build_query_user_handoffs_use_case(self) -> QueryUserHandoffsUseCase:
        """Build QueryUserHandoffsUseCase"""
        return QueryUserHandoffsUseCase(self.handoff_repository)

    def build_send_overdue_reminders_use_case(self) -> SendOverdueRemindersUseCase:
        """Build SendOverdueRemindersUseCase"""
        return SendOverdueRemindersUseCase(self.handoff_repository)

    # Use Case Builders - Conversation (new Conversations Context)

    def build_get_or_create_conversation_use_case(self) -> GetOrCreateConversationUseCase:
        """Build GetOrCreateConversationUseCase"""
        return GetOrCreateConversationUseCase(self.new_conversation_repository)

    def build_add_message_use_case(self) -> AddMessageUseCase:
        """Build AddMessageUseCase"""
        return AddMessageUseCase(self.new_conversation_repository)

    def build_cleanup_expired_conversations_use_case(
        self,
    ) -> CleanupExpiredConversationsUseCase:
        """Build CleanupExpiredConversationsUseCase"""
        return CleanupExpiredConversationsUseCase(self.new_conversation_repository)

    # Use Case Builders - Workforce Management

    def build_suggest_assignees_use_case(self) -> SuggestAssigneesUseCase:
        """Build SuggestAssigneesUseCase"""
        return SuggestAssigneesUseCase(self.skill_repository)

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
            skill_repository=self.skill_repository,
            suggest_assignees_use_case=self.build_suggest_assignees_use_case(),
            conversation_ttl_hours=conversation_ttl_hours,
        )
