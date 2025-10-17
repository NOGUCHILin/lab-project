"""Send Overdue Reminders Use Case"""

from datetime import datetime

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository


class SendOverdueRemindersUseCase:
    """Send overdue reminders use case"""

    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    def execute(self, current_time: datetime | None = None) -> list[Handoff]:
        """
        Execute send overdue reminders use case

        Returns list of handoffs that were marked as reminded
        """
        check_time = current_time or datetime.now()

        # Find overdue handoffs without reminders
        overdue_handoffs = self._handoff_repository.find_overdue_without_reminder(
            check_time
        )

        # Mark as reminded
        reminded_handoffs = []
        for handoff in overdue_handoffs:
            reminded = handoff.mark_reminded(check_time)
            self._handoff_repository.save(reminded)
            reminded_handoffs.append(reminded)

        return reminded_handoffs
