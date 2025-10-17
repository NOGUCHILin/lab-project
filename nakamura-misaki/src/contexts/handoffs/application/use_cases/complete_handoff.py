"""Complete Handoff Use Case"""

from dataclasses import dataclass
from datetime import datetime

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository
from src.contexts.handoffs.domain.value_objects.handoff_id import HandoffId


@dataclass
class CompleteHandoffCommand:
    """Complete handoff command"""

    handoff_id: str
    completed_at: datetime | None = None


class CompleteHandoffUseCase:
    """Complete handoff use case"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    def execute(self, command: CompleteHandoffCommand) -> Handoff:
        """Execute complete handoff use case"""
        # Find handoff
        handoff_id = HandoffId.from_string(command.handoff_id)
        handoff = self._handoff_repository.find_by_id(handoff_id)
        if not handoff:
            raise ValueError(f"Handoff not found: {command.handoff_id}")

        # Complete handoff
        completed_handoff = handoff.complete(command.completed_at)

        # Save updated handoff
        self._handoff_repository.save(completed_handoff)

        return completed_handoff
