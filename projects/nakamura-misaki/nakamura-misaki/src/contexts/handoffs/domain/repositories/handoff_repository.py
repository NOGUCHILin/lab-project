"""Handoff Repository Interface"""

from abc import ABC, abstractmethod
from datetime import datetime

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.value_objects.handoff_id import HandoffId
from src.shared_kernel.domain.value_objects.user_id import UserId


class HandoffRepository(ABC):
    """Handoff repository interface"""

    @abstractmethod
    def save(self, handoff: Handoff) -> None:
        """Save handoff"""
        pass

    @abstractmethod
    def find_by_id(self, handoff_id: HandoffId) -> Handoff | None:
        """Find handoff by ID"""
        pass

    @abstractmethod
    def find_pending_by_recipient(self, user_id: UserId) -> list[Handoff]:
        """Find pending handoffs for a specific recipient"""
        pass

    @abstractmethod
    def find_by_recipient(
        self, user_id: UserId, include_completed: bool = False
    ) -> list[Handoff]:
        """Find all handoffs for a specific recipient"""
        pass

    @abstractmethod
    def find_overdue_without_reminder(self, current_time: datetime) -> list[Handoff]:
        """Find overdue handoffs that haven't been reminded yet"""
        pass

    @abstractmethod
    def delete(self, handoff_id: HandoffId) -> None:
        """Delete handoff"""
        pass
