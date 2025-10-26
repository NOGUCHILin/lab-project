"""Archive Project Use Case"""

from uuid import UUID

from ...domain.repositories.project_repository import ProjectRepository
from ..dto.project_dto import ProjectDTO


class ArchiveProjectUseCase:
    """Use case for archiving a project"""

    def __init__(self, project_repository: ProjectRepository):
        """Initialize use case

        Args:
            project_repository: ProjectRepository instance
        """
        self._project_repo = project_repository

    async def execute(self, project_id: UUID) -> ProjectDTO:
        """Execute use case

        Args:
            project_id: UUID of the project to archive

        Returns:
            ProjectDTO: Archived project data

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
        saved_project = await self._project_repo.save(project)

        # Convert to DTO
        return ProjectDTO(
            project_id=saved_project.project_id,
            name=saved_project.name,
            owner_user_id=saved_project.owner_user_id,
            status=saved_project.status.value,
            created_at=saved_project.created_at,
            updated_at=saved_project.updated_at,
            description=saved_project.description,
            deadline=saved_project.deadline,
            task_count=len(saved_project.task_ids),
            completed_task_count=0,  # Will be calculated by GetProjectProgressUseCase if needed
        )
