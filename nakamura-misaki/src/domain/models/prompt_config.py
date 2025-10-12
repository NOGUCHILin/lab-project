"""Prompt configuration domain model"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass
class PromptConfig:
    """システムプロンプト設定"""

    name: str
    system_prompt: str
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "PromptConfig":
        """辞書からPromptConfigを生成"""
        return cls(
            name=data["name"],
            system_prompt=data["system_prompt"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> Dict:
        """PromptConfigを辞書に変換"""
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "description": self.description,
            "version": self.version,
            "metadata": self.metadata,
        }
