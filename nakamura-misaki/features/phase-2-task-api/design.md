# Phase 2: Task API - Design

## System Architecture

### Data Flow: Task Registration

```
User (Slack) → SlackEventAdapter → TaskCommandParser → RegisterTaskUseCase → PostgreSQLTaskRepository → PostgreSQL
                                                              ↓
                                                         ClaudeAdapter (応答生成)
```

### Data Flow: Task Context Injection

```
User Message → ClaudeAdapter.send_message()
                    ↓
               _generate_task_context()
                    ↓
               PostgreSQLTaskRepository.list_due_today()
                    ↓
               System Prompt Variable Replacement ({task_context})
                    ↓
               Claude API
```

## Use Case Implementation

### RegisterTaskUseCase

```python
from src.domain.models.task import Task
from src.domain.repositories.task_repository import TaskRepository
from src.application.dto.task_dto import CreateTaskDTO

class RegisterTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, dto: CreateTaskDTO) -> Task:
        """タスク登録

        Args:
            dto: タスク作成DTO
                - title: str
                - description: str | None
                - assignee_user_id: str
                - creator_user_id: str
                - due_at: datetime | None

        Returns:
            作成されたTask

        Raises:
            ValueError: バリデーションエラー
        """
        # Validation
        if not dto.title or len(dto.title) > 200:
            raise ValueError("タスク名は1-200文字で指定してください")

        # Entity作成
        task = Task(
            title=dto.title,
            description=dto.description,
            assignee_user_id=dto.assignee_user_id,
            creator_user_id=dto.creator_user_id,
            status="pending",
            due_at=dto.due_at,
        )

        # Repository保存
        return await self._task_repository.create(task)
```

### QueryTodayTasksUseCase

```python
class QueryTodayTasksUseCase:
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, user_id: str) -> list[Task]:
        """今日のタスク一覧取得

        Args:
            user_id: Slack User ID

        Returns:
            今日が期限のタスク一覧（期限順）
        """
        return await self._task_repository.list_due_today(user_id)
```

### CompleteTaskUseCase

```python
class CompleteTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, task_id: UUID, user_id: str) -> Task:
        """タスク完了

        Args:
            task_id: タスクID
            user_id: 完了操作を行ったユーザーID

        Returns:
            更新されたTask

        Raises:
            ValueError: タスクが見つからない、権限がない
        """
        # タスク取得
        task = await self._task_repository.get(task_id)
        if not task:
            raise ValueError(f"タスクが見つかりません: {task_id}")

        # 権限チェック（担当者のみ完了可能）
        if task.assignee_user_id != user_id:
            raise ValueError("担当者のみタスクを完了できます")

        # ステータス更新
        task.complete()  # Domain modelのビジネスロジック

        # Repository更新
        return await self._task_repository.update(task)
```

## Command Parser

### TaskCommandParser

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParsedCommand:
    action: str  # "register", "list_today", "list_all", "complete", "delete"
    task_id: UUID | None = None
    title: str | None = None
    due_at: datetime | None = None
    assignee_user_id: str | None = None

class TaskCommandParser:
    """自然言語のタスクコマンドを解析"""

    def parse(self, text: str, user_id: str) -> ParsedCommand:
        """コマンド解析

        Args:
            text: ユーザーの入力テキスト
            user_id: ユーザーID（デフォルト担当者）

        Returns:
            ParsedCommand

        Raises:
            ValueError: 解析失敗
        """
        text = text.strip()

        # タスク登録
        if "タスク登録" in text or "タスク追加" in text:
            return self._parse_register(text, user_id)

        # タスク一覧
        if "今日のタスク" in text:
            return ParsedCommand(action="list_today")
        if "タスク一覧" in text:
            return ParsedCommand(action="list_all")

        # タスク完了
        if "を完了" in text or "完了" in text:
            return self._parse_complete(text)

        # タスク削除
        if "を削除" in text or "削除" in text:
            return self._parse_delete(text)

        raise ValueError("コマンドを解析できませんでした")

    def _parse_register(self, text: str, user_id: str) -> ParsedCommand:
        """タスク登録コマンドを解析

        Format: タスク登録: [タスク名] 期限: [日時] 担当: [ユーザー]
        """
        import re

        # タスク名抽出
        title_match = re.search(r"タスク登録[:：]\s*(.+?)(?:期限|担当|$)", text)
        if not title_match:
            raise ValueError("タスク名が見つかりません")
        title = title_match.group(1).strip()

        # 期限抽出
        due_at = None
        due_match = re.search(r"期限[:：]\s*(.+?)(?:担当|$)", text)
        if due_match:
            due_str = due_match.group(1).strip()
            due_at = self._parse_datetime(due_str)

        # 担当者抽出（デフォルトは自分）
        assignee_user_id = user_id
        assignee_match = re.search(r"担当[:：]\s*<@([A-Z0-9]+)>", text)
        if assignee_match:
            assignee_user_id = assignee_match.group(1)

        return ParsedCommand(
            action="register",
            title=title,
            due_at=due_at,
            assignee_user_id=assignee_user_id,
        )

    def _parse_datetime(self, text: str) -> datetime:
        """自然言語の日時表現を解析

        Examples:
            - "明日15時" → 2025-10-15 15:00:00
            - "来週月曜" → 2025-10-21 09:00:00
            - "今日中" → 2025-10-14 23:59:59
            - "3日後" → 2025-10-17 23:59:59
        """
        from dateutil import parser as dateparser
        from dateutil.relativedelta import relativedelta
        import re

        now = datetime.now()

        # "明日"
        if "明日" in text:
            base = now + relativedelta(days=1)
            # 時刻指定あり
            time_match = re.search(r"(\d{1,2})[:：時]", text)
            if time_match:
                hour = int(time_match.group(1))
                return base.replace(hour=hour, minute=0, second=0, microsecond=0)
            return base.replace(hour=23, minute=59, second=59, microsecond=0)

        # "今日中"
        if "今日" in text:
            return now.replace(hour=23, minute=59, second=59, microsecond=0)

        # "N日後"
        days_match = re.search(r"(\d+)日後", text)
        if days_match:
            days = int(days_match.group(1))
            return (now + relativedelta(days=days)).replace(hour=23, minute=59, second=59, microsecond=0)

        # "来週月曜"
        if "来週" in text:
            days_ahead = 7
            if "月" in text:
                days_ahead += (0 - now.weekday()) % 7
            elif "火" in text:
                days_ahead += (1 - now.weekday()) % 7
            # ... (他の曜日)
            return (now + relativedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)

        # dateutil.parserでパース試行
        try:
            return dateparser.parse(text, fuzzy=True)
        except Exception:
            raise ValueError(f"日時を解析できませんでした: {text}")
```

## Task Context Generation

### ClaudeAdapter._generate_task_context()

```python
class ClaudeAdapter:
    async def _generate_task_context(self, user_id: str) -> str:
        """Generate task context for system prompt

        Phase 2: Returns today's tasks
        Phase 3: Also returns pending handoffs
        """
        # 今日のタスク取得
        tasks = await self.task_repository.list_due_today(user_id)

        if not tasks:
            return "今日のタスク: なし"

        context = "今日のタスク:\n"
        for task in tasks:
            due_time = task.due_at.strftime("%H:%M") if task.due_at else "期限なし"
            status_icon = {
                "pending": "⏸️",
                "in_progress": "▶️",
                "completed": "✅",
                "cancelled": "❌",
            }.get(task.status, "")

            context += f"- [{task.id}] {task.title} ({due_time}) {status_icon}\n"

        return context
```

## Response Formatter

### TaskResponseFormatter

```python
class TaskResponseFormatter:
    """タスク応答メッセージ生成"""

    @staticmethod
    def format_task_created(task: Task) -> str:
        """タスク登録完了メッセージ"""
        return f"""✅ タスク登録完了

- タスク: {task.title}
- 担当: <@{task.assignee_user_id}>
- 期限: {task.due_at.strftime('%Y-%m-%d %H:%M') if task.due_at else '期限なし'}
- ID: {task.id}"""

    @staticmethod
    def format_today_tasks(tasks: list[Task]) -> str:
        """今日のタスク一覧"""
        if not tasks:
            return "今日のタスク: なし"

        lines = [f"今日のタスク（{len(tasks)}件）:"]
        for task in tasks:
            due_time = task.due_at.strftime("%H:%M") if task.due_at else "期限なし"
            status_icon = {
                "pending": "⏸️",
                "in_progress": "▶️",
                "completed": "✅",
            }.get(task.status, "")

            lines.append(f"- [{task.id}] {task.title} ({due_time}) {status_icon}")

        return "\n".join(lines)

    @staticmethod
    def format_task_completed(task: Task, duration_hours: float | None = None) -> str:
        """タスク完了メッセージ"""
        msg = f"""✅ タスク完了

タスク: {task.title}
完了時刻: {task.completed_at.strftime('%Y-%m-%d %H:%M')}"""

        if duration_hours:
            msg += f"\n所要時間: {duration_hours:.1f}時間"

        return msg

    @staticmethod
    def format_error(error: str) -> str:
        """エラーメッセージ"""
        return f"❌ エラー: {error}"
```

## Slack Integration

### SlackEventAdapter

```python
class SlackEventAdapter:
    def __init__(
        self,
        claude_adapter: ClaudeAdapter,
        task_command_parser: TaskCommandParser,
        register_task_use_case: RegisterTaskUseCase,
        query_today_tasks_use_case: QueryTodayTasksUseCase,
        complete_task_use_case: CompleteTaskUseCase,
    ):
        # ...

    async def handle_message(self, event: dict):
        """Slackメッセージ処理"""
        text = event["text"]
        user_id = event["user"]

        # タスクコマンドか判定
        if self._is_task_command(text):
            await self._handle_task_command(text, user_id, event["channel"])
        else:
            # 通常のClaude応答
            await self._handle_normal_message(text, user_id, event["channel"])

    def _is_task_command(self, text: str) -> bool:
        """タスクコマンドか判定"""
        keywords = ["タスク登録", "タスク追加", "今日のタスク", "タスク一覧", "を完了", "を削除"]
        return any(keyword in text for keyword in keywords)

    async def _handle_task_command(self, text: str, user_id: str, channel: str):
        """タスクコマンド処理"""
        try:
            # コマンド解析
            command = self.task_command_parser.parse(text, user_id)

            # Use Case実行
            if command.action == "register":
                task = await self.register_task_use_case.execute(
                    CreateTaskDTO(
                        title=command.title,
                        assignee_user_id=command.assignee_user_id,
                        creator_user_id=user_id,
                        due_at=command.due_at,
                    )
                )
                response = TaskResponseFormatter.format_task_created(task)

            elif command.action == "list_today":
                tasks = await self.query_today_tasks_use_case.execute(user_id)
                response = TaskResponseFormatter.format_today_tasks(tasks)

            elif command.action == "complete":
                task = await self.complete_task_use_case.execute(command.task_id, user_id)
                response = TaskResponseFormatter.format_task_completed(task)

            # Slackに返信
            await self.slack_client.chat_postMessage(channel=channel, text=response)

        except ValueError as e:
            # エラーメッセージ
            await self.slack_client.chat_postMessage(
                channel=channel,
                text=TaskResponseFormatter.format_error(str(e)),
            )
```

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_task_command_parser.py

def test_parse_register_with_due_date():
    """タスク登録コマンド解析（期限あり）"""
    parser = TaskCommandParser()

    command = parser.parse("タスク登録: API統合 期限: 明日15時", "U01ABC123")

    assert command.action == "register"
    assert command.title == "API統合"
    assert command.due_at.hour == 15
    assert command.assignee_user_id == "U01ABC123"

def test_parse_complete():
    """タスク完了コマンド解析"""
    parser = TaskCommandParser()

    command = parser.parse("タスク abc12345 を完了", "U01ABC123")

    assert command.action == "complete"
    assert command.task_id == UUID("abc12345")
```

### Integration Tests

```python
# tests/integration/test_task_workflow.py

@pytest.mark.asyncio
async def test_task_crud_workflow():
    """タスクCRUDワークフロー"""
    # 1. タスク登録
    task = await register_task_use_case.execute(
        CreateTaskDTO(
            title="API統合",
            assignee_user_id="U01ABC123",
            creator_user_id="U01ABC123",
            due_at=datetime(2025, 10, 15, 15, 0),
        )
    )

    # 2. 今日のタスク一覧
    tasks = await query_today_tasks_use_case.execute("U01ABC123")
    assert len(tasks) == 1

    # 3. タスク完了
    completed = await complete_task_use_case.execute(task.id, "U01ABC123")
    assert completed.status == "completed"

    # 4. タスク削除
    await delete_task_use_case.execute(task.id, "U01ABC123")
    deleted = await task_repository.get(task.id)
    assert deleted is None
```

### E2E Tests

```python
# tests/e2e/test_task_slack_commands.py

@pytest.mark.asyncio
async def test_register_task_via_slack():
    """Slack経由でタスク登録"""
    response = await send_slack_message(
        "@中村美咲 タスク登録: API統合 期限: 明日15時"
    )

    assert "✅ タスク登録完了" in response
    assert "API統合" in response
```

## Performance Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def _parse_datetime_cached(text: str) -> datetime:
    """日時解析（キャッシュあり）"""
    return _parse_datetime(text)
```

### Batch Loading

```python
async def list_tasks_with_handoffs(user_ids: list[str]) -> dict[str, list[Task]]:
    """複数ユーザーのタスクを一括取得"""
    # N+1問題回避
    query = select(tasks_table).where(tasks_table.c.assignee_user_id.in_(user_ids))
    # ...
```

## Error Handling

### Validation Errors

```python
class TaskValidationError(ValueError):
    """タスクバリデーションエラー"""
    pass

# Use Case
if not dto.title:
    raise TaskValidationError("タスク名は必須です")
```

### User-Friendly Messages

```python
# Slack応答でエラーメッセージを分かりやすく
try:
    task = await use_case.execute(dto)
except TaskValidationError as e:
    return f"❌ {e}\n\n例: タスク登録: API統合 期限: 明日15時"
```

## Deployment

### Configuration

```python
# src/infrastructure/config.py

class Settings(BaseSettings):
    # Database
    database_url: str

    # OpenAI
    openai_api_key: str

    # Task Management
    task_max_title_length: int = 200
    task_context_limit: int = 10  # システムプロンプトに注入するタスク数上限

    class Config:
        env_file = ".env"
```

### Monitoring

```python
logger.info("Task created", extra={
    "task_id": str(task.id),
    "assignee": task.assignee_user_id,
    "due_at": task.due_at.isoformat() if task.due_at else None,
    "duration_ms": duration,
})
```
