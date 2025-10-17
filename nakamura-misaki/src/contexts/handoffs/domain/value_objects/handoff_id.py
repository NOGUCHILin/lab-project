"""Handoff ID Value Object"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class HandoffId:
    """Handoff identifier value object"""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> "HandoffId":
        """Generate new handoff ID"""
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "HandoffId":
        """Create HandoffId from string"""
        return cls(value=uuid.UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
