"""Employee entity for workforce management"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Employee:
    """Employee aggregate root

    Represents a staff member who can perform business tasks.
    """

    employee_id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        """Validate employee invariants"""
        if not self.name or not self.name.strip():
            raise ValueError("Employee name cannot be empty")
