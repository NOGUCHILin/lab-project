"""Handoff domain model"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Handoff:
    """ハンドオフエンティティ"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    task_id: uuid.UUID | None = None
    from_user_id: str = ""
    to_user_id: str = ""
    progress_note: str = ""
    next_steps: str = ""
    handoff_at: datetime = field(default_factory=datetime.now)
    reminded_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """バリデーション"""
        if not self.from_user_id:
            raise ValueError("Handoff from_user_id cannot be empty")
        if not self.to_user_id:
            raise ValueError("Handoff to_user_id cannot be empty")
        if not self.progress_note:
            raise ValueError("Handoff progress_note cannot be empty")
        if not self.next_steps:
            raise ValueError("Handoff next_steps cannot be empty")

    def is_pending(self) -> bool:
        """未完了か？"""
        return self.completed_at is None

    def is_reminder_needed(self, current_time: datetime) -> bool:
        """リマインダー送信が必要か？

        引き継ぎ予定時刻の10分前にリマインダー送信
        """
        if self.reminded_at is not None:
            return False  # 既に送信済み

        if not self.is_pending():
            return False  # 完了済み

        # 引き継ぎ予定時刻の10分前
        reminder_time = self.handoff_at - timedelta(minutes=10)
        return current_time >= reminder_time

    def complete(self) -> None:
        """ハンドオフを完了にする"""
        self.completed_at = datetime.now()

    def mark_reminded(self) -> None:
        """リマインダー送信済みにする"""
        self.reminded_at = datetime.now()

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": str(self.id),
            "task_id": str(self.task_id) if self.task_id else None,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "progress_note": self.progress_note,
            "next_steps": self.next_steps,
            "handoff_at": self.handoff_at.isoformat(),
            "reminded_at": self.reminded_at.isoformat() if self.reminded_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
        }
