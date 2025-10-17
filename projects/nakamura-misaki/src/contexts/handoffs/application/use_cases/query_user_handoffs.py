"""Query User Handoffs Use Case"""

from dataclasses import dataclass

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository
from src.shared_kernel.domain.value_objects.user_id import UserId


@dataclass
class QueryUserHandoffsCommand:
    """Query user handoffs command"""

    user_id: str
    include_completed: bool = False


class QueryUserHandoffsUseCase:
    """Query user handoffs use case"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    def execute(self, command: QueryUserHandoffsCommand) -> list[Handoff]:
        """Execute query user handoffs use case"""
        user_id = UserId(value=command.user_id)
        return self._handoff_repository.find_by_recipient(
            user_id, include_completed=command.include_completed
        )
