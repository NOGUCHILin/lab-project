"""Base tool interface for Claude Tool Use.

All tools must implement this interface to be compatible with
Claude Messages API Tool Use feature.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """抽象基底クラス for Claude Tool Use.

    各Tool実装はこのクラスを継承し、name, description, input_schema, execute()を実装する。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool名（Claude APIに渡す識別子）.

        例: "register_task", "list_tasks"
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Toolの説明（Claudeがいつ使うべきか判断するための説明）.

        例: "ユーザーの新しいタスクを登録する"
        """
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """Tool入力のJSONスキーマ.

        Claude Messages API Tool Use形式に準拠。

        例:
        {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "タスクタイトル"}
            },
            "required": ["title"]
        }
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Toolを実行.

        Args:
            **kwargs: input_schemaに準拠したパラメータ

        Returns:
            dict: 実行結果（JSON serializable）
                成功時: {"success": True, "data": {...}}
                失敗時: {"success": False, "error": "..."}
        """
        pass

    def to_tool_definition(self) -> dict[str, Any]:
        """Claude API用のTool定義を生成.

        Returns:
            dict: Claude Messages API Tool Use形式のTool定義
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
