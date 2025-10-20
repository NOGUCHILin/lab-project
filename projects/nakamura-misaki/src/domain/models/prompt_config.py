"""Prompt Configuration Model - Bridge pattern for migration

DEPRECATION NOTICE:
This module is a temporary bridge to support legacy code during the migration
to the new Bounded Context architecture.

This bridge will be removed in a future version after complete migration.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PromptConfig:
    """Prompt configuration - Legacy bridge model

    This class maintains backward compatibility with code expecting PromptConfig
    while we migrate to the new architecture.

    Attributes:
        name: Prompt configuration name (e.g., "default", "technical")
        system_prompt: System prompt text for Claude
        description: Human-readable description of the prompt
        version: Version string for the prompt configuration
    """

    name: str
    system_prompt: str
    description: str
    version: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptConfig":
        """Create PromptConfig from dictionary

        Args:
            data: Dictionary representation of prompt config
                  Expected keys: name, system_prompt, description, version

        Returns:
            PromptConfig instance
        """
        return cls(
            name=data["name"],
            system_prompt=data["system_prompt"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization

        Returns:
            Dictionary representation of prompt config
        """
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "description": self.description,
            "version": self.version,
        }

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"PromptConfig(name={self.name!r}, "
            f"version={self.version!r}, "
            f"description={self.description!r})"
        )
