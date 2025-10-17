"""Handoff Status Value Object"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HandoffState(str, Enum):
    """Handoff state enumeration"""

    PENDING = "pending"  # 引き継ぎ待ち
    ACCEPTED = "accepted"  # 受理済み
    COMPLETED = "completed"  # 完了


@dataclass(frozen=True)
class HandoffStatus:
    """Handoff status value object"""

    state: HandoffState
    reminded_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def pending(cls) -> "HandoffStatus":
        """Create pending status"""
        return cls(state=HandoffState.PENDING)

    def accept(self) -> "HandoffStatus":
        """Accept the handoff"""
        if self.state != HandoffState.PENDING:
            raise ValueError(f"Cannot accept handoff in {self.state} state")
        return HandoffStatus(
            state=HandoffState.ACCEPTED,
            reminded_at=self.reminded_at,
            completed_at=None,
        )

    def complete(self, completed_at: datetime) -> "HandoffStatus":
        """Complete the handoff"""
        if self.state == HandoffState.COMPLETED:
            raise ValueError("Handoff is already completed")
        return HandoffStatus(
            state=HandoffState.COMPLETED,
            reminded_at=self.reminded_at,
            completed_at=completed_at,
        )

    def mark_reminded(self, reminded_at: datetime) -> "HandoffStatus":
        """Mark as reminded"""
        if self.state == HandoffState.COMPLETED:
            raise ValueError("Cannot remind completed handoff")
        return HandoffStatus(
            state=self.state,
            reminded_at=reminded_at,
            completed_at=self.completed_at,
        )

    def is_pending(self) -> bool:
        """Check if handoff is pending"""
        return self.state == HandoffState.PENDING

    def is_accepted(self) -> bool:
        """Check if handoff is accepted"""
        return self.state == HandoffState.ACCEPTED

    def is_completed(self) -> bool:
        """Check if handoff is completed"""
        return self.state == HandoffState.COMPLETED
