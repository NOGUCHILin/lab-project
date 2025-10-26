"""Get Project Progress Use Case"""

from uuid import UUID

from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository
from src.shared_kernel.domain.value_objects.task_status import TaskStatus

from ...domain.repositories.project_repository import ProjectRepository
from ..dto.project_dto import ProjectProgressDTO


class GetProjectProgressUseCase:
    """Use case for getting project progress

    This use case orchestrates between Project Management and Personal Tasks contexts.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
    ):
        """Initialize use case

        Args:
            project_repository: ProjectRepository instance
            task_repository: TaskRepository instance (from Personal Tasks context)
        """
        self._project_repo = project_repository
        self._task_repo = task_repository

    async def execute(self, project_id: UUID) -> ProjectProgressDTO:
        """Execute use case

        Args:
            project_id: UUID of the project

        Returns:
            ProjectProgressDTO with progress data

        Raises:
            ValueError: If project not found
        """
        # 1. Get project
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # 2. Get associated task IDs
        task_ids = await self._project_repo.get_task_ids(project_id)

        # 3. Count tasks by status
        total_tasks = len(task_ids)
        completed_tasks = 0
        in_progress_tasks = 0
        pending_tasks = 0

        for task_id in task_ids:
            task = await self._task_repo.get_by_id(task_id)
            if task:
                if task.status == TaskStatus.COMPLETED:
                    completed_tasks += 1
                elif task.status == TaskStatus.IN_PROGRESS:
                    in_progress_tasks += 1
                elif task.status == TaskStatus.PENDING:
                    pending_tasks += 1

        # 4. Calculate completion percentage
        completion_percentage = 0.0
        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100

        # 5. Return progress DTO
        return ProjectProgressDTO(
            project_id=project.project_id,
            name=project.name,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            pending_tasks=pending_tasks,
            completion_percentage=round(completion_percentage, 2),
            status=project.status.value,
            deadline=project.deadline,
        )
