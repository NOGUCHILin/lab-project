"""Handoff Content Value Object"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HandoffContent:
    """Handoff content value object (progress note and next steps)"""

    progress_note: str
    next_steps: str

    def __post_init__(self):
        """Validate handoff content"""
        if not self.progress_note or not self.progress_note.strip():
            raise ValueError("Progress note cannot be empty")
        if not self.next_steps or not self.next_steps.strip():
            raise ValueError("Next steps cannot be empty")
        if len(self.progress_note) > 5000:
            raise ValueError("Progress note is too long (max 5000 characters)")
        if len(self.next_steps) > 5000:
            raise ValueError("Next steps is too long (max 5000 characters)")
