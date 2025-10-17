"""Employee repository interface"""

from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.employee import Employee


class EmployeeRepository(ABC):
    """Repository interface for Employee aggregate"""

    @abstractmethod
    async def find_by_id(self, employee_id: UUID) -> Employee | None:
        """Find employee by ID"""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Employee | None:
        """Find employee by name"""
        pass

    @abstractmethod
    async def find_all_active(self) -> list[Employee]:
        """Find all active employees"""
        pass

    @abstractmethod
    async def save(self, employee: Employee) -> None:
        """Save employee"""
        pass

    @abstractmethod
    async def delete(self, employee_id: UUID) -> None:
        """Delete employee"""
        pass
