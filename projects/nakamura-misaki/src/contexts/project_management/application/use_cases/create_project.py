"""Create Project Use Case"""

from ...domain.entities.project import Project
from ...domain.repositories.project_repository import ProjectRepository
from ..dto.project_dto import CreateProjectDTO, ProjectDTO


class CreateProjectUseCase:
    """Use case for creating a project"""

    def __init__(self, project_repository: ProjectRepository):
        """Initialize use case

        Args:
            project_repository: ProjectRepository instance
        """
        self._project_repo = project_repository

    async def execute(self, dto: CreateProjectDTO) -> ProjectDTO:
        """Execute use case

        Args:
            dto: CreateProjectDTO with project details

        Returns:
            ProjectDTO with created project data

        Raises:
            ValueError: If project name is empty
        """
        if not dto.name or not dto.name.strip():
            raise ValueError("Project name cannot be empty")

        if not dto.owner_user_id or not dto.owner_user_id.strip():
            raise ValueError("Owner user ID cannot be empty")

        # Create project entity
        project = Project.create(
            name=dto.name.strip(),
            owner_user_id=dto.owner_user_id,
            description=dto.description,
            deadline=dto.deadline,
        )

        # Persist project
        saved_project = await self._project_repo.save(project)

        # Return DTO
        return ProjectDTO(
            project_id=saved_project.project_id,
            name=saved_project.name,
            owner_user_id=saved_project.owner_user_id,
            status=saved_project.status.value,
            description=saved_project.description,
            deadline=saved_project.deadline,
            created_at=saved_project.created_at,
            updated_at=saved_project.updated_at,
            task_count=0,
            completed_task_count=0,
        )
