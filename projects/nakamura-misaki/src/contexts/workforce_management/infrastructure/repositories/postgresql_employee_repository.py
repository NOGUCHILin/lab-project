"""PostgreSQL implementation of EmployeeRepository"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import EmployeeTable

from ...domain.entities.employee import Employee
from ...domain.repositories.employee_repository import EmployeeRepository


class PostgreSQLEmployeeRepository(EmployeeRepository):
    """PostgreSQL implementation of EmployeeRepository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, employee_id: UUID) -> Employee | None:
        """Find employee by ID"""
        result = await self._session.execute(
            select(EmployeeTable).where(EmployeeTable.employee_id == employee_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def find_by_name(self, name: str) -> Employee | None:
        """Find employee by name"""
        result = await self._session.execute(
            select(EmployeeTable).where(EmployeeTable.name == name)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def find_all_active(self) -> list[Employee]:
        """Find all active employees"""
        result = await self._session.execute(
            select(EmployeeTable).where(EmployeeTable.is_active == True).order_by(EmployeeTable.name)  # noqa: E712
        )
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def save(self, employee: Employee) -> None:
        """Save employee"""
        existing = await self._session.get(EmployeeTable, employee.employee_id)

        if existing:
            # Update
            existing.name = employee.name
            existing.is_active = employee.is_active
            existing.updated_at = datetime.now()
        else:
            # Insert
            new_employee = EmployeeTable(
                employee_id=employee.employee_id,
                name=employee.name,
                is_active=employee.is_active,
                created_at=employee.created_at,
                updated_at=employee.updated_at,
            )
            self._session.add(new_employee)

        await self._session.flush()

    async def delete(self, employee_id: UUID) -> None:
        """Delete employee"""
        existing = await self._session.get(EmployeeTable, employee_id)
        if existing:
            await self._session.delete(existing)
            await self._session.flush()

    def _to_entity(self, row: EmployeeTable) -> Employee:
        """Convert database row to Employee entity"""
        return Employee(
            employee_id=row.employee_id,
            name=row.name,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
