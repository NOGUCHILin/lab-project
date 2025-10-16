# Phase 2: Plan - Context基盤構築の技術設計

**nakamura-misaki v6.0.0 - Phase 1実装の技術設計**

---

## 🎯 設計の目的

Phase 1: Specify で定義した要件を、**DDD + Clean Architecture**パターンで実装するための技術設計。

### 設計原則

1. **Bounded Context分離** - Personal Tasks Contextとして独立
2. **Clean Architecture 4層構造** - Domain/Application/Adapters/Infrastructure
3. **依存性逆転** - 外側→内側への依存のみ
4. **テスト容易性** - 各層が独立してテスト可能
5. **既存機能維持** - v5.1.0と完全互換

---

## 📐 Architecture Decision Records (ADR)

### ADR-001: Bounded Context分離

**Status**: Accepted

**Context**:
- 既存コードは単一の`src/`に全て配置
- 将来Work Tasks Contextを追加予定
- ドメイン境界を明確にする必要

**Decision**:
- `contexts/personal_tasks/` として分離
- 個人タスク管理に関する全ての責務を含む
- 他Contextへの依存なし

**Consequences**:
- ✅ ドメイン境界が明確
- ✅ 将来の拡張が容易
- ⚠️ ディレクトリ構造が深くなる

---

### ADR-002: Clean Architecture 4層構造

**Status**: Accepted

**Context**:
- テスト容易性が必要
- ビジネスロジックの独立性が必要
- 外部依存（DB, API）の交換可能性が必要

**Decision**:
以下の4層構造を採用：

```
1. Domain層（ビジネスルール）
   - 誰にも依存しない
   - Pure Python（外部ライブラリ最小限）

2. Application層（ユースケース）
   - Domainに依存
   - Use CaseとDTOを配置

3. Adapters層（インターフェース）
   - Applicationに依存
   - Primary（入力）: Slack, REST API, Tools
   - Secondary（出力）: Repository実装

4. Infrastructure層（技術詳細）
   - 全層に依存可能
   - DB接続、DIコンテナ、設定
```

**Consequences**:
- ✅ テストが書きやすい
- ✅ 外部依存の交換が容易
- ⚠️ ボイラープレート増加

---

### ADR-003: Shared Kernel抽出

**Status**: Accepted

**Context**:
- Personal TasksとWork Tasksで共通の概念がある
- 重複コードを避けたい
- 過度な共有は避けたい

**Decision**:
以下のみをShared Kernelに配置：
- Value Objects: `UserId`, `TaskStatus`
- Infrastructure: `ClaudeClient`, `SlackClient`

**Consequences**:
- ✅ 重複コード削減
- ✅ 共通概念の一貫性
- ⚠️ Shared Kernelへの変更は両Contextに影響

---

### ADR-004: リポジトリパターン採用

**Status**: Accepted

**Context**:
- Domain層をインフラから独立させたい
- テストでモックを使いたい
- 将来DBを変更する可能性

**Decision**:
- Domain層にRepositoryインターフェース定義
- Adapters層（Secondary）に実装
- DIコンテナで注入

**Consequences**:
- ✅ Domain層の独立性
- ✅ テストでモック可能
- ⚠️ インターフェースと実装の2ファイル必要

---

## 🏗️ システムアーキテクチャ

### 全体構成図

```
┌─────────────────────────────────────────────────────┐
│                   nakamura-misaki                    │
│                                                      │
│  ┌────────────────────────────────────────────┐   │
│  │         contexts/personal_tasks/            │   │
│  │                                              │   │
│  │  ┌────────────────────────────────────┐   │   │
│  │  │  Domain層（ビジネスルール）         │   │   │
│  │  │  - Task（集約ルート）               │   │   │
│  │  │  - Conversation                     │   │   │
│  │  │  - Repository Interface             │   │   │
│  │  └────────────────────────────────────┘   │   │
│  │              ↑                              │   │
│  │  ┌────────────────────────────────────┐   │   │
│  │  │  Application層（ユースケース）      │   │   │
│  │  │  - RegisterTaskUseCase              │   │   │
│  │  │  - CompleteTaskUseCase              │   │   │
│  │  │  - UpdateTaskUseCase                │   │   │
│  │  │  - QueryUserTasksUseCase            │   │   │
│  │  └────────────────────────────────────┘   │   │
│  │              ↑                              │   │
│  │  ┌────────────────────────────────────┐   │   │
│  │  │  Adapters層（インターフェース）     │   │   │
│  │  │                                      │   │   │
│  │  │  Primary（入力）:                   │   │   │
│  │  │  - SlackEventHandler                │   │   │
│  │  │  - TaskTools（Claude用）            │   │   │
│  │  │  - REST API Routes                  │   │   │
│  │  │                                      │   │   │
│  │  │  Secondary（出力）:                 │   │   │
│  │  │  - PostgreSQLTaskRepository         │   │   │
│  │  │  - PostgreSQLConversationRepository │   │   │
│  │  └────────────────────────────────────┘   │   │
│  │              ↑                              │   │
│  │  ┌────────────────────────────────────┐   │   │
│  │  │  Infrastructure層（技術詳細）       │   │   │
│  │  │  - DIContainer                      │   │   │
│  │  │  - Database接続                     │   │   │
│  │  │  - Config                           │   │   │
│  │  └────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────┘   │
│                                                      │
│  ┌────────────────────────────────────────────┐   │
│  │         shared_kernel/                      │   │
│  │  - Value Objects（UserId, TaskStatus）     │   │
│  │  - ClaudeClient, SlackClient                │   │
│  └────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

外部システム:
- PostgreSQL Database
- Claude API
- Slack API
```

---

## 📊 データモデル設計

### Domain Model: Task

```python
# contexts/personal_tasks/domain/models/task.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Task:
    """個人タスク（集約ルート）

    不変条件:
    - idは一意
    - titleは空文字列不可
    - statusはTaskStatusのいずれか
    - completed_atはstatus=COMPLETEDの場合のみ存在
    """
    id: UUID
    title: str
    description: str | None
    assignee_user_id: str  # Slack User ID
    creator_user_id: str
    status: TaskStatus
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        title: str,
        assignee_user_id: str,
        creator_user_id: str,
        description: str | None = None,
        due_at: datetime | None = None
    ) -> "Task":
        """ファクトリメソッド：新しいタスクを作成

        Args:
            title: タスクタイトル（必須）
            assignee_user_id: 担当者のSlack User ID
            creator_user_id: 作成者のSlack User ID
            description: 説明（オプション）
            due_at: 期限（オプション）

        Returns:
            新しいTaskインスタンス

        Raises:
            ValueError: titleが空の場合
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        from uuid import uuid4
        from datetime import datetime, UTC

        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            title=title.strip(),
            description=description,
            assignee_user_id=assignee_user_id,
            creator_user_id=creator_user_id,
            status=TaskStatus.PENDING,
            due_at=due_at,
            completed_at=None,
            created_at=now,
            updated_at=now
        )

    def complete(self) -> None:
        """タスクを完了する

        不変条件:
        - 完了済みタスクは再完了不可

        Raises:
            ValueError: 既に完了済みの場合
        """
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Task is already completed")

        from datetime import datetime, UTC
        now = datetime.now(UTC)

        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now

    def reassign(self, new_assignee_user_id: str) -> None:
        """担当者を変更する

        Args:
            new_assignee_user_id: 新しい担当者のSlack User ID

        Raises:
            ValueError: new_assignee_user_idが空の場合
        """
        if not new_assignee_user_id:
            raise ValueError("Assignee user ID cannot be empty")

        from datetime import datetime, UTC

        self.assignee_user_id = new_assignee_user_id
        self.updated_at = datetime.now(UTC)

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        due_at: datetime | None = None
    ) -> None:
        """タスク情報を更新する

        Args:
            title: 新しいタイトル（オプション）
            description: 新しい説明（オプション）
            due_at: 新しい期限（オプション）

        Raises:
            ValueError: titleが空の場合
        """
        from datetime import datetime, UTC

        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            self.title = title.strip()

        if description is not None:
            self.description = description

        if due_at is not None:
            self.due_at = due_at

        self.updated_at = datetime.now(UTC)
```

### Domain Model: Conversation

```python
# contexts/personal_tasks/domain/models/conversation.py

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Message:
    """会話メッセージ（値オブジェクト）"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


@dataclass
class Conversation:
    """会話履歴（集約ルート）

    不変条件:
    - channel_idとuser_idの組み合わせは一意
    - messagesは時系列順
    """
    id: UUID
    channel_id: str  # Slack Channel ID
    user_id: str  # Slack User ID
    messages: list[Message] = field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    def add_message(self, role: str, content: str) -> None:
        """メッセージを追加

        Args:
            role: "user" or "assistant"
            content: メッセージ内容

        Raises:
            ValueError: roleが不正な場合
        """
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role: {role}")

        from datetime import datetime, UTC

        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(UTC)
        )
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)
```

---

### Repository Interface

```python
# contexts/personal_tasks/domain/repositories/task_repository.py

from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime

from ..models.task import Task


class TaskRepository(ABC):
    """タスクリポジトリインターフェース（Domain層）"""

    @abstractmethod
    async def save(self, task: Task) -> Task:
        """タスクを保存

        Args:
            task: 保存するタスク

        Returns:
            保存されたタスク（IDが付与される）
        """
        pass

    @abstractmethod
    async def find_by_id(self, task_id: UUID) -> Task | None:
        """IDでタスクを検索

        Args:
            task_id: タスクID

        Returns:
            見つかったタスク、存在しない場合はNone
        """
        pass

    @abstractmethod
    async def find_by_assignee(
        self,
        assignee_user_id: str,
        include_completed: bool = False
    ) -> list[Task]:
        """担当者でタスクを検索

        Args:
            assignee_user_id: 担当者のSlack User ID
            include_completed: 完了済みタスクを含めるか

        Returns:
            タスクのリスト（due_at昇順）
        """
        pass

    @abstractmethod
    async def find_today_tasks(
        self,
        assignee_user_id: str
    ) -> list[Task]:
        """今日期限のタスクを検索

        Args:
            assignee_user_id: 担当者のSlack User ID

        Returns:
            今日期限のタスクのリスト
        """
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """タスクを削除

        Args:
            task_id: 削除するタスクのID

        Returns:
            削除成功した場合True
        """
        pass
```

---

### Database Schema (PostgreSQL)

```sql
-- 既存のスキーマを維持（v5.1.0互換）

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assignee_user_id VARCHAR(50) NOT NULL,
    creator_user_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed')),
    due_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_assignee ON tasks(assignee_user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_at ON tasks(due_at);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    channel_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(channel_id, user_id)
);

CREATE INDEX idx_conversations_channel_user ON conversations(channel_id, user_id);
```

**Note**: Phase 1ではスキーマ変更なし。Alembicマイグレーションも不要。

---

## 🔌 API設計

### REST API (FastAPI)

#### Endpoint: Slack Events

```python
# contexts/personal_tasks/adapters/primary/api/routes/slack.py

POST /api/v1/slack/events

Request:
{
  "type": "event_callback",
  "event": {
    "type": "message",
    "channel": "C12345",
    "user": "U12345",
    "text": "明日までにレポート書く"
  }
}

Response:
200 OK
```

**処理フロー**:
1. Slack署名検証
2. イベント重複チェック
3. SlackEventHandler呼び出し
4. 非同期処理（バックグラウンド）

---

### Claude Tool API

```python
# contexts/personal_tasks/adapters/primary/tools/task_tools.py

# Tool 1: create_task
{
  "name": "create_task",
  "description": "新しいタスクを登録する",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string", "description": "タスクタイトル"},
      "description": {"type": "string", "description": "タスク説明（任意）"},
      "due_at": {"type": "string", "description": "期限（ISO 8601形式、任意）"}
    },
    "required": ["title"]
  }
}

# Tool 2: complete_task
{
  "name": "complete_task",
  "description": "タスクを完了状態にする",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string", "description": "タスクID（UUID）"}
    },
    "required": ["task_id"]
  }
}

# Tool 3: list_tasks
{
  "name": "list_tasks",
  "description": "ユーザーのタスク一覧を取得",
  "input_schema": {
    "type": "object",
    "properties": {
      "include_completed": {"type": "boolean", "description": "完了済みタスクを含めるか"}
    }
  }
}

# Tool 4: update_task
{
  "name": "update_task",
  "description": "タスク情報を更新",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {"type": "string", "description": "タスクID（UUID）"},
      "title": {"type": "string", "description": "新しいタイトル（任意）"},
      "description": {"type": "string", "description": "新しい説明（任意）"},
      "due_at": {"type": "string", "description": "新しい期限（任意）"},
      "assignee_user_id": {"type": "string", "description": "新しい担当者（任意）"}
    },
    "required": ["task_id"]
  }
}
```

---

## 🔄 Use Case設計

### RegisterTaskUseCase

```python
# contexts/personal_tasks/application/use_cases/register_task.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.models.task import Task
from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import RegisterTaskDTO, TaskDTO


class RegisterTaskUseCase:
    """タスク登録ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, dto: RegisterTaskDTO) -> TaskDTO:
        """タスクを登録する

        Args:
            dto: タスク登録情報

        Returns:
            登録されたタスク情報

        Raises:
            ValueError: バリデーションエラー
        """
        # Domain Modelを作成
        task = Task.create(
            title=dto.title,
            assignee_user_id=dto.assignee_user_id,
            creator_user_id=dto.creator_user_id,
            description=dto.description,
            due_at=dto.due_at
        )

        # 永続化
        saved_task = await self._task_repository.save(task)

        # DTOに変換して返却
        return TaskDTO.from_domain(saved_task)
```

### CompleteTaskUseCase

```python
# contexts/personal_tasks/application/use_cases/complete_task.py

from uuid import UUID

from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import CompleteTaskDTO, TaskDTO


class CompleteTaskUseCase:
    """タスク完了ユースケース"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self, dto: CompleteTaskDTO) -> TaskDTO:
        """タスクを完了する

        Args:
            dto: タスク完了情報

        Returns:
            完了したタスク情報

        Raises:
            ValueError: タスクが存在しない、または既に完了済み
        """
        # タスクを取得
        task = await self._task_repository.find_by_id(dto.task_id)
        if task is None:
            raise ValueError(f"Task not found: {dto.task_id}")

        # Domain Modelで完了処理
        task.complete()

        # 永続化
        saved_task = await self._task_repository.save(task)

        # DTOに変換して返却
        return TaskDTO.from_domain(saved_task)
```

---

## 🎨 DTO設計

```python
# contexts/personal_tasks/application/dto/task_dto.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.models.task import Task, TaskStatus


@dataclass
class RegisterTaskDTO:
    """タスク登録DTO"""
    title: str
    assignee_user_id: str
    creator_user_id: str
    description: str | None = None
    due_at: datetime | None = None


@dataclass
class CompleteTaskDTO:
    """タスク完了DTO"""
    task_id: UUID


@dataclass
class UpdateTaskDTO:
    """タスク更新DTO"""
    task_id: UUID
    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None
    assignee_user_id: str | None = None


@dataclass
class TaskDTO:
    """タスク情報DTO（レスポンス用）"""
    id: UUID
    title: str
    description: str | None
    assignee_user_id: str
    creator_user_id: str
    status: str
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task: Task) -> "TaskDTO":
        """Domain ModelからDTOに変換"""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            assignee_user_id=task.assignee_user_id,
            creator_user_id=task.creator_user_id,
            status=task.status.value,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
```

---

## 🔧 Infrastructure設計

### DIContainer

```python
# contexts/personal_tasks/infrastructure/di_container.py

from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.repositories.task_repository import TaskRepository
from ..domain.repositories.conversation_repository import ConversationRepository
from ..adapters.secondary.postgresql_task_repository import PostgreSQLTaskRepository
from ..adapters.secondary.postgresql_conversation_repository import PostgreSQLConversationRepository
from ..application.use_cases.register_task import RegisterTaskUseCase
from ..application.use_cases.complete_task import CompleteTaskUseCase
from ..application.use_cases.update_task import UpdateTaskUseCase
from ..application.use_cases.query_user_tasks import QueryUserTasksUseCase


class PersonalTasksDIContainer:
    """Personal Tasks Context専用のDIコンテナ"""

    def __init__(
        self,
        db_session: AsyncSession,
        claude_client,  # shared_kernel.infrastructure.ClaudeClient
        slack_client    # shared_kernel.infrastructure.SlackClient
    ):
        self._session = db_session
        self._claude = claude_client
        self._slack = slack_client

        # Repository（遅延初期化）
        self._task_repository: TaskRepository | None = None
        self._conversation_repository: ConversationRepository | None = None

    @property
    def task_repository(self) -> TaskRepository:
        """TaskRepositoryを取得（シングルトン）"""
        if self._task_repository is None:
            self._task_repository = PostgreSQLTaskRepository(self._session)
        return self._task_repository

    @property
    def conversation_repository(self) -> ConversationRepository:
        """ConversationRepositoryを取得（シングルトン）"""
        if self._conversation_repository is None:
            self._conversation_repository = PostgreSQLConversationRepository(
                self._session
            )
        return self._conversation_repository

    def build_register_task_use_case(self) -> RegisterTaskUseCase:
        """RegisterTaskUseCaseを構築"""
        return RegisterTaskUseCase(task_repository=self.task_repository)

    def build_complete_task_use_case(self) -> CompleteTaskUseCase:
        """CompleteTaskUseCaseを構築"""
        return CompleteTaskUseCase(task_repository=self.task_repository)

    def build_update_task_use_case(self) -> UpdateTaskUseCase:
        """UpdateTaskUseCaseを構築"""
        return UpdateTaskUseCase(task_repository=self.task_repository)

    def build_query_user_tasks_use_case(self) -> QueryUserTasksUseCase:
        """QueryUserTasksUseCaseを構築"""
        return QueryUserTasksUseCase(task_repository=self.task_repository)
```

---

## 📦 Shared Kernel設計

### Value Objects

```python
# shared_kernel/domain/value_objects/user_id.py

from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """ユーザーID（値オブジェクト）

    Slack User IDを表現
    """
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("UserId cannot be empty")
        if not self.value.startswith("U"):
            raise ValueError("Slack User ID must start with 'U'")


# shared_kernel/domain/value_objects/task_status.py

from enum import Enum


class TaskStatus(Enum):
    """タスクステータス（値オブジェクト）

    両Context（Personal/Work）で共通
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

### Infrastructure

```python
# shared_kernel/infrastructure/claude_client.py

from anthropic import AsyncAnthropic


class ClaudeClient:
    """Claude API呼び出しクライアント（両Contextで共有）"""

    def __init__(self, api_key: str):
        self._client = AsyncAnthropic(api_key=api_key)

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict],
        conversation_history: list[dict] | None = None
    ) -> dict:
        """Claude APIでチャット

        Args:
            system_prompt: システムプロンプト
            user_message: ユーザーメッセージ
            tools: Tool定義リスト
            conversation_history: 会話履歴（オプション）

        Returns:
            Claude APIレスポンス
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        response = await self._client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=messages,
            tools=tools,
            max_tokens=4096
        )

        return {
            "content": response.content,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
```

---

## 🧪 テスト戦略

### Unit Test（Domain層）

```python
# tests/unit/personal_tasks/domain/models/test_task.py

import pytest
from datetime import datetime, UTC
from uuid import uuid4

from contexts.personal_tasks.domain.models.task import Task, TaskStatus


class TestTaskCreation:
    """Task作成のテスト"""

    def test_create_task_with_minimum_fields(self):
        """最小限のフィールドでタスク作成"""
        # When
        task = Task.create(
            title="レポート作成",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        # Then
        assert task.id is not None
        assert task.title == "レポート作成"
        assert task.status == TaskStatus.PENDING
        assert task.completed_at is None

    def test_create_task_with_empty_title_raises_error(self):
        """空のタイトルでエラー"""
        # When & Then
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task.create(
                title="",
                assignee_user_id="U12345",
                creator_user_id="U12345"
            )


class TestTaskCompletion:
    """Task完了のテスト"""

    def test_complete_task_changes_status(self):
        """完了でステータス変更"""
        # Given
        task = Task.create(
            title="テスト",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        # When
        task.complete()

        # Then
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    def test_complete_already_completed_task_raises_error(self):
        """完了済みタスクの再完了はエラー"""
        # Given
        task = Task.create(
            title="テスト",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )
        task.complete()

        # When & Then
        with pytest.raises(ValueError, match="already completed"):
            task.complete()
```

### Integration Test（Repository）

```python
# tests/integration/personal_tasks/adapters/secondary/test_postgresql_task_repository.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from contexts.personal_tasks.domain.models.task import Task
from contexts.personal_tasks.adapters.secondary.postgresql_task_repository import (
    PostgreSQLTaskRepository
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_save_and_find_task(db_session: AsyncSession):
    """タスクの保存と取得"""
    # Given
    repo = PostgreSQLTaskRepository(db_session)
    task = Task.create(
        title="統合テスト用タスク",
        assignee_user_id="U12345",
        creator_user_id="U12345"
    )

    # When
    saved = await repo.save(task)
    await db_session.commit()

    found = await repo.find_by_id(saved.id)

    # Then
    assert found is not None
    assert found.title == "統合テスト用タスク"
    assert found.id == saved.id
```

---

## 📁 完全なディレクトリ構造

```
nakamura-misaki/
├── pyproject.toml
├── alembic/
│   ├── versions/
│   └── env.py
│
├── src/
│   ├── contexts/
│   │   └── personal_tasks/
│   │       ├── __init__.py
│   │       │
│   │       ├── domain/
│   │       │   ├── __init__.py
│   │       │   ├── models/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── task.py
│   │       │   │   └── conversation.py
│   │       │   ├── repositories/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── task_repository.py
│   │       │   │   └── conversation_repository.py
│   │       │   └── services/
│   │       │       ├── __init__.py
│   │       │       └── claude_agent_service.py
│   │       │
│   │       ├── application/
│   │       │   ├── __init__.py
│   │       │   ├── use_cases/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── register_task.py
│   │       │   │   ├── complete_task.py
│   │       │   │   ├── update_task.py
│   │       │   │   └── query_user_tasks.py
│   │       │   └── dto/
│   │       │       ├── __init__.py
│   │       │       └── task_dto.py
│   │       │
│   │       ├── adapters/
│   │       │   ├── __init__.py
│   │       │   ├── primary/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── api/
│   │       │   │   │   ├── __init__.py
│   │       │   │   │   ├── app.py
│   │       │   │   │   └── routes/
│   │       │   │   │       ├── __init__.py
│   │       │   │   │       └── slack.py
│   │       │   │   ├── slack_event_handler.py
│   │       │   │   └── tools/
│   │       │   │       ├── __init__.py
│   │       │   │       ├── base_tool.py
│   │       │   │       └── task_tools.py
│   │       │   └── secondary/
│   │       │       ├── __init__.py
│   │       │       ├── postgresql_task_repository.py
│   │       │       └── postgresql_conversation_repository.py
│   │       │
│   │       └── infrastructure/
│   │           ├── __init__.py
│   │           ├── di_container.py
│   │           ├── database.py
│   │           └── config.py
│   │
│   ├── shared_kernel/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   └── value_objects/
│   │   │       ├── __init__.py
│   │   │       ├── user_id.py
│   │   │       └── task_status.py
│   │   └── infrastructure/
│   │       ├── __init__.py
│   │       ├── claude_client.py
│   │       └── slack_client.py
│   │
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── personal_tasks/
│   │   │   ├── domain/
│   │   │   │   ├── models/
│   │   │   │   │   ├── test_task.py
│   │   │   │   │   └── test_conversation.py
│   │   │   │   └── services/
│   │   │   └── application/
│   │   │       └── use_cases/
│   │   │           ├── test_register_task.py
│   │   │           ├── test_complete_task.py
│   │   │           ├── test_update_task.py
│   │   │           └── test_query_user_tasks.py
│   │   └── shared_kernel/
│   │       └── domain/
│   │           └── test_value_objects.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   └── personal_tasks/
│   │       └── adapters/
│   │           └── secondary/
│   │               ├── test_postgresql_task_repository.py
│   │               └── test_postgresql_conversation_repository.py
│   │
│   └── e2e/
│       ├── __init__.py
│       └── test_slack_bot_flow.py
│
├── specs/
│   ├── PHASE1_SPECIFY.md
│   └── PHASE1_PLAN.md  # このファイル
│
└── claudedocs/
    ├── DEVELOPMENT_PHILOSOPHY.md
    ├── INTEGRATION_PLAN.md
    └── V5_MIGRATION_SUMMARY.md
```

---

## 🚀 Implementation Roadmap

Phase 1実装の推奨順序：

### Step 1: 基盤準備（1時間）
1. ディレクトリ構造作成
2. `__init__.py` 作成
3. 基本設定ファイル配置

### Step 2: Domain層（3時間）
1. Task モデル実装 + Unit Test
2. Conversation モデル実装 + Unit Test
3. Repository インターフェース定義

### Step 3: Shared Kernel（1時間）
1. Value Objects実装 + Unit Test
2. ClaudeClient, SlackClient移動

### Step 4: Application層（3時間）
1. DTO定義
2. Use Case実装 + Unit Test（モック使用）

### Step 5: Adapters層（4時間）
1. Repository実装 + Integration Test
2. Tools実装
3. SlackEventHandler移動

### Step 6: Infrastructure層（2時間）
1. DIContainer実装
2. Database接続設定
3. Config設定

### Step 7: 統合とテスト（3時間）
1. Import文修正
2. E2Eテスト
3. 本番環境デプロイ

**合計見積もり**: 17時間（約2-3日）

---

## 📝 Implementation Checklist

- [ ] ディレクトリ構造作成完了
- [ ] Domain層実装完了
- [ ] Shared Kernel実装完了
- [ ] Application層実装完了
- [ ] Adapters層実装完了
- [ ] Infrastructure層実装完了
- [ ] 全Unit Testパス
- [ ] 全Integration Testパス
- [ ] E2Eテスト成功
- [ ] トークン消費量確認（1800±100）
- [ ] 本番デプロイ成功

---

**作成日**: 2025-10-16
**作成者**: Claude Code
**レビュー**: 野口凜
**ステータス**: Draft → Review中
