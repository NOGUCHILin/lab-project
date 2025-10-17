# Phase 3: Handoff Management - Design

## System Architecture

### Handoff Registration Flow

```
User (Slack) → HandoffCommandParser → RegisterHandoffUseCase → PostgreSQLHandoffRepository → PostgreSQL
                                            ↓
                                       ClaudeAdapter (応答生成 + 進捗確認)
```

### Reminder Scheduler Flow

```
Cron Job (every minute) → SendHandoffReminderUseCase → PostgreSQLHandoffRepository.list_pending_reminders()
                                                              ↓
                                                         Slack DM送信
                                                              ↓
                                                         mark_reminded()
```

## Domain Model

### Handoff Entity

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Handoff:
    id: UUID
    task_id: UUID | None  # Taskに関連しない引き継ぎも可能
    from_user_id: str     # Slack User ID
    to_user_id: str       # Slack User ID
    progress_note: str    # 現在の進捗状況
    next_steps: str       # 次のステップ・注意点
    handoff_at: datetime  # 引き継ぎ予定日時
    reminded_at: datetime | None  # リマインダー送信済み日時
    completed_at: datetime | None # 完了日時
    created_at: datetime

    def is_pending(self) -> bool:
        """未完了か？"""
        return self.completed_at is None

    def is_reminder_needed(self, current_time: datetime) -> bool:
        """リマインダー送信が必要か？"""
        if self.reminded_at is not None:
            return False  # 既に送信済み

        if not self.is_pending():
            return False  # 完了済み

        # 引き継ぎ予定時刻の10分前
        reminder_time = self.handoff_at - timedelta(minutes=10)
        return current_time >= reminder_time
```

## Use Case Implementation

### RegisterHandoffUseCase

```python
from src.domain.models.handoff import Handoff
from src.domain.repositories.handoff_repository import HandoffRepository
from src.application.dto.handoff_dto import CreateHandoffDTO

class RegisterHandoffUseCase:
    def __init__(self, handoff_repository: HandoffRepository):
        self._handoff_repository = handoff_repository

    async def execute(self, dto: CreateHandoffDTO) -> Handoff:
        """ハンドオフ登録

        Args:
            dto: ハンドオフ作成DTO
                - task_id: UUID | None
                - from_user_id: str
                - to_user_id: str
                - progress_note: str
                - next_steps: str
                - handoff_at: datetime

        Returns:
            作成されたHandoff
        """
        # Validation
        if dto.handoff_at < datetime.utcnow():
            raise ValueError("引き継ぎ予定日時は未来である必要があります")

        # Entity作成
        handoff = Handoff(
            task_id=dto.task_id,
            from_user_id=dto.from_user_id,
            to_user_id=dto.to_user_id,
            progress_note=dto.progress_note,
            next_steps=dto.next_steps,
            handoff_at=dto.handoff_at,
        )

        # Repository保存
        return await self._handoff_repository.create(handoff)
```

### SendHandoffReminderUseCase

```python
from src.infrastructure.slack_client import SlackClient

class SendHandoffReminderUseCase:
    def __init__(
        self,
        handoff_repository: HandoffRepository,
        slack_client: SlackClient,
    ):
        self._handoff_repository = handoff_repository
        self._slack_client = slack_client

    async def execute(self) -> int:
        """保留中のリマインダーを送信

        Returns:
            送信したリマインダー数
        """
        now = datetime.utcnow()
        reminder_time = now + timedelta(minutes=10)

        # 送信対象取得
        handoffs = await self._handoff_repository.list_pending_reminders(reminder_time)

        sent_count = 0
        for handoff in handoffs:
            try:
                # DM送信
                await self._slack_client.chat_postMessage(
                    channel=handoff.to_user_id,  # User ID → DM
                    text=self._format_reminder(handoff),
                )

                # リマインダー送信済みマーク
                await self._handoff_repository.mark_reminded(handoff.id)
                sent_count += 1

                logger.info("Handoff reminder sent", extra={
                    "handoff_id": str(handoff.id),
                    "to_user_id": handoff.to_user_id,
                })

            except Exception as e:
                logger.error("Failed to send handoff reminder", extra={
                    "handoff_id": str(handoff.id),
                    "error": str(e),
                })
                # 失敗してもmark_remindedしない（次回再送信）

        return sent_count

    def _format_reminder(self, handoff: Handoff) -> str:
        """リマインダーメッセージ生成"""
        minutes_until = int((handoff.handoff_at - datetime.utcnow()).total_seconds() / 60)

        return f"""🔔 引き継ぎリマインダー

{minutes_until}分後（{handoff.handoff_at.strftime('%H:%M')}）に以下の引き継ぎがあります：

タスク: {handoff.task_id or "（タスク名不明）"}
引き継ぎ元: <@{handoff.from_user_id}>

現在の進捗:
{handoff.progress_note}

次のステップ:
{handoff.next_steps}

不明点があれば <@{handoff.from_user_id}> に確認してください。"""
```

## Command Parser

### HandoffCommandParser

```python
class HandoffCommandParser:
    """ハンドオフコマンド解析"""

    def parse(self, text: str, user_id: str) -> ParsedHandoffCommand:
        """コマンド解析

        Args:
            text: ユーザーの入力テキスト
            user_id: 実行ユーザーID

        Returns:
            ParsedHandoffCommand
        """
        text = text.strip()

        # ハンドオフ登録
        if "引き継ぎ" in text and "を" in text and "に" in text:
            return self._parse_register(text, user_id)

        # ハンドオフ一覧
        if "引き継ぎ一覧" in text:
            return ParsedHandoffCommand(action="list", user_id=user_id)

        # ハンドオフ完了
        if "ハンドオフ" in text and "完了" in text:
            return self._parse_complete(text, user_id)

        raise ValueError("ハンドオフコマンドを解析できませんでした")

    def _parse_register(self, text: str, user_id: str) -> ParsedHandoffCommand:
        """ハンドオフ登録コマンド解析

        Format: 「タスク名」を @ユーザー に 明日9時 から引き継ぎ
        """
        import re

        # タスク名抽出（「」で囲まれた部分）
        task_match = re.search(r"「(.+?)」", text)
        task_name = task_match.group(1) if task_match else None

        # 引き継ぎ先ユーザー
        to_user_match = re.search(r"<@([A-Z0-9]+)>", text)
        if not to_user_match:
            raise ValueError("引き継ぎ先ユーザーが見つかりません（例: @田中太郎）")
        to_user_id = to_user_match.group(1)

        # 引き継ぎ予定日時
        handoff_at = None
        date_match = re.search(r"(明日|今日|[0-9]+日後)\s*([0-9]{1,2})[:：時]", text)
        if date_match:
            handoff_at = self._parse_datetime(date_match.group(0))
        else:
            # デフォルト: 明日9:00
            handoff_at = (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        return ParsedHandoffCommand(
            action="register",
            user_id=user_id,
            task_name=task_name,
            to_user_id=to_user_id,
            handoff_at=handoff_at,
        )
```

## Response Formatter

### HandoffResponseFormatter

```python
class HandoffResponseFormatter:
    """ハンドオフ応答メッセージ生成"""

    @staticmethod
    def format_handoff_created(handoff: Handoff) -> str:
        """ハンドオフ登録完了メッセージ"""
        return f"""📝 ハンドオフ登録

タスク: {handoff.task_id or "（タスク名不明）"}
引き継ぎ: <@{handoff.from_user_id}> → <@{handoff.to_user_id}>
開始予定: {handoff.handoff_at.strftime('%m/%d %H:%M')}

進捗状況を教えてください。"""

    @staticmethod
    def format_handoff_list(handoffs: list[Handoff]) -> str:
        """ハンドオフ一覧"""
        if not handoffs:
            return "あなた宛の引き継ぎはありません。"

        lines = [f"📋 あなた宛の引き継ぎ（{len(handoffs)}件）:\n"]

        for i, handoff in enumerate(handoffs, 1):
            lines.append(f"{i}. {handoff.task_id or '（タスク名不明）'}")
            lines.append(f"   - 引き継ぎ元: <@{handoff.from_user_id}>")
            lines.append(f"   - 開始予定: {handoff.handoff_at.strftime('%m/%d %H:%M')}")
            lines.append(f"   - 進捗: {handoff.progress_note}")
            lines.append(f"   - 次のステップ: {handoff.next_steps}\n")

        return "\n".join(lines)

    @staticmethod
    def format_handoff_completed(handoff: Handoff) -> str:
        """ハンドオフ完了メッセージ"""
        duration_hours = (handoff.completed_at - handoff.handoff_at).total_seconds() / 3600

        return f"""✅ ハンドオフ完了

タスク: {handoff.task_id or "（タスク名不明）"}
引き継ぎ元: <@{handoff.from_user_id}> → あなた
開始: {handoff.handoff_at.strftime('%m/%d %H:%M')}
完了: {handoff.completed_at.strftime('%m/%d %H:%M')}
所要時間: {duration_hours:.1f}時間

<@{handoff.from_user_id}> に完了通知を送信しました。"""
```

## Reminder Scheduler

### Cron Job (systemd timer)

```nix
# NixOS設定

systemd.timers.nakamura-misaki-reminder = {
  wantedBy = [ "timers.target" ];
  timerConfig = {
    OnBootSec = "1m";
    OnUnitActiveSec = "1m";  # 毎分実行
    Unit = "nakamura-misaki-reminder.service";
  };
};

systemd.services.nakamura-misaki-reminder = {
  description = "nakamura-misaki Handoff Reminder";
  serviceConfig = {
    Type = "oneshot";
    ExecStart = "${pkgs.python3}/bin/python /path/to/send_reminders.py";
    User = "nakamura-misaki";
  };
};
```

### send_reminders.py

```python
#!/usr/bin/env python3
"""ハンドオフリマインダー送信スクリプト"""

import asyncio
from src.infrastructure.di import build_send_handoff_reminder_use_case

async def main():
    use_case = await build_send_handoff_reminder_use_case()
    sent_count = await use_case.execute()
    print(f"Sent {sent_count} reminders")

if __name__ == "__main__":
    asyncio.run(main())
```

## Task Context Update

```python
# src/adapters/secondary/claude_adapter.py

async def _generate_task_context(self, user_id: str) -> str:
    """Generate task context for system prompt

    Phase 2: Returns today's tasks
    Phase 3: Also returns pending handoffs
    """
    # 今日のタスク取得
    tasks = await self.task_repository.list_due_today(user_id)

    context = "今日のタスク:\n"
    if tasks:
        for task in tasks:
            due_time = task.due_at.strftime("%H:%M") if task.due_at else "期限なし"
            context += f"- [{task.id}] {task.title} ({due_time})\n"
    else:
        context += "- なし\n"

    # 保留中のハンドオフ取得
    handoffs = await self.handoff_repository.list_by_to_user(user_id)

    if handoffs:
        context += "\n保留中のハンドオフ:\n"
        for handoff in handoffs:
            context += f"- [{handoff.task_id}] <@{handoff.from_user_id}> → あなた ({handoff.handoff_at.strftime('%m/%d %H:%M')})\n"

    return context
```

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_handoff_command_parser.py

def test_parse_register_handoff():
    """ハンドオフ登録コマンド解析"""
    parser = HandoffCommandParser()

    command = parser.parse(
        "「API統合」を @U02XYZ に 明日9時 から引き継ぎ",
        "U01ABC123"
    )

    assert command.action == "register"
    assert command.task_name == "API統合"
    assert command.to_user_id == "U02XYZ"
    assert command.handoff_at.hour == 9
```

### Integration Tests

```python
# tests/integration/test_handoff_reminder.py

@pytest.mark.asyncio
async def test_send_handoff_reminder():
    """ハンドオフリマインダー送信"""
    # ハンドオフ登録（10分後）
    handoff = await register_handoff_use_case.execute(
        CreateHandoffDTO(
            from_user_id="U01ABC123",
            to_user_id="U02XYZ",
            handoff_at=datetime.utcnow() + timedelta(minutes=10),
            progress_note="認証部分完了",
            next_steps="決済API実装",
        )
    )

    # リマインダー送信
    sent_count = await send_handoff_reminder_use_case.execute()

    assert sent_count == 1

    # リマインダー送信済みマーク確認
    updated = await handoff_repository.get(handoff.id)
    assert updated.reminded_at is not None
```

## Monitoring

### Metrics

- **Reminder送信成功率**: 99%以上
- **Reminder送信遅延**: 10秒以内
- **Handoff登録時間**: 200ms以内

### Logging

```python
logger.info("Handoff reminder sent", extra={
    "handoff_id": str(handoff.id),
    "to_user_id": handoff.to_user_id,
    "handoff_at": handoff.handoff_at.isoformat(),
    "delay_seconds": (datetime.utcnow() - expected_send_time).total_seconds(),
})
```
