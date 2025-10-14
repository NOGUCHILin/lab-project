"""TaskCommandParser - タスク関連コマンドの自然言語解析"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID


@dataclass
class ParsedTaskCommand:
    """解析済みタスクコマンド"""

    command_type: str  # "register", "list", "complete", "update"
    user_id: str
    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None
    task_id: UUID | None = None
    status: str | None = None


class TaskCommandParser:
    """タスクコマンドパーサー"""

    def parse(self, text: str, user_id: str) -> ParsedTaskCommand | None:
        """コマンドを解析"""
        text = text.strip()

        # タスク登録
        if self._is_register_command(text):
            return self._parse_register(text, user_id)

        # タスク一覧
        if self._is_list_command(text):
            return self._parse_list(text, user_id)

        # タスク完了
        if self._is_complete_command(text):
            return self._parse_complete(text, user_id)

        return None

    def _is_register_command(self, text: str) -> bool:
        """タスク登録コマンドか判定"""
        patterns = [
            r"タスク.*登録",
            r"タスク.*追加",
            r"タスク.*作成",
            r".*をやる",
            r".*をする",
            r".*を実施",
        ]
        return any(re.search(pattern, text) for pattern in patterns)

    def _is_list_command(self, text: str) -> bool:
        """タスク一覧コマンドか判定"""
        patterns = [
            r"タスク.*一覧",
            r"タスク.*リスト",
            r"今日のタスク",
            r"タスクを見せて",
            r"タスクは？",
        ]
        return any(re.search(pattern, text) for pattern in patterns)

    def _is_complete_command(self, text: str) -> bool:
        """タスク完了コマンドか判定"""
        patterns = [
            r"タスク.*完了",
            r"タスク.*終わった",
            r"完了.*タスク",
        ]
        return any(re.search(pattern, text) for pattern in patterns)

    def _parse_register(self, text: str, user_id: str) -> ParsedTaskCommand:
        """タスク登録コマンドを解析"""
        # タイトル抽出（「」内または最初の文を抽出）
        title_match = re.search(r"「([^」]+)」", text)
        if title_match:
            title = title_match.group(1)
        else:
            # 「をやる」「をする」の前の部分を抽出
            title_match = re.search(r"(.+?)(?:をやる|をする|を実施)", text)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = text[:50]  # Fallback

        # 期限抽出
        due_at = self._extract_due_date(text)

        return ParsedTaskCommand(
            command_type="register",
            user_id=user_id,
            title=title,
            due_at=due_at,
        )

    def _parse_list(self, text: str, user_id: str) -> ParsedTaskCommand:
        """タスク一覧コマンドを解析"""
        # ステータスフィルタ
        status = None
        if re.search(r"進行中|作業中", text):
            status = "in_progress"
        elif re.search(r"完了", text):
            status = "completed"
        elif re.search(r"保留|未着手", text):
            status = "pending"

        return ParsedTaskCommand(
            command_type="list",
            user_id=user_id,
            status=status,
        )

    def _parse_complete(self, text: str, user_id: str) -> ParsedTaskCommand:
        """タスク完了コマンドを解析"""
        # UUID抽出
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        uuid_match = re.search(uuid_pattern, text, re.IGNORECASE)

        task_id = None
        if uuid_match:
            task_id = UUID(uuid_match.group(0))

        return ParsedTaskCommand(
            command_type="complete",
            user_id=user_id,
            task_id=task_id,
        )

    def _extract_due_date(self, text: str) -> datetime | None:
        """期限を抽出"""
        now = datetime.now()

        # 「今日」
        if re.search(r"今日", text):
            return now.replace(hour=23, minute=59, second=59, microsecond=0)

        # 「明日」
        if re.search(r"明日", text):
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)

        # 「明後日」
        if re.search(r"明後日", text):
            day_after_tomorrow = now + timedelta(days=2)
            return day_after_tomorrow.replace(
                hour=23, minute=59, second=59, microsecond=0
            )

        # 「N日後」
        days_match = re.search(r"(\d+)日後", text)
        if days_match:
            days = int(days_match.group(1))
            future = now + timedelta(days=days)
            return future.replace(hour=23, minute=59, second=59, microsecond=0)

        # 「来週」
        if re.search(r"来週", text):
            next_week = now + timedelta(days=7)
            return next_week.replace(hour=23, minute=59, second=59, microsecond=0)

        return None
