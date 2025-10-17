"""Business skill entity for workforce management"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ..value_objects.skill_category import SkillCategory


@dataclass(frozen=True)
class BusinessSkill:
    """Business skill entity

    Represents a specific task or capability required in business operations.
    Examples: "返信", "査定", "出品", etc.
    """

    skill_id: UUID
    skill_name: str
    category: SkillCategory
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        """Validate business skill invariants"""
        if not self.skill_name or not self.skill_name.strip():
            raise ValueError("Skill name cannot be empty")
        if self.display_order < 0:
            raise ValueError("Display order must be non-negative")
