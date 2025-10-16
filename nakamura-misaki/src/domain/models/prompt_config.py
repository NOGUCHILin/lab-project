"""Prompt configuration domain model"""

from dataclasses import dataclass, field


@dataclass
class PromptConfig:
    """システムプロンプト設定"""

    name: str
    system_prompt: str
    description: str = ""
    version: str = "1.0.0"
    metadata: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "PromptConfig":
        """辞書からPromptConfigを生成"""
        return cls(
            name=data["name"],
            system_prompt=data["system_prompt"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict:
        """PromptConfigを辞書に変換"""
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "description": self.description,
            "version": self.version,
            "metadata": self.metadata,
        }
