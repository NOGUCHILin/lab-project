"""Create Handoff Use Case"""

from dataclasses import dataclass
from datetime import datetime

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository
from src.contexts.handoffs.domain.value_objects.handoff_content import HandoffContent
from src.contexts.personal_tasks.domain.value_objects.task_id import TaskId
from src.shared_kernel.domain.value_objects.user_id import UserId


@dataclass
class CreateHandoffCommand:
    """Create handoff command"""

    from_user_id: str
    to_user_id: str
    progress_note: str
    next_steps: str
    handoff_at: datetime
    task_id: str | None = None


class CreateHandoffUseCase:
    """Create handoff use case"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    def execute(self, command: CreateHandoffCommand) -> Handoff:
        """Execute create handoff use case"""
        # Create value objects
        from_user_id = UserId(value=command.from_user_id)
        to_user_id = UserId(value=command.to_user_id)
        content = HandoffContent(
            progress_note=command.progress_note,
            next_steps=command.next_steps,
        )
        task_id = TaskId.from_string(command.task_id) if command.task_id else None

        # Create handoff entity
        handoff = Handoff.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            content=content,
            handoff_at=command.handoff_at,
            task_id=task_id,
        )

        # Save to repository
        self._handoff_repository.save(handoff)

        return handoff
