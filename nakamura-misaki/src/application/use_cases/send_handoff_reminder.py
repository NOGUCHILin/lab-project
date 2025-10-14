"""SendHandoffReminderUseCase - ハンドオフリマインダー送信"""

from datetime import datetime, timedelta

from src.domain.repositories.handoff_repository import HandoffRepository


class SendHandoffReminderUseCase:
    """ハンドオフリマインダー送信ユースケース"""

    def __init__(
        self,
        handoff_repository: HandoffRepository,
        slack_client,  # SlackClient (実装は後ほど)
    ):
        self._handoff_repository = handoff_repository
        self._slack_client = slack_client

    async def execute(self) -> int:
        """リマインダー送信が必要なハンドオフを検出して送信

        Returns:
            送信したリマインダーの件数
        """
        # 10分後までのハンドオフを取得
        check_time = datetime.now() + timedelta(minutes=10)
        handoffs = await self._handoff_repository.list_pending_reminders(check_time)

        sent_count = 0

        for handoff in handoffs:
            if handoff.is_reminder_needed(datetime.now()):
                try:
                    # Slack DM送信
                    await self._send_reminder_dm(handoff)

                    # リマインダー送信済みとしてマーク
                    await self._handoff_repository.mark_reminded(handoff.id)
                    sent_count += 1

                except Exception as e:
                    # エラー時はmark_remindedしない（次回再試行）
                    print(f"Failed to send reminder for handoff {handoff.id}: {e}")

        return sent_count

    async def _send_reminder_dm(self, handoff):
        """リマインダーDMを送信"""
        handoff_time = handoff.handoff_at.strftime("%H:%M")
        message = (
            f"🔔 ハンドオフのリマインダー\n\n"
            f"**タスクID**: {handoff.task_id}\n"
            f"**引き継ぎ元**: <@{handoff.from_user_id}>\n"
            f"**引き継ぎ時刻**: {handoff_time}\n"
            f"**進捗**: {handoff.progress_note}"
        )

        await self._slack_client.send_dm(handoff.to_user_id, message)
