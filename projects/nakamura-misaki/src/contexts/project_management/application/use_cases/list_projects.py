"""List Projects Use Case"""

from ...domain.repositories.project_repository import ProjectRepository
from ...domain.value_objects.project_status import ProjectStatus
from ..dto.project_dto import ProjectDTO


class ListProjectsUseCase:
    """Use case for listing projects"""

    def __init__(self, project_repository: ProjectRepository):
        """Initialize use case

        Args:
            project_repository: ProjectRepository instance
        """
        self._project_repo = project_repository

    async def execute(
        self,
        owner_user_id: str,
        status: ProjectStatus | None = None,
    ) -> list[ProjectDTO]:
        """Execute use case

        Args:
            owner_user_id: Slack user ID of the owner
            status: Optional status filter

        Returns:
            List of ProjectDTO
        """
        # Get projects
        projects = await self._project_repo.find_by_owner(
            owner_user_id=owner_user_id,
            status=status,
        )

        # Convert to DTOs
        result = []
        for project in projects:
            task_count = len(project.task_ids)
            result.append(
                ProjectDTO(
                    project_id=project.project_id,
                    name=project.name,
                    owner_user_id=project.owner_user_id,
                    status=project.status.value,
                    description=project.description,
                    deadline=project.deadline,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                    task_count=task_count,
                    completed_task_count=0,  # Will be calculated if needed
                )
            )

        return result
