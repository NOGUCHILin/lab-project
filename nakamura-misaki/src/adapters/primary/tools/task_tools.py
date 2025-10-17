"""Task management tools for Claude Tool Use (v6.0.0 DDD)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from src.contexts.personal_tasks.application.dto.task_dto import CreateTaskDTO, TaskDTO, UpdateTaskDTO
from src.contexts.personal_tasks.application.use_cases.complete_task import CompleteTaskUseCase
from src.contexts.personal_tasks.application.use_cases.query_user_tasks import QueryUserTasksUseCase
from src.contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from src.contexts.personal_tasks.application.use_cases.update_task import UpdateTaskUseCase
from src.shared_kernel.domain.value_objects.task_status import TaskStatus

from .base_tool import BaseTool


class RegisterTaskTool(BaseTool):
    """タスク登録Tool.

    ユーザーの新しいタスクを登録する。
    """

    def __init__(self, register_task_use_case: RegisterTaskUseCase, user_id: str):
        """Initialize RegisterTaskTool.

        Args:
            register_task_use_case: RegisterTaskUseCase instance
            user_id: Current user's Slack user ID
        """
        self._register_task_use_case = register_task_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "register_task"

    @property
    def description(self) -> str:
        return "ユーザーの新しいタスクを登録する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "タスクのタイトル",
                },
                "description": {
                    "type": "string",
                    "description": "タスクの詳細説明（任意）",
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "期限（ISO 8601形式、任意）",
                },
            },
            "required": ["title"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """タスク登録を実行.

        Args:
            title: タスクタイトル
            description: タスク説明（任意）
            due_date: 期限（ISO 8601形式、任意）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            title = kwargs["title"]
            description = kwargs.get("description")
            due_date_str = kwargs.get("due_date")

            # Parse due_date if provided
            due_at = None
            if due_date_str:
                due_at = datetime.fromisoformat(due_date_str)

            # Create DTO
            dto = CreateTaskDTO(
                title=title,
                assignee_user_id=self._user_id,
                creator_user_id=self._user_id,
                description=description,
                due_at=due_at,
            )

            # Create task via use case
            task_dto = await self._register_task_use_case.execute(dto)

            return {
                "success": True,
                "data": self._task_dto_to_dict(task_dto),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _task_dto_to_dict(self, task_dto: TaskDTO) -> dict[str, Any]:
        """Convert TaskDTO to dict for JSON serialization.

        Args:
            task_dto: TaskDTO

        Returns:
            dict: JSON-serializable task data
        """
        return {
            "id": str(task_dto.id),
            "title": task_dto.title,
            "description": task_dto.description,
            "status": task_dto.status,
            "assignee_user_id": task_dto.assignee_user_id,
            "creator_user_id": task_dto.creator_user_id,
            "due_at": task_dto.due_at.isoformat() if task_dto.due_at else None,
            "completed_at": task_dto.completed_at.isoformat() if task_dto.completed_at else None,
            "created_at": task_dto.created_at.isoformat(),
            "updated_at": task_dto.updated_at.isoformat(),
        }


class ListTasksTool(BaseTool):
    """タスク一覧取得Tool.

    ユーザーのタスク一覧を取得する。
    """

    def __init__(self, query_user_tasks_use_case: QueryUserTasksUseCase, user_id: str):
        """Initialize ListTasksTool.

        Args:
            query_user_tasks_use_case: QueryUserTasksUseCase instance
            user_id: Current user's Slack user ID
        """
        self._query_user_tasks_use_case = query_user_tasks_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "list_tasks"

    @property
    def description(self) -> str:
        return "ユーザーのタスク一覧を取得する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "フィルタするステータス（任意）",
                },
            },
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """タスク一覧を取得.

        Args:
            status: ステータスフィルタ（任意）

        Returns:
            dict: {"success": True, "data": {"tasks": [...], "count": N}}
        """
        try:
            status_str = kwargs.get("status")
            status = TaskStatus(status_str) if status_str else None

            tasks = await self._query_user_tasks_use_case.execute(
                user_id=self._user_id,
                status=status,
            )

            return {
                "success": True,
                "data": {
                    "tasks": [self._task_dto_to_dict(task) for task in tasks],
                    "count": len(tasks),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _task_dto_to_dict(self, task_dto: TaskDTO) -> dict[str, Any]:
        """Convert TaskDTO to dict.

        Args:
            task_dto: TaskDTO

        Returns:
            dict: JSON-serializable task data
        """
        return {
            "id": str(task_dto.id),
            "title": task_dto.title,
            "description": task_dto.description,
            "status": task_dto.status,
            "assignee_user_id": task_dto.assignee_user_id,
            "creator_user_id": task_dto.creator_user_id,
            "due_at": task_dto.due_at.isoformat() if task_dto.due_at else None,
            "completed_at": task_dto.completed_at.isoformat() if task_dto.completed_at else None,
            "created_at": task_dto.created_at.isoformat(),
            "updated_at": task_dto.updated_at.isoformat(),
        }


class CompleteTaskTool(BaseTool):
    """タスク完了Tool.

    タスクを完了済みにする。
    task_identifierがUUIDでない場合、タイトル部分一致で検索する。
    """

    def __init__(
        self,
        complete_task_use_case: CompleteTaskUseCase,
        query_user_tasks_use_case: QueryUserTasksUseCase,
        user_id: str,
    ):
        """Initialize CompleteTaskTool.

        Args:
            complete_task_use_case: CompleteTaskUseCase instance
            query_user_tasks_use_case: QueryUserTasksUseCase for title search
            user_id: Current user's Slack user ID
        """
        self._complete_task_use_case = complete_task_use_case
        self._query_user_tasks_use_case = query_user_tasks_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "complete_task"

    @property
    def description(self) -> str:
        return "タスクを完了済みにする"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_identifier": {
                    "type": "string",
                    "description": "タスクID（UUID）またはタスクタイトルの一部",
                },
            },
            "required": ["task_identifier"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """タスク完了を実行.

        Args:
            task_identifier: タスクIDまたはタスクタイトル

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            task_identifier = kwargs["task_identifier"]

            # Try to parse as UUID
            task_id = None
            try:
                task_id = UUID(task_identifier)
            except ValueError:
                # Not a UUID, search by title
                task_id = await self._find_task_id_by_title(task_identifier)

            if not task_id:
                return {
                    "success": False,
                    "error": f"Task not found: {task_identifier}",
                }

            # Complete task
            task_dto = await self._complete_task_use_case.execute(task_id=task_id)

            return {
                "success": True,
                "data": self._task_dto_to_dict(task_dto),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _find_task_id_by_title(self, title_part: str) -> UUID | None:
        """Find task ID by title partial match.

        Args:
            title_part: Part of task title

        Returns:
            UUID: Task ID if found, None otherwise
        """
        tasks = await self._query_user_tasks_use_case.execute(user_id=self._user_id)

        for task in tasks:
            if title_part.lower() in task.title.lower():
                return task.id

        return None

    def _task_dto_to_dict(self, task_dto: TaskDTO) -> dict[str, Any]:
        """Convert TaskDTO to dict.

        Args:
            task_dto: TaskDTO

        Returns:
            dict: JSON-serializable task data
        """
        return {
            "id": str(task_dto.id),
            "title": task_dto.title,
            "description": task_dto.description,
            "status": task_dto.status,
            "assignee_user_id": task_dto.assignee_user_id,
            "creator_user_id": task_dto.creator_user_id,
            "due_at": task_dto.due_at.isoformat() if task_dto.due_at else None,
            "completed_at": task_dto.completed_at.isoformat() if task_dto.completed_at else None,
            "created_at": task_dto.created_at.isoformat(),
            "updated_at": task_dto.updated_at.isoformat(),
        }


class UpdateTaskTool(BaseTool):
    """タスク更新Tool.

    タスクの属性（タイトル、説明、ステータス、期限）を更新する。
    """

    def __init__(self, update_task_use_case: UpdateTaskUseCase, user_id: str):
        """Initialize UpdateTaskTool.

        Args:
            update_task_use_case: UpdateTaskUseCase instance
            user_id: Current user's Slack user ID
        """
        self._update_task_use_case = update_task_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "update_task"

    @property
    def description(self) -> str:
        return "タスクを更新する（タイトル、説明、ステータス、期限）"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "タスクID（UUID）",
                },
                "title": {
                    "type": "string",
                    "description": "新しいタイトル（任意）",
                },
                "description": {
                    "type": "string",
                    "description": "新しい説明（任意）",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "新しいステータス（任意）",
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "新しい期限（ISO 8601形式、任意）",
                },
            },
            "required": ["task_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """タスク更新を実行.

        Args:
            task_id: タスクID（UUID）
            title: 新しいタイトル（任意）
            description: 新しい説明（任意）
            status: 新しいステータス（任意）
            due_date: 新しい期限（ISO 8601形式、任意）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            task_id_str = kwargs["task_id"]

            # Parse UUID
            try:
                task_id = UUID(task_id_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid task ID format: {task_id_str}",
                }

            # Parse optional due_date
            due_at = None
            due_date_str = kwargs.get("due_date")
            if due_date_str:
                due_at = datetime.fromisoformat(due_date_str)

            # Parse optional status
            status = None
            status_str = kwargs.get("status")
            if status_str:
                status = TaskStatus(status_str)

            # Create UpdateTaskDTO
            dto = UpdateTaskDTO(
                title=kwargs.get("title"),
                description=kwargs.get("description"),
                status=status,
                due_at=due_at,
            )

            # Execute use case
            task_dto = await self._update_task_use_case.execute(task_id, dto)

            return {
                "success": True,
                "data": self._task_dto_to_dict(task_dto),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _task_dto_to_dict(self, task_dto: TaskDTO) -> dict[str, Any]:
        """Convert TaskDTO to dict.

        Args:
            task_dto: TaskDTO

        Returns:
            dict: JSON-serializable task data
        """
        return {
            "id": str(task_dto.id),
            "title": task_dto.title,
            "description": task_dto.description,
            "status": task_dto.status,
            "assignee_user_id": task_dto.assignee_user_id,
            "creator_user_id": task_dto.creator_user_id,
            "due_at": task_dto.due_at.isoformat() if task_dto.due_at else None,
            "completed_at": task_dto.completed_at.isoformat() if task_dto.completed_at else None,
            "created_at": task_dto.created_at.isoformat(),
            "updated_at": task_dto.updated_at.isoformat(),
        }
