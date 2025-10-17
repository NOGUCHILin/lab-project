"""Repository implementations for workforce management context"""

from .postgresql_employee_repository import PostgreSQLEmployeeRepository
from .postgresql_skill_repository import PostgreSQLSkillRepository

__all__ = ["PostgreSQLEmployeeRepository", "PostgreSQLSkillRepository"]
