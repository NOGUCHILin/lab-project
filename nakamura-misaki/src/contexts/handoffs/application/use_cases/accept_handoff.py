"""Accept Handoff Use Case"""

from dataclasses import dataclass

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository
from src.contexts.handoffs.domain.value_objects.handoff_id import HandoffId


@dataclass
class AcceptHandoffCommand:
    """Accept handoff command"""

    handoff_id: str


class AcceptHandoffUseCase:
    """Accept handoff use case"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    def execute(self, command: AcceptHandoffCommand) -> Handoff:
        """Execute accept handoff use case"""
        # Find handoff
        handoff_id = HandoffId.from_string(command.handoff_id)
        handoff = self._handoff_repository.find_by_id(handoff_id)
        if not handoff:
            raise ValueError(f"Handoff not found: {command.handoff_id}")

        # Accept handoff
        accepted_handoff = handoff.accept()

        # Save updated handoff
        self._handoff_repository.save(accepted_handoff)

        return accepted_handoff
