"""JSON file-based prompt repository adapter"""

import json
from pathlib import Path
from typing import Optional

from src.domain.models.prompt_config import PromptConfig
from src.domain.repositories.prompt_repository import PromptRepository


class JsonPromptRepository(PromptRepository):
    """JSONファイルベースのプロンプトリポジトリ実装"""

    def __init__(self, prompts_dir: Path):
        """
        Args:
            prompts_dir: プロンプトJSONファイルを格納するディレクトリ
        """
        self.prompts_dir = prompts_dir
        self._cache: dict[str, PromptConfig] = {}
        self._mtime: dict[str, float] = {}  # ファイル変更時刻を記録

    async def get_by_name(self, name: str) -> Optional[PromptConfig]:
        """名前でプロンプト設定を取得（ファイル変更検知付き）"""
        file_path = self.prompts_dir / f"{name}.json"
        if not file_path.exists():
            return None

        try:
            # ファイルの最終更新時刻を取得
            current_mtime = file_path.stat().st_mtime

            # キャッシュチェック：ファイルが変更されていなければキャッシュを返す
            if name in self._cache and self._mtime.get(name) == current_mtime:
                return self._cache[name]

            # ファイルから読み込み（変更があった場合または初回）
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            prompt_config = PromptConfig.from_dict(data)

            # キャッシュとmtimeを更新
            self._cache[name] = prompt_config
            self._mtime[name] = current_mtime

            print(f"✅ プロンプト再読み込み: {name} (mtime: {current_mtime})")
            return prompt_config

        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"⚠️ プロンプト読み込みエラー ({name}): {e}")
            return None

    async def get_for_user(self, user_id: str) -> PromptConfig:
        """
        ユーザーに適したプロンプト設定を取得

        現在はデフォルトプロンプトを返す
        将来的にユーザー設定やロールに基づいて切り替え可能
        """
        # 将来の拡張例:
        # user_config = await user_repository.get(user_id)
        # if user_config.role == "admin":
        #     return await self.get_by_name("technical")
        # elif user_config.preferences.get("mode") == "schedule":
        #     return await self.get_by_name("schedule")

        # デフォルトプロンプトを取得
        default_prompt = await self.get_by_name("default")

        # デフォルトが見つからない場合はフォールバック
        if default_prompt is None:
            print("⚠️ デフォルトプロンプトが見つかりません。フォールバックを使用します。")
            return self._get_fallback_prompt()

        return default_prompt

    async def list_all(self) -> list[PromptConfig]:
        """すべてのプロンプト設定を取得"""
        prompts = []

        if not self.prompts_dir.exists():
            return prompts

        for file_path in self.prompts_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prompts.append(PromptConfig.from_dict(data))
            except (json.JSONDecodeError, KeyError, OSError) as e:
                print(f"⚠️ プロンプト読み込みエラー ({file_path.name}): {e}")
                continue

        return prompts

    def _get_fallback_prompt(self) -> PromptConfig:
        """デフォルトプロンプトが見つからない場合のフォールバック"""
        return PromptConfig(
            name="fallback",
            system_prompt="""あなたは中村美咲、親切なアシスタントです。

ユーザーの質問に丁寧に答え、タスク管理をサポートします。
""",
            description="フォールバックプロンプト",
            version="1.0.0",
        )
