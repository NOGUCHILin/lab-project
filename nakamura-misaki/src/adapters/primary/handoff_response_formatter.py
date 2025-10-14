"""HandoffResponseFormatter - ハンドオフ関連の応答フォーマット"""

from src.application.dto.handoff_dto import HandoffDTO


class HandoffResponseFormatter:
    """ハンドオフ応答フォーマッター"""

    def format_handoff_created(self, handoff: HandoffDTO) -> str:
        """ハンドオフ作成応答"""
        handoff_time = handoff.handoff_at.strftime("%m/%d %H:%M")
        response = (
            f"✅ ハンドオフを登録しました\n\n"
            f"**タスクID**: `{handoff.task_id}`\n"
            f"**引き継ぎ先**: <@{handoff.to_user_id}>\n"
            f"**引き継ぎ時刻**: {handoff_time}\n"
            f"**進捗**: {handoff.progress_note}\n\n"
            f"引き継ぎ予定時刻の10分前にリマインダーDMを送信します。"
        )
        return response

    def format_handoff_list(self, handoffs: list[HandoffDTO]) -> str:
        """ハンドオフ一覧応答"""
        if not handoffs:
            return "📝 保留中の引き継ぎはありません"

        response = f"📝 保留中の引き継ぎ一覧（{len(handoffs)}件）\n\n"

        for handoff in handoffs:
            handoff_time = handoff.handoff_at.strftime("%m/%d %H:%M")
            response += (
                f"🔔 **タスクID**: `{handoff.task_id}`\n"
                f"**引き継ぎ元**: <@{handoff.from_user_id}>\n"
                f"**引き継ぎ時刻**: {handoff_time}\n"
                f"**進捗**: {handoff.progress_note}\n"
                f"**ID**: `{handoff.id}`\n\n"
            )

        return response

    def format_handoff_completed(self, handoff: HandoffDTO) -> str:
        """ハンドオフ完了応答"""
        return (
            f"✅ ハンドオフを完了しました\n\n"
            f"**タスクID**: `{handoff.task_id}`\n"
            f"**引き継ぎ元**: <@{handoff.from_user_id}>"
        )

    def format_handoff_reminder(self, handoff: HandoffDTO) -> str:
        """ハンドオフリマインダー応答"""
        handoff_time = handoff.handoff_at.strftime("%H:%M")
        return (
            f"🔔 ハンドオフのリマインダー\n\n"
            f"**タスクID**: `{handoff.task_id}`\n"
            f"**引き継ぎ元**: <@{handoff.from_user_id}>\n"
            f"**引き継ぎ時刻**: {handoff_time}\n"
            f"**進捗**: {handoff.progress_note}"
        )
