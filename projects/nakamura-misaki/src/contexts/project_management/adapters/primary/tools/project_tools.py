"""Project management tools for Claude Tool Use (Phase 1)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from src.adapters.primary.tools.base_tool import BaseTool

from ....application.dto.project_dto import CreateProjectDTO, ProjectDTO, ProjectProgressDTO
from ....application.use_cases.add_task_to_project import AddTaskToProjectUseCase
from ....application.use_cases.archive_project import ArchiveProjectUseCase
from ....application.use_cases.create_project import CreateProjectUseCase
from ....application.use_cases.get_project_progress import GetProjectProgressUseCase
from ....application.use_cases.list_projects import ListProjectsUseCase
from ....application.use_cases.remove_task_from_project import RemoveTaskFromProjectUseCase
from ....domain.value_objects.project_status import ProjectStatus


class CreateProjectTool(BaseTool):
    """プロジェクト作成Tool.

    新しいプロジェクトを作成する。
    """

    def __init__(self, create_project_use_case: CreateProjectUseCase, user_id: str):
        """Initialize CreateProjectTool.

        Args:
            create_project_use_case: CreateProjectUseCase instance
            user_id: Current user's Slack user ID
        """
        self._create_project_use_case = create_project_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "create_project"

    @property
    def description(self) -> str:
        return "新しいプロジェクトを作成する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "プロジェクト名",
                },
                "description": {
                    "type": "string",
                    "description": "プロジェクトの説明（任意）",
                },
                "deadline": {
                    "type": "string",
                    "format": "date-time",
                    "description": "プロジェクト期限（ISO 8601形式、任意）",
                },
                "owner_user_id": {
                    "type": "string",
                    "description": "オーナーのSlack User ID（任意、未指定の場合は現在のユーザー）",
                },
            },
            "required": ["name"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """プロジェクト作成を実行.

        Args:
            name: プロジェクト名
            description: プロジェクト説明（任意）
            deadline: プロジェクト期限（ISO 8601形式、任意）
            owner_user_id: オーナーのSlack User ID（任意）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            name = kwargs["name"]
            description = kwargs.get("description")
            owner_user_id = kwargs.get("owner_user_id", self._user_id)
            deadline_str = kwargs.get("deadline")

            # Parse deadline if provided
            deadline = None
            if deadline_str:
                deadline = datetime.fromisoformat(deadline_str)

            # Create DTO
            dto = CreateProjectDTO(
                name=name,
                owner_user_id=owner_user_id,
                description=description,
                deadline=deadline,
            )

            # Create project via use case
            project_dto = await self._create_project_use_case.execute(dto)

            return {
                "success": True,
                "data": self._project_dto_to_dict(project_dto),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _project_dto_to_dict(self, project_dto: ProjectDTO) -> dict[str, Any]:
        """Convert ProjectDTO to dict for JSON serialization.

        Args:
            project_dto: ProjectDTO

        Returns:
            dict: JSON-serializable project data
        """
        return {
            "project_id": str(project_dto.project_id),
            "name": project_dto.name,
            "description": project_dto.description,
            "owner_user_id": project_dto.owner_user_id,
            "status": project_dto.status,
            "deadline": project_dto.deadline.isoformat() if project_dto.deadline else None,
            "task_count": project_dto.task_count,
            "completed_task_count": project_dto.completed_task_count,
            "created_at": project_dto.created_at.isoformat(),
            "updated_at": project_dto.updated_at.isoformat(),
        }


class AddTaskToProjectTool(BaseTool):
    """プロジェクトにタスク追加Tool.

    既存のプロジェクトにタスクを追加する。
    """

    def __init__(self, add_task_to_project_use_case: AddTaskToProjectUseCase, user_id: str):
        """Initialize AddTaskToProjectTool.

        Args:
            add_task_to_project_use_case: AddTaskToProjectUseCase instance
            user_id: Current user's Slack user ID
        """
        self._add_task_to_project_use_case = add_task_to_project_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "add_task_to_project"

    @property
    def description(self) -> str:
        return "既存のプロジェクトにタスクを追加する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "プロジェクトID（UUID）",
                },
                "task_id": {
                    "type": "string",
                    "description": "タスクID（UUID）",
                },
            },
            "required": ["project_id", "task_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """タスク追加を実行.

        Args:
            project_id: プロジェクトID（UUID）
            task_id: タスクID（UUID）

        Returns:
            dict: {"success": True} or {"success": False, "error": "..."}
        """
        try:
            project_id_str = kwargs["project_id"]
            task_id_str = kwargs["task_id"]

            # Parse UUIDs
            try:
                project_id = UUID(project_id_str)
                task_id = UUID(task_id_str)
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Invalid UUID format: {e}",
                }

            # Execute use case
            await self._add_task_to_project_use_case.execute(
                project_id=project_id,
                task_id=task_id,
            )

            return {
                "success": True,
                "message": f"Task {task_id} added to project {project_id}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class RemoveTaskFromProjectTool(BaseTool):
    """プロジェクトからタスク削除Tool.

    プロジェクトからタスクを削除する。
    """

    def __init__(self, remove_task_from_project_use_case: RemoveTaskFromProjectUseCase, user_id: str):
        """Initialize RemoveTaskFromProjectTool.

        Args:
            remove_task_from_project_use_case: RemoveTaskFromProjectUseCase instance
            user_id: Current user's Slack user ID
        """
        self._remove_task_from_project_use_case = remove_task_from_project_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "remove_task_from_project"

    @property
    def description(self) -> str:
        return "プロジェクトからタスクを削除する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "プロジェクトID（UUID）",
                },
                "task_id": {
                    "type": "string",
                    "description": "タスクID（UUID）",
                },
            },
            "required": ["project_id", "task_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """タスク削除を実行.

        Args:
            project_id: プロジェクトID（UUID）
            task_id: タスクID（UUID）

        Returns:
            dict: {"success": True} or {"success": False, "error": "..."}
        """
        try:
            project_id_str = kwargs["project_id"]
            task_id_str = kwargs["task_id"]

            # Parse UUIDs
            try:
                project_id = UUID(project_id_str)
                task_id = UUID(task_id_str)
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Invalid UUID format: {e}",
                }

            # Execute use case
            await self._remove_task_from_project_use_case.execute(
                project_id=project_id,
                task_id=task_id,
            )

            return {
                "success": True,
                "message": f"Task {task_id} removed from project {project_id}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class GetProjectProgressTool(BaseTool):
    """プロジェクト進捗取得Tool.

    プロジェクトの進捗状況を取得する。
    """

    def __init__(self, get_project_progress_use_case: GetProjectProgressUseCase, user_id: str):
        """Initialize GetProjectProgressTool.

        Args:
            get_project_progress_use_case: GetProjectProgressUseCase instance
            user_id: Current user's Slack user ID
        """
        self._get_project_progress_use_case = get_project_progress_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "get_project_progress"

    @property
    def description(self) -> str:
        return "プロジェクトの進捗状況を取得する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "プロジェクトID（UUID）",
                },
            },
            "required": ["project_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """進捗取得を実行.

        Args:
            project_id: プロジェクトID（UUID）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            project_id_str = kwargs["project_id"]

            # Parse UUID
            try:
                project_id = UUID(project_id_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid UUID format: {project_id_str}",
                }

            # Execute use case
            progress_dto = await self._get_project_progress_use_case.execute(project_id)

            return {
                "success": True,
                "data": self._progress_dto_to_dict(progress_dto),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _progress_dto_to_dict(self, progress_dto: ProjectProgressDTO) -> dict[str, Any]:
        """Convert ProjectProgressDTO to dict for JSON serialization.

        Args:
            progress_dto: ProjectProgressDTO

        Returns:
            dict: JSON-serializable progress data
        """
        return {
            "project_id": str(progress_dto.project_id),
            "name": progress_dto.name,
            "total_tasks": progress_dto.total_tasks,
            "completed_tasks": progress_dto.completed_tasks,
            "in_progress_tasks": progress_dto.in_progress_tasks,
            "pending_tasks": progress_dto.pending_tasks,
            "completion_percentage": progress_dto.completion_percentage,
            "status": progress_dto.status,
            "deadline": progress_dto.deadline.isoformat() if progress_dto.deadline else None,
        }


class ListProjectsTool(BaseTool):
    """プロジェクト一覧取得Tool.

    ユーザーのプロジェクト一覧を取得する。
    """

    def __init__(self, list_projects_use_case: ListProjectsUseCase, user_id: str):
        """Initialize ListProjectsTool.

        Args:
            list_projects_use_case: ListProjectsUseCase instance
            user_id: Current user's Slack user ID
        """
        self._list_projects_use_case = list_projects_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "list_projects"

    @property
    def description(self) -> str:
        return "ユーザーのプロジェクト一覧を取得する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "owner_user_id": {
                    "type": "string",
                    "description": "オーナーのSlack User ID（任意、未指定の場合は現在のユーザー）",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "completed", "archived"],
                    "description": "フィルタするステータス（任意）",
                },
            },
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """プロジェクト一覧を取得.

        Args:
            owner_user_id: オーナーのSlack User ID（任意）
            status: ステータスフィルタ（任意）

        Returns:
            dict: {"success": True, "data": {"projects": [...], "count": N}}
        """
        try:
            owner_user_id = kwargs.get("owner_user_id", self._user_id)
            status_str = kwargs.get("status")
            status = ProjectStatus(status_str) if status_str else None

            projects = await self._list_projects_use_case.execute(
                owner_user_id=owner_user_id,
                status=status,
            )

            return {
                "success": True,
                "data": {
                    "projects": [self._project_dto_to_dict(p) for p in projects],
                    "count": len(projects),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _project_dto_to_dict(self, project_dto: ProjectDTO) -> dict[str, Any]:
        """Convert ProjectDTO to dict.

        Args:
            project_dto: ProjectDTO

        Returns:
            dict: JSON-serializable project data
        """
        return {
            "project_id": str(project_dto.project_id),
            "name": project_dto.name,
            "description": project_dto.description,
            "owner_user_id": project_dto.owner_user_id,
            "status": project_dto.status,
            "deadline": project_dto.deadline.isoformat() if project_dto.deadline else None,
            "task_count": project_dto.task_count,
            "completed_task_count": project_dto.completed_task_count,
            "created_at": project_dto.created_at.isoformat(),
            "updated_at": project_dto.updated_at.isoformat(),
        }


class ArchiveProjectTool(BaseTool):
    """プロジェクトアーカイブTool.

    プロジェクトをアーカイブする。
    """

    def __init__(self, archive_project_use_case: ArchiveProjectUseCase, user_id: str):
        """Initialize ArchiveProjectTool.

        Args:
            archive_project_use_case: ArchiveProjectUseCase instance
            user_id: Current user's Slack user ID
        """
        self._archive_project_use_case = archive_project_use_case
        self._user_id = user_id

    @property
    def name(self) -> str:
        return "archive_project"

    @property
    def description(self) -> str:
        return "プロジェクトをアーカイブする"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "プロジェクトID（UUID）",
                },
            },
            "required": ["project_id"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """プロジェクトアーカイブを実行.

        Args:
            project_id: プロジェクトID（UUID）

        Returns:
            dict: {"success": True, "data": {...}} or {"success": False, "error": "..."}
        """
        try:
            project_id_str = kwargs["project_id"]

            # Parse UUID
            try:
                project_id = UUID(project_id_str)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid UUID format: {project_id_str}",
                }

            # Execute use case
            project_dto = await self._archive_project_use_case.execute(project_id)

            return {
                "success": True,
                "data": self._project_dto_to_dict(project_dto),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _project_dto_to_dict(self, project_dto: ProjectDTO) -> dict[str, Any]:
        """Convert ProjectDTO to dict for JSON serialization.

        Args:
            project_dto: ProjectDTO

        Returns:
            dict: JSON-serializable project data
        """
        return {
            "project_id": str(project_dto.project_id),
            "name": project_dto.name,
            "description": project_dto.description,
            "owner_user_id": project_dto.owner_user_id,
            "status": project_dto.status,
            "deadline": project_dto.deadline.isoformat() if project_dto.deadline else None,
            "task_count": project_dto.task_count,
            "completed_task_count": project_dto.completed_task_count,
            "created_at": project_dto.created_at.isoformat(),
            "updated_at": project_dto.updated_at.isoformat(),
        }
