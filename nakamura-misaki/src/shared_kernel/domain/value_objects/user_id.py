"""UserId value object - Shared across contexts"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """User ID value object

    Represents a Slack user ID across all contexts.
    Immutable value object shared between Personal Tasks and Work Tasks.

    Attributes:
        value: The Slack user ID string (e.g., "U12345")

    Business Rules:
        - User ID cannot be empty
        - User ID is immutable once created
        - Used for identity across all task systems
    """

    value: str

    def __post_init__(self):
        """Validate user ID after initialization"""
        if not self.value or not self.value.strip():
            raise ValueError("User ID cannot be empty")

    def __str__(self) -> str:
        """Return string representation (the value itself)"""
        return self.value

    def __repr__(self) -> str:
        """Return detailed string representation"""
        return f"UserId('{self.value}')"

    def __hash__(self) -> int:
        """Hash based on value for use in sets/dicts"""
        return hash(self.value)
