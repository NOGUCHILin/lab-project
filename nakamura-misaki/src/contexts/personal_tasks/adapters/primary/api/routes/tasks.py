"""Task API routes - FastAPI endpoints for task operations"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .....application.use_cases.register_task import RegisterTaskUseCase
from .....application.use_cases.complete_task import CompleteTaskUseCase
from .....application.use_cases.update_task import UpdateTaskUseCase
from .....application.use_cases.query_user_tasks import QueryUserTasksUseCase
from .....application.use_cases.query_due_tasks import QueryDueTasksUseCase
from .....application.dto.task_dto import CreateTaskDTO, UpdateTaskDTO
from .......shared_kernel.domain.value_objects.task_status import TaskStatus


# Request/Response Models
class RegisterTaskRequest(BaseModel):
    """Request model for registering a task"""
    title: str = Field(..., min_length=1, max_length=500)
    assignee_user_id: str = Field(..., min_length=1)
    creator_user_id: str = Field(..., min_length=1)
    description: str | None = None
    due_at: datetime | None = None


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task"""
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = None
    due_at: datetime | None = None


class TaskResponse(BaseModel):
    """Response model for a task"""
    id: UUID
    title: str
    description: str | None
    assignee_user_id: str
    creator_user_id: str
    status: str
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


def create_task_router(
    register_task_use_case: RegisterTaskUseCase,
    complete_task_use_case: CompleteTaskUseCase,
    update_task_use_case: UpdateTaskUseCase,
    query_user_tasks_use_case: QueryUserTasksUseCase,
    query_due_tasks_use_case: QueryDueTasksUseCase,
) -> APIRouter:
    """Create task router with use case dependencies

    Args:
        register_task_use_case: Use case for registering tasks
        complete_task_use_case: Use case for completing tasks
        update_task_use_case: Use case for updating tasks
        query_user_tasks_use_case: Use case for querying user tasks
        query_due_tasks_use_case: Use case for querying due/overdue tasks

    Returns:
        Configured APIRouter instance
    """
    router = APIRouter(prefix="/tasks", tags=["tasks"])

    @router.post("", status_code=201, response_model=TaskResponse)
    async def register_task(request: RegisterTaskRequest) -> TaskResponse:
        """Register a new task

        Args:
            request: Task registration data

        Returns:
            Created task data

        Raises:
            HTTPException: If task creation fails
        """
        try:
            dto = CreateTaskDTO(
                title=request.title,
                assignee_user_id=request.assignee_user_id,
                creator_user_id=request.creator_user_id,
                description=request.description,
                due_at=request.due_at,
            )

            result = await register_task_use_case.execute(dto)

            return TaskResponse(
                id=result.id,
                title=result.title,
                description=result.description,
                assignee_user_id=result.assignee_user_id,
                creator_user_id=result.creator_user_id,
                status=result.status,
                due_at=result.due_at,
                completed_at=result.completed_at,
                created_at=result.created_at,
                updated_at=result.updated_at,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.patch("/{task_id}/complete", response_model=TaskResponse)
    async def complete_task(task_id: UUID) -> TaskResponse:
        """Complete a task

        Args:
            task_id: ID of task to complete

        Returns:
            Updated task data

        Raises:
            HTTPException: If task not found or already completed
        """
        try:
            result = await complete_task_use_case.execute(task_id)

            return TaskResponse(
                id=result.id,
                title=result.title,
                description=result.description,
                assignee_user_id=result.assignee_user_id,
                creator_user_id=result.creator_user_id,
                status=result.status,
                due_at=result.due_at,
                completed_at=result.completed_at,
                created_at=result.created_at,
                updated_at=result.updated_at,
            )
        except ValueError as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                raise HTTPException(status_code=404, detail=str(e))
            raise HTTPException(status_code=400, detail=str(e))

    @router.patch("/{task_id}", response_model=TaskResponse)
    async def update_task(task_id: UUID, request: UpdateTaskRequest) -> TaskResponse:
        """Update a task

        Args:
            task_id: ID of task to update
            request: Update data

        Returns:
            Updated task data

        Raises:
            HTTPException: If task not found or update fails
        """
        try:
            # Convert status string to enum if provided
            status_enum = None
            if request.status:
                status_enum = TaskStatus(request.status)

            dto = UpdateTaskDTO(
                title=request.title,
                description=request.description,
                status=status_enum,
                due_at=request.due_at,
            )

            result = await update_task_use_case.execute(task_id, dto)

            return TaskResponse(
                id=result.id,
                title=result.title,
                description=result.description,
                assignee_user_id=result.assignee_user_id,
                creator_user_id=result.creator_user_id,
                status=result.status,
                due_at=result.due_at,
                completed_at=result.completed_at,
                created_at=result.created_at,
                updated_at=result.updated_at,
            )
        except ValueError as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                raise HTTPException(status_code=404, detail=str(e))
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("", response_model=list[TaskResponse])
    async def query_user_tasks(
        user_id: str = Query(..., description="User ID to query tasks for"),
        status: str | None = Query(None, description="Optional status filter (pending/completed)")
    ) -> list[TaskResponse]:
        """Query user's tasks

        Args:
            user_id: User ID to query tasks for
            status: Optional status filter

        Returns:
            List of tasks

        Raises:
            HTTPException: If query fails
        """
        try:
            # Convert status string to enum if provided
            status_enum = None
            if status:
                status_enum = TaskStatus(status)

            results = await query_user_tasks_use_case.execute(user_id, status_enum)

            return [
                TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    assignee_user_id=task.assignee_user_id,
                    creator_user_id=task.creator_user_id,
                    status=task.status,
                    due_at=task.due_at,
                    completed_at=task.completed_at,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in results
            ]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/due-today", response_model=list[TaskResponse])
    async def query_due_today(
        user_id: str = Query(..., description="User ID to query tasks for")
    ) -> list[TaskResponse]:
        """Query tasks due today

        Args:
            user_id: User ID to query tasks for

        Returns:
            List of tasks due today

        Raises:
            HTTPException: If query fails
        """
        try:
            results = await query_due_tasks_use_case.execute_due_today(user_id)

            return [
                TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    assignee_user_id=task.assignee_user_id,
                    creator_user_id=task.creator_user_id,
                    status=task.status,
                    due_at=task.due_at,
                    completed_at=task.completed_at,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in results
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/overdue", response_model=list[TaskResponse])
    async def query_overdue(
        user_id: str = Query(..., description="User ID to query tasks for")
    ) -> list[TaskResponse]:
        """Query overdue tasks

        Args:
            user_id: User ID to query tasks for

        Returns:
            List of overdue tasks

        Raises:
            HTTPException: If query fails
        """
        try:
            results = await query_due_tasks_use_case.execute_overdue(user_id)

            return [
                TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    assignee_user_id=task.assignee_user_id,
                    creator_user_id=task.creator_user_id,
                    status=task.status,
                    due_at=task.due_at,
                    completed_at=task.completed_at,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in results
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
