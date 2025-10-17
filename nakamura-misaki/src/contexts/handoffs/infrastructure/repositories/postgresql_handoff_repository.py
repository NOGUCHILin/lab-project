"""PostgreSQL Handoff Repository Implementation"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.contexts.personal_tasks.domain.value_objects.task_id import TaskId
from src.infrastructure.database.models import HandoffModel

from src.contexts.handoffs.domain.entities.handoff import Handoff
from src.contexts.handoffs.domain.repositories.handoff_repository import HandoffRepository
from src.contexts.handoffs.domain.value_objects.handoff_content import HandoffContent
from src.contexts.handoffs.domain.value_objects.handoff_id import HandoffId
from src.contexts.handoffs.domain.value_objects.handoff_status import (
    HandoffState,
    HandoffStatus,
)
from src.shared_kernel.domain.value_objects.user_id import UserId


class PostgreSQLHandoffRepository(HandoffRepository):
    """PostgreSQL implementation of HandoffRepository"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, handoff: Handoff) -> None:
        """Save handoff"""
        # Check if handoff already exists
        existing = self._session.get(HandoffModel, handoff.id.value)

        if existing:
            # Update existing handoff
            self._update_model(existing, handoff)
        else:
            # Create new handoff
            model = self._to_model(handoff)
            self._session.add(model)

        self._session.commit()

    def find_by_id(self, handoff_id: HandoffId) -> Handoff | None:
        """Find handoff by ID"""
        model = self._session.get(HandoffModel, handoff_id.value)
        return self._to_entity(model) if model else None

    def find_pending_by_recipient(self, user_id: UserId) -> list[Handoff]:
        """Find pending handoffs for a specific recipient"""
        stmt = (
            select(HandoffModel)
            .where(HandoffModel.to_user_id == user_id.value)
            .where(HandoffModel.completed_at.is_(None))
            .order_by(HandoffModel.handoff_at)
        )
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(model) for model in models]

    def find_by_recipient(
        self, user_id: UserId, include_completed: bool = False
    ) -> list[Handoff]:
        """Find all handoffs for a specific recipient"""
        stmt = select(HandoffModel).where(HandoffModel.to_user_id == user_id.value)

        if not include_completed:
            stmt = stmt.where(HandoffModel.completed_at.is_(None))

        stmt = stmt.order_by(HandoffModel.handoff_at.desc())
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(model) for model in models]

    def find_overdue_without_reminder(self, current_time: datetime) -> list[Handoff]:
        """Find overdue handoffs that haven't been reminded yet"""
        stmt = (
            select(HandoffModel)
            .where(HandoffModel.handoff_at < current_time)
            .where(HandoffModel.completed_at.is_(None))
            .where(HandoffModel.reminded_at.is_(None))
            .order_by(HandoffModel.handoff_at)
        )
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(model) for model in models]

    def delete(self, handoff_id: HandoffId) -> None:
        """Delete handoff"""
        model = self._session.get(HandoffModel, handoff_id.value)
        if model:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: HandoffModel) -> Handoff:
        """Convert model to entity"""
        # Determine handoff state based on completed_at and reminded_at
        if model.completed_at:
            state = HandoffState.COMPLETED
        elif model.reminded_at:
            state = HandoffState.ACCEPTED
        else:
            state = HandoffState.PENDING

        return Handoff(
            id=HandoffId(value=model.id),
            task_id=TaskId(value=model.task_id) if model.task_id else None,
            from_user_id=UserId(value=model.from_user_id),
            to_user_id=UserId(value=model.to_user_id),
            content=HandoffContent(
                progress_note=model.progress_note,
                next_steps=model.next_steps,
            ),
            status=HandoffStatus(
                state=state,
                reminded_at=model.reminded_at,
                completed_at=model.completed_at,
            ),
            handoff_at=model.handoff_at,
            created_at=model.created_at,
        )

    def _to_model(self, handoff: Handoff) -> HandoffModel:
        """Convert entity to model"""
        return HandoffModel(
            id=handoff.id.value,
            task_id=handoff.task_id.value if handoff.task_id else None,
            from_user_id=handoff.from_user_id.value,
            to_user_id=handoff.to_user_id.value,
            progress_note=handoff.content.progress_note,
            next_steps=handoff.content.next_steps,
            handoff_at=handoff.handoff_at,
            reminded_at=handoff.status.reminded_at,
            completed_at=handoff.status.completed_at,
            created_at=handoff.created_at,
        )

    def _update_model(self, model: HandoffModel, handoff: Handoff) -> None:
        """Update existing model with entity data"""
        model.task_id = handoff.task_id.value if handoff.task_id else None
        model.from_user_id = handoff.from_user_id.value
        model.to_user_id = handoff.to_user_id.value
        model.progress_note = handoff.content.progress_note
        model.next_steps = handoff.content.next_steps
        model.handoff_at = handoff.handoff_at
        model.reminded_at = handoff.status.reminded_at
        model.completed_at = handoff.status.completed_at
