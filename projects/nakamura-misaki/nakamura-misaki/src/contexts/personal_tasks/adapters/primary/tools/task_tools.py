"""Task Tools - MCP Tools adapter for task operations"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ......shared_kernel.domain.value_objects.task_status import TaskStatus
from ....application.dto.task_dto import CreateTaskDTO, UpdateTaskDTO
from ....application.use_cases.complete_task import CompleteTaskUseCase
from ....application.use_cases.query_due_tasks import QueryDueTasksUseCase
from ....application.use_cases.query_user_tasks import QueryUserTasksUseCase
from ....application.use_cases.register_task import RegisterTaskUseCase
from ....application.use_cases.update_task import UpdateTaskUseCase


@dataclass
class RegisterTaskParams:
    """Parameters for registering a task"""
    title: str
    assignee_user_id: str
    creator_user_id: str
    description: str | None = None
    due_at: datetime | None = None


@dataclass
class CompleteTaskParams:
    """Parameters for completing a task"""
    task_id: str


@dataclass
class UpdateTaskParams:
    """Parameters for updating a task"""
    task_id: str
    title: str | None = None
    description: str | None = None
    status: str | None = None
    due_at: datetime | None = None


@dataclass
class QueryUserTasksParams:
    """Parameters for querying user tasks"""
    user_id: str
    status: str | None = None


class TaskTools:
    """MCP Tools adapter for task operations

    This adapter converts MCP tool calls to use case executions,
    providing a clean interface between the MCP layer and application logic.
    """

    def __init__(
        self,
        register_task_use_case: RegisterTaskUseCase,
        complete_task_use_case: CompleteTaskUseCase,
        update_task_use_case: UpdateTaskUseCase,
        query_user_tasks_use_case: QueryUserTasksUseCase,
        query_due_tasks_use_case: QueryDueTasksUseCase,
    ):
        """Initialize TaskTools with use cases

        Args:
            register_task_use_case: Use case for registering tasks
            complete_task_use_case: Use case for completing tasks
            update_task_use_case: Use case for updating tasks
            query_user_tasks_use_case: Use case for querying user tasks
            query_due_tasks_use_case: Use case for querying due/overdue tasks
        """
        self.register_task_use_case = register_task_use_case
        self.complete_task_use_case = complete_task_use_case
        self.update_task_use_case = update_task_use_case
        self.query_user_tasks_use_case = query_user_tasks_use_case
        self.query_due_tasks_use_case = query_due_tasks_use_case

    async def register_task(self, params: RegisterTaskParams) -> dict:
        """Register a new task

        Args:
            params: Task registration parameters

        Returns:
            Dict with success status and task data
        """
        try:
            dto = CreateTaskDTO(
                title=params.title,
                assignee_user_id=params.assignee_user_id,
                creator_user_id=params.creator_user_id,
                description=params.description,
                due_at=params.due_at,
            )

            result = await self.register_task_use_case.execute(dto)

            return {
                "success": True,
                "task_id": str(result.id),
                "title": result.title,
                "status": result.status,
                "assignee_user_id": result.assignee_user_id,
                "creator_user_id": result.creator_user_id,
                "created_at": result.created_at.isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def complete_task(self, params: CompleteTaskParams) -> dict:
        """Complete a task

        Args:
            params: Task completion parameters

        Returns:
            Dict with success status and task data
        """
        try:
            task_id = UUID(params.task_id)
            result = await self.complete_task_use_case.execute(task_id)

            return {
                "success": True,
                "task_id": str(result.id),
                "title": result.title,
                "status": result.status,
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_task(self, params: UpdateTaskParams) -> dict:
        """Update a task

        Args:
            params: Task update parameters

        Returns:
            Dict with success status and task data
        """
        try:
            task_id = UUID(params.task_id)

            # Convert status string to enum if provided
            status_enum = None
            if params.status:
                status_enum = TaskStatus(params.status)

            dto = UpdateTaskDTO(
                title=params.title,
                description=params.description,
                status=status_enum,
                due_at=params.due_at,
            )

            result = await self.update_task_use_case.execute(task_id, dto)

            return {
                "success": True,
                "task_id": str(result.id),
                "title": result.title,
                "description": result.description,
                "status": result.status,
                "updated_at": result.updated_at.isoformat(),
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def query_user_tasks(self, params: QueryUserTasksParams) -> dict:
        """Query user's tasks

        Args:
            params: Query parameters

        Returns:
            Dict with tasks list
        """
        try:
            # Convert status string to enum if provided
            status_enum = None
            if params.status:
                status_enum = TaskStatus(params.status)

            results = await self.query_user_tasks_use_case.execute(
                user_id=params.user_id,
                status=status_enum
            )

            return {
                "tasks": [
                    {
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "assignee_user_id": task.assignee_user_id,
                        "creator_user_id": task.creator_user_id,
                        "due_at": task.due_at.isoformat() if task.due_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "created_at": task.created_at.isoformat(),
                    }
                    for task in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    async def query_due_today(self, user_id: str) -> dict:
        """Query tasks due today

        Args:
            user_id: User ID to query tasks for

        Returns:
            Dict with tasks list
        """
        try:
            results = await self.query_due_tasks_use_case.execute_due_today(user_id)

            return {
                "tasks": [
                    {
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "due_at": task.due_at.isoformat() if task.due_at else None,
                        "created_at": task.created_at.isoformat(),
                    }
                    for task in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    async def query_overdue(self, user_id: str) -> dict:
        """Query overdue tasks

        Args:
            user_id: User ID to query tasks for

        Returns:
            Dict with tasks list
        """
        try:
            results = await self.query_due_tasks_use_case.execute_overdue(user_id)

            return {
                "tasks": [
                    {
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "due_at": task.due_at.isoformat() if task.due_at else None,
                        "created_at": task.created_at.isoformat(),
                    }
                    for task in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}
