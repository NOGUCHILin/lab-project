"""Handoff Data Transfer Objects"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateHandoffDTO:
    """ハンドオフ作成用DTO"""

    task_id: UUID
    from_user_id: str
    to_user_id: str
    progress_note: str
    handoff_at: datetime


@dataclass
class HandoffDTO:
    """ハンドオフ出力用DTO"""

    id: UUID
    task_id: UUID
    from_user_id: str
    to_user_id: str
    progress_note: str
    handoff_at: datetime
    reminded_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    @classmethod
    def from_entity(cls, handoff) -> "HandoffDTO":
        """Handoffエンティティから変換"""
        return cls(
            id=handoff.id,
            task_id=handoff.task_id,
            from_user_id=handoff.from_user_id,
            to_user_id=handoff.to_user_id,
            progress_note=handoff.progress_note,
            handoff_at=handoff.handoff_at,
            reminded_at=handoff.reminded_at,
            completed_at=handoff.completed_at,
            created_at=handoff.created_at,
        )
