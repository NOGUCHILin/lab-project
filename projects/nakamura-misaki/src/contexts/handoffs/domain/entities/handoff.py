"""Handoff Entity"""

from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from src.contexts.handoffs.domain.value_objects.handoff_content import HandoffContent
from src.contexts.handoffs.domain.value_objects.handoff_id import HandoffId
from src.contexts.handoffs.domain.value_objects.handoff_status import HandoffStatus
from src.shared_kernel.domain.value_objects.user_id import UserId


@dataclass
class Handoff:
    """
    Handoff Entity - Represents a task handoff between users

    Business Rules:
    - A handoff must have from_user and to_user
    - A handoff can optionally reference a task
    - Progress note and next steps are required
    - Handoff can be in pending, accepted, or completed state
    - Only pending handoffs can be accepted
    - Only non-completed handoffs can be reminded
    """

    id: HandoffId
    task_id: UUID | None
    from_user_id: UserId
    to_user_id: UserId
    content: HandoffContent
    status: HandoffStatus
    handoff_at: datetime
    created_at: datetime

    @classmethod
    def create(
        cls,
        from_user_id: UserId,
        to_user_id: UserId,
        content: HandoffContent,
        handoff_at: datetime,
        task_id: UUID | None = None,
    ) -> "Handoff":
        """Create a new handoff"""
        if from_user_id == to_user_id:
            raise ValueError("Cannot handoff to the same user")

        now = datetime.now()
        return cls(
            id=HandoffId.generate(),
            task_id=task_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            content=content,
            status=HandoffStatus.pending(),
            handoff_at=handoff_at,
            created_at=now,
        )

    def accept(self) -> "Handoff":
        """Accept this handoff"""
        return replace(self, status=self.status.accept())

    def complete(self, completed_at: datetime | None = None) -> "Handoff":
        """Complete this handoff"""
        completion_time = completed_at or datetime.now()
        return replace(self, status=self.status.complete(completion_time))

    def mark_reminded(self, reminded_at: datetime | None = None) -> "Handoff":
        """Mark as reminded"""
        reminder_time = reminded_at or datetime.now()
        return replace(self, status=self.status.mark_reminded(reminder_time))

    def is_overdue(self, current_time: datetime | None = None) -> bool:
        """Check if handoff is overdue"""
        check_time = current_time or datetime.now()
        return not self.status.is_completed() and self.handoff_at < check_time

    def should_send_reminder(self, current_time: datetime | None = None) -> bool:
        """Check if reminder should be sent"""
        check_time = current_time or datetime.now()
        return (
            self.is_overdue(check_time)
            and not self.status.is_completed()
            and self.status.reminded_at is None
        )
