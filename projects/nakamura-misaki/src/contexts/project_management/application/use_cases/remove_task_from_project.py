"""Remove Task from Project Use Case"""

from uuid import UUID

from ...domain.repositories.project_repository import ProjectRepository


class RemoveTaskFromProjectUseCase:
    """Use case for removing a task from a project"""

    def __init__(self, project_repository: ProjectRepository):
        """Initialize use case

        Args:
            project_repository: ProjectRepository instance
        """
        self._project_repo = project_repository

    async def execute(self, project_id: UUID, task_id: UUID) -> None:
        """Execute use case

        Args:
            project_id: UUID of the project
            task_id: UUID of the task to remove

        Raises:
            ValueError: If project not found or task not in project
        """
        # 1. Verify project exists
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # 2. Remove task from project (using domain logic)
        try:
            project.remove_task(task_id)
        except ValueError as e:
            raise ValueError(str(e))

        # 3. Persist removal
        await self._project_repo.remove_task_from_project(
            project_id=project_id,
            task_id=task_id,
        )

        # 4. Update project entity
        await self._project_repo.save(project)
