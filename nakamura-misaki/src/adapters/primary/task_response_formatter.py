"""TaskResponseFormatter - タスク関連の応答フォーマット"""

from src.application.dto.task_dto import TaskDTO


class TaskResponseFormatter:
    """タスク応答フォーマッター"""

    def format_task_created(self, task: TaskDTO) -> str:
        """タスク作成応答"""
        response = f"✅ タスクを登録しました\n\n**{task.title}**"

        if task.due_at:
            due_str = task.due_at.strftime("%m/%d %H:%M")
            response += f"\n期限: {due_str}"

        return response

    def format_task_list(self, tasks: list[TaskDTO]) -> str:
        """タスク一覧応答"""
        if not tasks:
            return "📝 該当するタスクはありません"

        response = f"📝 タスク一覧（{len(tasks)}件）\n\n"

        for task in tasks:
            status_emoji = self._get_status_emoji(task.status)
            response += f"{status_emoji} **{task.title}**"

            if task.due_at:
                due_str = task.due_at.strftime("%m/%d %H:%M")
                response += f" (期限: {due_str})"

            response += f"\nID: `{task.id}`\n\n"

        return response

    def format_task_completed(self, task: TaskDTO) -> str:
        """タスク完了応答"""
        return f"✅ タスクを完了しました\n\n**{task.title}**"

    def format_task_updated(self, task: TaskDTO) -> str:
        """タスク更新応答"""
        return f"✅ タスクを更新しました\n\n**{task.title}**"

    def _get_status_emoji(self, status: str) -> str:
        """ステータスに応じた絵文字を返す"""
        status_map = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "cancelled": "❌",
        }
        return status_map.get(status, "📝")
