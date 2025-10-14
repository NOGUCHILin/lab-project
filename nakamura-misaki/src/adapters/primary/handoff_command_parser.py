"""HandoffCommandParser - ハンドオフ関連コマンドの自然言語解析"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID


@dataclass
class ParsedHandoffCommand:
    """解析済みハンドオフコマンド"""

    command_type: str  # "register", "list", "complete"
    user_id: str
    task_id: UUID | None = None
    to_user_id: str | None = None
    progress_note: str | None = None
    handoff_at: datetime | None = None
    handoff_id: UUID | None = None


class HandoffCommandParser:
    """ハンドオフコマンドパーサー"""

    def parse(self, text: str, user_id: str) -> ParsedHandoffCommand | None:
        """コマンドを解析"""
        text = text.strip()

        # ハンドオフ登録
        if self._is_register_command(text):
            return self._parse_register(text, user_id)

        # ハンドオフ一覧
        if self._is_list_command(text):
            return self._parse_list(text, user_id)

        # ハンドオフ完了
        if self._is_complete_command(text):
            return self._parse_complete(text, user_id)

        return None

    def _is_register_command(self, text: str) -> bool:
        """ハンドオフ登録コマンドか判定"""
        patterns = [
            r"引き継ぎ",
            r"ハンドオフ",
            r"引継ぎ",
        ]
        return any(re.search(pattern, text) for pattern in patterns) and not re.search(
            r"一覧|リスト|完了", text
        )

    def _is_list_command(self, text: str) -> bool:
        """ハンドオフ一覧コマンドか判定"""
        patterns = [
            r"引き継ぎ.*一覧",
            r"引き継ぎ.*リスト",
            r"ハンドオフ.*一覧",
        ]
        return any(re.search(pattern, text) for pattern in patterns)

    def _is_complete_command(self, text: str) -> bool:
        """ハンドオフ完了コマンドか判定"""
        patterns = [
            r"ハンドオフ.*完了",
            r"引き継ぎ.*完了",
        ]
        return any(re.search(pattern, text) for pattern in patterns)

    def _parse_register(self, text: str, user_id: str) -> ParsedHandoffCommand:
        """ハンドオフ登録コマンドを解析"""
        # タスクID抽出
        task_id = self._extract_task_id(text)

        # 引き継ぎ先ユーザー抽出
        to_user_match = re.search(r"<@([A-Z0-9]+)>", text)
        to_user_id = to_user_match.group(1) if to_user_match else None

        # 引き継ぎ時刻抽出
        handoff_at = self._extract_handoff_time(text)

        # 進捗メモ抽出（「」内）
        progress_match = re.search(r"「([^」]+)」", text)
        progress_note = progress_match.group(1) if progress_match else "進捗メモなし"

        return ParsedHandoffCommand(
            command_type="register",
            user_id=user_id,
            task_id=task_id,
            to_user_id=to_user_id,
            progress_note=progress_note,
            handoff_at=handoff_at,
        )

    def _parse_list(self, text: str, user_id: str) -> ParsedHandoffCommand:
        """ハンドオフ一覧コマンドを解析"""
        return ParsedHandoffCommand(
            command_type="list",
            user_id=user_id,
        )

    def _parse_complete(self, text: str, user_id: str) -> ParsedHandoffCommand:
        """ハンドオフ完了コマンドを解析"""
        # UUID抽出
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        uuid_match = re.search(uuid_pattern, text, re.IGNORECASE)

        handoff_id = None
        if uuid_match:
            handoff_id = UUID(uuid_match.group(0))

        return ParsedHandoffCommand(
            command_type="complete",
            user_id=user_id,
            handoff_id=handoff_id,
        )

    def _extract_task_id(self, text: str) -> UUID | None:
        """タスクIDを抽出"""
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        uuid_match = re.search(uuid_pattern, text, re.IGNORECASE)

        if uuid_match:
            return UUID(uuid_match.group(0))
        return None

    def _extract_handoff_time(self, text: str) -> datetime | None:
        """引き継ぎ時刻を抽出"""
        now = datetime.now()

        # 「明日9時」
        tomorrow_match = re.search(r"明日.*?(\d+)時", text)
        if tomorrow_match:
            hour = int(tomorrow_match.group(1))
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)

        # 「今日15時」
        today_match = re.search(r"今日.*?(\d+)時", text)
        if today_match:
            hour = int(today_match.group(1))
            return now.replace(hour=hour, minute=0, second=0, microsecond=0)

        # 「N時間後」
        hours_match = re.search(r"(\d+)時間後", text)
        if hours_match:
            hours = int(hours_match.group(1))
            return now + timedelta(hours=hours)

        # デフォルト: 2時間後
        return now + timedelta(hours=2)
