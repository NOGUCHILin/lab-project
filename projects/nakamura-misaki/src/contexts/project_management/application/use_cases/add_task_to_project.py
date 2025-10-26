"""Add Task to Project Use Case"""

from uuid import UUID

from src.contexts.personal_tasks.domain.repositories.task_repository import TaskRepository

from ...domain.repositories.project_repository import ProjectRepository


class AddTaskToProjectUseCase:
    """Use case for adding a task to a project

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

    async def execute(self, project_id: UUID, task_id: UUID) -> None:
        """Execute use case

        Args:
            project_id: UUID of the project
            task_id: UUID of the task to add

        Raises:
            ValueError: If project or task not found, or task already in project
        """
        # 1. Verify task exists (Personal Tasks Context)
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # 2. Verify project exists and get current task IDs
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # 3. Add task to project (using domain logic)
        try:
            project.add_task(task_id)
        except ValueError as e:
            raise ValueError(str(e))

        # 4. Calculate position (append to end)
        current_task_ids = await self._project_repo.get_task_ids(project_id)
        position = len(current_task_ids)

        # 5. Persist relationship
        await self._project_repo.add_task_to_project(
            project_id=project_id,
            task_id=task_id,
            position=position,
        )

        # 6. Update project entity
        await self._project_repo.save(project)
