"""Conversation ID Value Object"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationId:
    """Conversation identifier value object"""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> "ConversationId":
        """Generate new conversation ID"""
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "ConversationId":
        """Create ConversationId from string"""
        return cls(value=uuid.UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
