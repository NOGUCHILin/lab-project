"""Employee skill entity for workforce management"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class EmployeeSkill:
    """Employee skill association entity

    Represents the fact that a specific employee possesses a specific business skill.
    """

    id: UUID
    employee_id: UUID
    skill_id: UUID
    acquired_at: datetime
    created_at: datetime
    updated_at: datetime
