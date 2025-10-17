"""Query Pending Handoffs Use Case"""

from dataclasses import dataclass

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository
from src.shared_kernel.domain.value_objects.user_id import UserId


@dataclass
class QueryPendingHandoffsCommand:
    """Query pending handoffs command"""

    user_id: str


class QueryPendingHandoffsUseCase:
    """Query pending handoffs use case"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    def execute(self, command: QueryPendingHandoffsCommand) -> list[Handoff]:
        """Execute query pending handoffs use case"""
        user_id = UserId(value=command.user_id)
        return self._handoff_repository.find_pending_by_recipient(user_id)
