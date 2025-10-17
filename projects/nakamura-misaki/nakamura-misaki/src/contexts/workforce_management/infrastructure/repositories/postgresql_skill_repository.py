"""PostgreSQL implementation of SkillRepository"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import (
    BusinessSkillTable,
    EmployeeSkillTable,
    EmployeeTable,
)

from ...domain.entities.business_skill import BusinessSkill
from ...domain.entities.employee import Employee
from ...domain.entities.employee_skill import EmployeeSkill
from ...domain.repositories.skill_repository import SkillRepository


class PostgreSQLSkillRepository(SkillRepository):
    """PostgreSQL implementation of SkillRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_skill_by_id(self, skill_id: UUID) -> BusinessSkill | None:
        """Find business skill by ID"""
        result = await self._session.execute(
            select(BusinessSkillTable).where(BusinessSkillTable.skill_id == skill_id)
        )
        row = result.scalar_one_or_none()
        return self._skill_to_entity(row) if row else None

    async def find_skill_by_name(self, skill_name: str) -> BusinessSkill | None:
        """Find business skill by name"""
        result = await self._session.execute(
            select(BusinessSkillTable).where(BusinessSkillTable.skill_name == skill_name)
        )
        row = result.scalar_one_or_none()
        return self._skill_to_entity(row) if row else None

    async def find_all_skills(self) -> list[BusinessSkill]:
        """Find all business skills"""
        result = await self._session.execute(
            select(BusinessSkillTable)
            .where(BusinessSkillTable.is_active == True)  # noqa: E712
            .order_by(BusinessSkillTable.display_order)
        )
        rows = result.scalars().all()
        return [self._skill_to_entity(row) for row in rows]

    async def save_skill(self, skill: BusinessSkill) -> None:
        """Save business skill"""
        existing = await self._session.get(BusinessSkillTable, skill.skill_id)

        if existing:
            # Update
            existing.skill_name = skill.skill_name
            existing.category = skill.category
            existing.display_order = skill.display_order
            existing.is_active = skill.is_active
            existing.updated_at = datetime.now()
        else:
            # Insert
            new_skill = BusinessSkillTable(
                skill_id=skill.skill_id,
                skill_name=skill.skill_name,
                category=skill.category,
                display_order=skill.display_order,
                is_active=skill.is_active,
                created_at=skill.created_at,
                updated_at=skill.updated_at,
            )
            self._session.add(new_skill)

        await self._session.flush()

    async def find_employees_with_skill(self, skill_name: str) -> list[Employee]:
        """Find all employees who have a specific skill"""
        result = await self._session.execute(
            select(EmployeeTable)
            .join(EmployeeSkillTable, EmployeeTable.employee_id == EmployeeSkillTable.employee_id)
            .join(BusinessSkillTable, EmployeeSkillTable.skill_id == BusinessSkillTable.skill_id)
            .where(BusinessSkillTable.skill_name == skill_name)
            .where(EmployeeTable.is_active == True)  # noqa: E712
            .order_by(EmployeeTable.name)
        )
        rows = result.scalars().all()
        return [self._employee_to_entity(row) for row in rows]

    async def find_employee_skills(self, employee_id: UUID) -> list[BusinessSkill]:
        """Find all skills an employee possesses"""
        result = await self._session.execute(
            select(BusinessSkillTable)
            .join(EmployeeSkillTable, BusinessSkillTable.skill_id == EmployeeSkillTable.skill_id)
            .where(EmployeeSkillTable.employee_id == employee_id)
            .where(BusinessSkillTable.is_active == True)  # noqa: E712
            .order_by(BusinessSkillTable.display_order)
        )
        rows = result.scalars().all()
        return [self._skill_to_entity(row) for row in rows]

    async def add_employee_skill(self, employee_skill: EmployeeSkill) -> None:
        """Add a skill to an employee"""
        new_skill = EmployeeSkillTable(
            id=employee_skill.id,
            employee_id=employee_skill.employee_id,
            skill_id=employee_skill.skill_id,
            acquired_at=employee_skill.acquired_at,
            created_at=employee_skill.created_at,
            updated_at=employee_skill.updated_at,
        )
        self._session.add(new_skill)
        await self._session.flush()

    async def remove_employee_skill(self, employee_id: UUID, skill_id: UUID) -> None:
        """Remove a skill from an employee"""
        result = await self._session.execute(
            select(EmployeeSkillTable)
            .where(EmployeeSkillTable.employee_id == employee_id)
            .where(EmployeeSkillTable.skill_id == skill_id)
        )
        row = result.scalar_one_or_none()
        if row:
            await self._session.delete(row)
            await self._session.flush()

    async def suggest_assignees(
        self, required_skills: list[str], limit: int = 5
    ) -> list[tuple[Employee, int]]:
        """Suggest assignees based on required skills

        Returns list of (Employee, skill_match_count) tuples, ordered by match count descending.
        """
        # Subquery to count matching skills per employee
        skill_count_subquery = (
            select(
                EmployeeSkillTable.employee_id,
                func.count(EmployeeSkillTable.skill_id).label("match_count"),
            )
            .join(BusinessSkillTable, EmployeeSkillTable.skill_id == BusinessSkillTable.skill_id)
            .where(BusinessSkillTable.skill_name.in_(required_skills))
            .group_by(EmployeeSkillTable.employee_id)
            .subquery()
        )

        # Main query to get employees with their match counts
        result = await self._session.execute(
            select(EmployeeTable, skill_count_subquery.c.match_count)
            .join(skill_count_subquery, EmployeeTable.employee_id == skill_count_subquery.c.employee_id)
            .where(EmployeeTable.is_active == True)  # noqa: E712
            .order_by(skill_count_subquery.c.match_count.desc(), EmployeeTable.name)
            .limit(limit)
        )

        rows = result.all()
        return [(self._employee_to_entity(row[0]), row[1]) for row in rows]

    def _skill_to_entity(self, row: BusinessSkillTable) -> BusinessSkill:
        """Convert database row to BusinessSkill entity"""
        return BusinessSkill(
            skill_id=row.skill_id,
            skill_name=row.skill_name,
            category=row.category,
            display_order=row.display_order,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _employee_to_entity(self, row: EmployeeTable) -> Employee:
        """Convert database row to Employee entity"""
        return Employee(
            employee_id=row.employee_id,
            name=row.name,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
