"""Project Status Value Object"""

from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration"""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

    def __str__(self) -> str:
        return self.value
