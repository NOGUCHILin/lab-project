"""Skill repository interface"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.business_skill import BusinessSkill
from ..entities.employee import Employee
from ..entities.employee_skill import EmployeeSkill


class SkillRepository(ABC):
    """Repository interface for skill-related operations"""

    @abstractmethod
    async def find_skill_by_id(self, skill_id: UUID) -> BusinessSkill | None:
        """Find business skill by ID"""
        pass

    @abstractmethod
    async def find_skill_by_name(self, skill_name: str) -> BusinessSkill | None:
        """Find business skill by name"""
        pass

    @abstractmethod
    async def find_all_skills(self) -> list[BusinessSkill]:
        """Find all business skills"""
        pass

    @abstractmethod
    async def save_skill(self, skill: BusinessSkill) -> None:
        """Save business skill"""
        pass

    @abstractmethod
    async def find_employees_with_skill(self, skill_name: str) -> list[Employee]:
        """Find all employees who have a specific skill"""
        pass

    @abstractmethod
    async def find_employee_skills(self, employee_id: UUID) -> list[BusinessSkill]:
        """Find all skills an employee possesses"""
        pass

    @abstractmethod
    async def add_employee_skill(self, employee_skill: EmployeeSkill) -> None:
        """Add a skill to an employee"""
        pass

    @abstractmethod
    async def remove_employee_skill(self, employee_id: UUID, skill_id: UUID) -> None:
        """Remove a skill from an employee"""
        pass

    @abstractmethod
    async def suggest_assignees(
        self, required_skills: list[str], limit: int = 5
    ) -> list[tuple[Employee, int]]:
        """Suggest assignees based on required skills

        Returns list of (Employee, skill_match_count) tuples, ordered by match count descending.
        """
        pass
