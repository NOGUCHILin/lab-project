"""Note domain model for Anthropic Structured Note-Taking"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Note:
    """ノートエンティティ

    Anthropic Structured Note-Takingで保存される構造化ノート。
    セッション間で永続化され、意味検索（vector search）が可能。
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    session_id: str = ""
    user_id: str = ""
    content: str = ""
    category: str = "general"  # code_changes, decisions, todos, errors, learnings
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """バリデーション"""
        if not self.content:
            raise ValueError("Note content cannot be empty")
        if not self.user_id:
            raise ValueError("Note user_id cannot be empty")
        if not self.session_id:
            raise ValueError("Note session_id cannot be empty")

    @classmethod
    def create(
        cls,
        session_id: str,
        user_id: str,
        content: str,
        category: str = "general",
    ) -> Note:
        """新規ノート作成"""
        return cls(
            session_id=session_id,
            user_id=user_id,
            content=content,
            category=category,
        )

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
        }
