"""Dependency Injection Container

Application全体の依存関係を管理するコンテナ。
"""

from anthropic import Anthropic, AsyncAnthropic
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.primary.slack_event_handler import SlackEventHandlerV5

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
from src.contexts.personal_tasks.infrastructure.repositories.postgresql_conversation_repository import (
    PostgreSQLConversationRepository,
)

# New Personal Tasks context repositories
from src.contexts.personal_tasks.infrastructure.repositories.postgresql_task_repository import (
    PostgreSQLTaskRepository as NewPostgreSQLTaskRepository,
)

# Project Management context (Phase 1)
from src.contexts.project_management.application.use_cases.add_task_to_project import (
    AddTaskToProjectUseCase,
)
from src.contexts.project_management.application.use_cases.archive_project import (
    ArchiveProjectUseCase,
)
from src.contexts.project_management.application.use_cases.create_project import (
    CreateProjectUseCase,
)
from src.contexts.project_management.application.use_cases.get_project_progress import (
    GetProjectProgressUseCase,
)
from src.contexts.project_management.application.use_cases.list_projects import (
    ListProjectsUseCase,
)
from src.contexts.project_management.application.use_cases.remove_task_from_project import (
    RemoveTaskFromProjectUseCase,
)
from src.contexts.project_management.infrastructure.repositories.postgresql_project_repository import (
    PostgreSQLProjectRepository,
)

# Task Dependencies context (Phase 2)
from src.contexts.task_dependencies.application.use_cases.add_task_dependency import (
    AddTaskDependencyUseCase,
)
from src.contexts.task_dependencies.application.use_cases.can_start_task import (
    CanStartTaskUseCase,
)
from src.contexts.task_dependencies.application.use_cases.check_task_blockers import (
    CheckTaskBlockersUseCase,
)
from src.contexts.task_dependencies.application.use_cases.get_dependency_chain import (
    GetDependencyChainUseCase,
)
from src.contexts.task_dependencies.application.use_cases.remove_task_dependency import (
    RemoveTaskDependencyUseCase,
)
from src.contexts.task_dependencies.infrastructure.repositories.postgresql_dependency_repository import (
    PostgreSQLDependencyRepository,
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
        slack_client: AsyncWebClient,
        claude_client: Anthropic | None = None,
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
        self._project_repository = None  # Project Management (Phase 1)
        self._dependency_repository = None  # Task Dependencies (Phase 2)

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

    @property
    def project_repository(self):
        """Get ProjectRepository (Project Management context - Phase 1)"""
        if self._project_repository is None:
            self._project_repository = PostgreSQLProjectRepository(self._session)
        return self._project_repository

    @property
    def dependency_repository(self):
        """Get DependencyRepository (Task Dependencies context - Phase 2)"""
        if self._dependency_repository is None:
            self._dependency_repository = PostgreSQLDependencyRepository(self._session)
        return self._dependency_repository

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

    # Use Case Builders - Project Management (Phase 1)

    def build_create_project_use_case(self) -> CreateProjectUseCase:
        """Build CreateProjectUseCase"""
        return CreateProjectUseCase(self.project_repository)

    def build_add_task_to_project_use_case(self) -> AddTaskToProjectUseCase:
        """Build AddTaskToProjectUseCase"""
        return AddTaskToProjectUseCase(
            project_repository=self.project_repository,
            task_repository=self.task_repository,
        )

    def build_remove_task_from_project_use_case(self) -> RemoveTaskFromProjectUseCase:
        """Build RemoveTaskFromProjectUseCase"""
        return RemoveTaskFromProjectUseCase(self.project_repository)

    def build_get_project_progress_use_case(self) -> GetProjectProgressUseCase:
        """Build GetProjectProgressUseCase"""
        return GetProjectProgressUseCase(
            project_repository=self.project_repository,
            task_repository=self.task_repository,
        )

    def build_list_projects_use_case(self) -> ListProjectsUseCase:
        """Build ListProjectsUseCase"""
        return ListProjectsUseCase(self.project_repository)

    def build_archive_project_use_case(self) -> ArchiveProjectUseCase:
        """Build ArchiveProjectUseCase"""
        return ArchiveProjectUseCase(self.project_repository)

    # Use Case Builders - Task Dependencies (Phase 2)

    def build_add_task_dependency_use_case(self) -> AddTaskDependencyUseCase:
        """Build AddTaskDependencyUseCase"""
        return AddTaskDependencyUseCase(
            dependency_repository=self.dependency_repository,
            task_repository=self.task_repository,
        )

    def build_remove_task_dependency_use_case(self) -> RemoveTaskDependencyUseCase:
        """Build RemoveTaskDependencyUseCase"""
        return RemoveTaskDependencyUseCase(self.dependency_repository)

    def build_check_task_blockers_use_case(self) -> CheckTaskBlockersUseCase:
        """Build CheckTaskBlockersUseCase"""
        return CheckTaskBlockersUseCase(self.dependency_repository)

    def build_can_start_task_use_case(self) -> CanStartTaskUseCase:
        """Build CanStartTaskUseCase"""
        return CanStartTaskUseCase(self.dependency_repository)

    def build_get_dependency_chain_use_case(self) -> GetDependencyChainUseCase:
        """Build GetDependencyChainUseCase"""
        return GetDependencyChainUseCase(self.dependency_repository)

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
            # Personal Tasks use cases
            register_task_use_case=self.build_register_task_use_case(),
            query_user_tasks_use_case=self.build_query_user_tasks_use_case(),
            complete_task_use_case=self.build_complete_task_use_case(),
            update_task_use_case=self.build_update_task_use_case(),
            # Workforce Management
            skill_repository=self.skill_repository,
            suggest_assignees_use_case=self.build_suggest_assignees_use_case(),
            # Project Management (Phase 1)
            create_project_use_case=self.build_create_project_use_case(),
            add_task_to_project_use_case=self.build_add_task_to_project_use_case(),
            remove_task_from_project_use_case=self.build_remove_task_from_project_use_case(),
            get_project_progress_use_case=self.build_get_project_progress_use_case(),
            list_projects_use_case=self.build_list_projects_use_case(),
            archive_project_use_case=self.build_archive_project_use_case(),
            conversation_ttl_hours=conversation_ttl_hours,
        )


# Global DI container instance
_di_container_instance: DIContainer | None = None


def get_di_container() -> DIContainer:
    """Get global DI container instance

    Returns:
        DIContainer: Global DI container instance

    Raises:
        RuntimeError: If DI container has not been initialized
    """
    if _di_container_instance is None:
        raise RuntimeError("DI container has not been initialized. " "Call initialize_di_container() first.")
    return _di_container_instance


def initialize_di_container(
    session: AsyncSession,
    slack_client: AsyncWebClient,
) -> DIContainer:
    """Initialize global DI container

    Args:
        session: SQLAlchemy async session
        slack_client: Slack async web client

    Returns:
        DIContainer: Initialized DI container
    """
    global _di_container_instance
    _di_container_instance = DIContainer(session, slack_client)
    return _di_container_instance
