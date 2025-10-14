"""Task domain model"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """タスクステータス"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """タスクエンティティ"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    description: str | None = None
    assignee_user_id: str = ""
    creator_user_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    due_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        """バリデーション"""
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title must be 200 characters or less")
        if not self.assignee_user_id:
            raise ValueError("Task assignee_user_id cannot be empty")
        if not self.creator_user_id:
            raise ValueError("Task creator_user_id cannot be empty")

        # status が文字列の場合、Enumに変換
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)

    def complete(self) -> None:
        """タスクを完了にする"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """タスクをキャンセルする"""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()

    def start(self) -> None:
        """タスクを進行中にする"""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """期限切れかどうか"""
        if not self.due_at:
            return False
        if self.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            return False
        return datetime.now() > self.due_at

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "assignee_user_id": self.assignee_user_id,
            "creator_user_id": self.creator_user_id,
            "status": self.status.value,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
