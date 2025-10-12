"""Query handlers (CQRS read operations)"""

from .health_query import HealthQuery, HealthQueryHandler

__all__ = ["HealthQuery", "HealthQueryHandler"]
