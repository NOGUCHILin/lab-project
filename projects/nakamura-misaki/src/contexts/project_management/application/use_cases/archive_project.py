"""Archive Project Use Case"""

from uuid import UUID

from ...domain.repositories.project_repository import ProjectRepository


class ArchiveProjectUseCase:
    """Use case for archiving a project"""

    def __init__(self, project_repository: ProjectRepository):
        """Initialize use case

        Args:
            project_repository: ProjectRepository instance
        """
        self._project_repo = project_repository

    async def execute(self, project_id: UUID) -> None:
        """Execute use case

        Args:
            project_id: UUID of the project to archive

        Raises:
            ValueError: If project not found
        """
        # Get project
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Archive project (domain logic)
        project.archive()

        # Persist changes
        await self._project_repo.save(project)
