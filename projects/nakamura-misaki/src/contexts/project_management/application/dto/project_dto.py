"""Project DTOs (Data Transfer Objects)"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateProjectDTO:
    """DTO for creating a project"""

    name: str
    owner_user_id: str
    description: str | None = None
    deadline: datetime | None = None


@dataclass
class ProjectDTO:
    """DTO for project data"""

    project_id: UUID
    name: str
    owner_user_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    deadline: datetime | None = None
    task_count: int = 0
    completed_task_count: int = 0


@dataclass
class ProjectProgressDTO:
    """DTO for project progress"""

    project_id: UUID
    name: str
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    completion_percentage: float
    status: str
    deadline: datetime | None = None
