"""Prompt repository interface (Port)"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.prompt_config import PromptConfig


class PromptRepository(ABC):
    """プロンプト設定リポジトリインターフェース"""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[PromptConfig]:
        """
        名前でプロンプト設定を取得

        Args:
            name: プロンプト名 (例: "default", "technical", "schedule")

        Returns:
            PromptConfig or None
        """
        pass

    @abstractmethod
    async def get_for_user(self, user_id: str) -> PromptConfig:
        """
        ユーザーに適したプロンプト設定を取得

        Args:
            user_id: Slack ユーザーID

        Returns:
            PromptConfig (デフォルトを返す保証あり)
        """
        pass

    @abstractmethod
    async def list_all(self) -> list[PromptConfig]:
        """
        すべてのプロンプト設定を取得

        Returns:
            PromptConfigのリスト
        """
        pass
