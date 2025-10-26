"""Project Repository Interface"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.project import Project
from ..value_objects.project_status import ProjectStatus


class ProjectRepository(ABC):
    """Project Repository Interface (Port)

    Defines the contract for project persistence operations.
    """

    @abstractmethod
    async def save(self, project: Project) -> Project:
        """Save a project

        Args:
            project: Project entity to save

        Returns:
            Saved project entity
        """
        pass

    @abstractmethod
    async def find_by_id(self, project_id: UUID) -> Project | None:
        """Find a project by ID

        Args:
            project_id: UUID of the project

        Returns:
            Project entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_owner(
        self,
        owner_user_id: str,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        """Find projects by owner

        Args:
            owner_user_id: Slack user ID of the owner
            status: Optional status filter

        Returns:
            List of projects
        """
        pass

    @abstractmethod
    async def delete(self, project_id: UUID) -> None:
        """Delete a project

        Args:
            project_id: UUID of the project to delete
        """
        pass

    @abstractmethod
    async def get_task_ids(self, project_id: UUID) -> list[UUID]:
        """Get all task IDs associated with a project

        Args:
            project_id: UUID of the project

        Returns:
            List of task UUIDs
        """
        pass

    @abstractmethod
    async def add_task_to_project(
        self,
        project_id: UUID,
        task_id: UUID,
        position: int,
    ) -> None:
        """Add a task to a project

        Args:
            project_id: UUID of the project
            task_id: UUID of the task
            position: Position of the task in the project
        """
        pass

    @abstractmethod
    async def remove_task_from_project(
        self,
        project_id: UUID,
        task_id: UUID,
    ) -> None:
        """Remove a task from a project

        Args:
            project_id: UUID of the project
            task_id: UUID of the task
        """
        pass
