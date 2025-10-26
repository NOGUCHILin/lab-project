"""Slack Event Handler for nakamura-misaki v5.0.0

Natural language task management via Claude Agent SDK.
"""

from anthropic import AsyncAnthropic
from slack_sdk.web.async_client import AsyncWebClient

from src.adapters.primary.tools.task_tools import (
    CompleteTaskTool,
    ListTasksTool,
    RegisterTaskTool,
    UpdateTaskTool,
)
from src.adapters.primary.tools.workforce_tools import (
    FindEmployeesWithSkillTool,
    GetEmployeeSkillsTool,
    SuggestAssigneesTool,
)
from src.contexts.personal_tasks.application.use_cases.complete_task import CompleteTaskUseCase
from src.contexts.personal_tasks.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from src.contexts.personal_tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.contexts.personal_tasks.domain.repositories.conversation_repository import ConversationRepository
from src.contexts.project_management.adapters.primary.tools.project_tools import (
    AddTaskToProjectTool,
    ArchiveProjectTool,
    CreateProjectTool,
    GetProjectProgressTool,
    ListProjectsTool,
    RemoveTaskFromProjectTool,
)
from src.contexts.project_management.application.use_cases.add_task_to_project import (
    AddTaskToProjectUseCase,
)
from src.contexts.project_management.application.use_cases.archive_project import ArchiveProjectUseCase
from src.contexts.project_management.application.use_cases.create_project import CreateProjectUseCase
from src.contexts.project_management.application.use_cases.get_project_progress import (
    GetProjectProgressUseCase,
)
from src.contexts.project_management.application.use_cases.list_projects import ListProjectsUseCase
from src.contexts.project_management.application.use_cases.remove_task_from_project import (
    RemoveTaskFromProjectUseCase,
)
from src.contexts.workforce_management.application.use_cases.suggest_assignees import SuggestAssigneesUseCase
from src.contexts.workforce_management.domain.repositories.skill_repository import SkillRepository
from src.domain.services.claude_agent_service import ClaudeAgentService
from src.domain.services.conversation_manager import ConversationManager


class SlackEventHandlerV5:
    """Slack Event Handler using Claude Agent SDK for natural language understanding."""

    def __init__(
        self,
        anthropic_client: AsyncAnthropic,
        slack_client: AsyncWebClient,
        conversation_repository: ConversationRepository,
        # Personal Tasks Use Cases
        register_task_use_case: RegisterTaskUseCase,
        query_user_tasks_use_case: QueryUserTasksUseCase,
        complete_task_use_case: CompleteTaskUseCase,
        update_task_use_case: UpdateTaskUseCase,
        # Workforce Management
        skill_repository: SkillRepository,
        suggest_assignees_use_case: SuggestAssigneesUseCase,
        # Project Management Use Cases (Phase 1)
        create_project_use_case: CreateProjectUseCase,
        add_task_to_project_use_case: AddTaskToProjectUseCase,
        remove_task_from_project_use_case: RemoveTaskFromProjectUseCase,
        get_project_progress_use_case: GetProjectProgressUseCase,
        list_projects_use_case: ListProjectsUseCase,
        archive_project_use_case: ArchiveProjectUseCase,
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
            conversation_ttl_hours: Conversation TTL in hours (default 24)
        """
        self._anthropic_client = anthropic_client
        self._slack_client = slack_client

        # Personal Tasks Use Cases (stored for tool initialization per user)
        self._register_task_use_case = register_task_use_case
        self._query_user_tasks_use_case = query_user_tasks_use_case
        self._complete_task_use_case = complete_task_use_case
        self._update_task_use_case = update_task_use_case

        # Workforce Management
        self._skill_repository = skill_repository
        self._suggest_assignees_use_case = suggest_assignees_use_case

        # Project Management Use Cases (Phase 1)
        self._create_project_use_case = create_project_use_case
        self._add_task_to_project_use_case = add_task_to_project_use_case
        self._remove_task_from_project_use_case = remove_task_from_project_use_case
        self._get_project_progress_use_case = get_project_progress_use_case
        self._list_projects_use_case = list_projects_use_case
        self._archive_project_use_case = archive_project_use_case

        # Conversation Manager
        self._conversation_manager = ConversationManager(
            repository=conversation_repository,
            ttl_hours=conversation_ttl_hours,
        )

    async def handle_message(self, user_id: str, text: str, channel_id: str) -> str:
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
            # Workforce Management Tools
            FindEmployeesWithSkillTool(
                skill_repository=self._skill_repository,
            ),
            GetEmployeeSkillsTool(
                skill_repository=self._skill_repository,
            ),
            SuggestAssigneesTool(
                suggest_assignees_use_case=self._suggest_assignees_use_case,
            ),
            # Project Management Tools (Phase 1)
            CreateProjectTool(
                create_project_use_case=self._create_project_use_case,
                user_id=user_id,
            ),
            AddTaskToProjectTool(
                add_task_to_project_use_case=self._add_task_to_project_use_case,
                user_id=user_id,
            ),
            RemoveTaskFromProjectTool(
                remove_task_from_project_use_case=self._remove_task_from_project_use_case,
                user_id=user_id,
            ),
            GetProjectProgressTool(
                get_project_progress_use_case=self._get_project_progress_use_case,
                user_id=user_id,
            ),
            ListProjectsTool(
                list_projects_use_case=self._list_projects_use_case,
                user_id=user_id,
            ),
            ArchiveProjectTool(
                archive_project_use_case=self._archive_project_use_case,
                user_id=user_id,
            ),
        ]
