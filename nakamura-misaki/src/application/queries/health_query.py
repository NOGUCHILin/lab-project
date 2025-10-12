"""Health check query"""

from dataclasses import dataclass


@dataclass
class HealthQuery:
    """Health check query"""

    pass


@dataclass
class HealthQueryResult:
    """Health query result"""

    status: str
    version: str = "2.0.0-fastapi"


class HealthQueryHandler:
    """Health query handler"""

    async def handle(self, query: HealthQuery) -> HealthQueryResult:
        """Handle health query"""
        return HealthQueryResult(status="healthy")
