"""Project Entity"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects.project_status import ProjectStatus


@dataclass
class Project:
    """Project Entity

    Represents a collection of tasks grouped for a specific goal.
    """

    project_id: UUID
    name: str
    owner_user_id: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    deadline: datetime | None = None
    task_ids: list[UUID] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        owner_user_id: str,
        description: str | None = None,
        deadline: datetime | None = None,
    ) -> "Project":
        """Create a new project

        Args:
            name: Project name
            owner_user_id: Slack user ID of the project owner
            description: Optional project description
            deadline: Optional project deadline

        Returns:
            New Project instance
        """
        now = datetime.now()
        return cls(
            project_id=uuid4(),
            name=name,
            owner_user_id=owner_user_id,
            status=ProjectStatus.ACTIVE,
            description=description,
            deadline=deadline,
            created_at=now,
            updated_at=now,
            task_ids=[],
        )

    def add_task(self, task_id: UUID) -> None:
        """Add a task to the project

        Args:
            task_id: UUID of the task to add

        Raises:
            ValueError: If task is already in the project
        """
        if task_id in self.task_ids:
            raise ValueError(f"Task {task_id} is already in the project")

        self.task_ids.append(task_id)
        self.updated_at = datetime.now()

    def remove_task(self, task_id: UUID) -> None:
        """Remove a task from the project

        Args:
            task_id: UUID of the task to remove

        Raises:
            ValueError: If task is not in the project
        """
        if task_id not in self.task_ids:
            raise ValueError(f"Task {task_id} is not in the project")

        self.task_ids.remove(task_id)
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Mark the project as completed"""
        self.status = ProjectStatus.COMPLETED
        self.updated_at = datetime.now()

    def archive(self) -> None:
        """Archive the project"""
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = datetime.now()

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
        deadline: datetime | None = None,
    ) -> None:
        """Update project details

        Args:
            name: New project name (if provided)
            description: New description (if provided)
            deadline: New deadline (if provided)
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if deadline is not None:
            self.deadline = deadline

        self.updated_at = datetime.now()
