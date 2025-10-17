# 開発思想・方法論

**nakamura-misaki v6.0.0 統合プロジェクトの開発方針**

---

## 🎯 開発方針の2本柱

本プロジェクトは以下の2つの方法論を組み合わせて開発を進めます：

1. **Spec-Driven Development (SDD)** - 仕様駆動開発
2. **Test-Driven Development (TDD)** - テスト駆動開発

**+ Clean Architecture + DDD** による保守性の高いアーキテクチャ

---

## 📖 1. Spec-Driven Development (SDD)

### 定義

**仕様を中心に据えた開発手法** - コードではなく**仕様（Specification）が信頼できる唯一の情報源**となる。

従来の「コードを書いてから仕様を後付け」を逆転し、**仕様を先に書き、それを実行可能な契約として扱う**。

### SDDの起源と背景

- **AWS Kiro IDE (2024-2025)** が採用している手法
- **GitHub Spec Kit** でも推奨されている
- 「Vibe Coding」（思いつきでコードを書く）からの脱却
- AI時代の開発手法として注目されている

**研究結果**: LLMに仕様を与えると、与えない場合の8回の反復と同等の精度を1回で達成できる。

---

## 🏗️ SDDの4つのPhase

### Phase 1: Specify（仕様定義）

**What & Why を記述** - 技術詳細には触れない

#### 含まれるもの
- ユーザーストーリー
- 受け入れ基準（Acceptance Criteria）
- 機能の目的・背景

#### 実践例

```markdown
# Feature: タスク完了機能

## User Story
ユーザーとして、タスクを完了状態にマークしたい。
なぜなら、終わったタスクを一覧から区別したいから。

## Acceptance Criteria
- [ ] タスク一覧で「完了」ボタンをクリックできる
- [ ] 完了したタスクはステータスが"completed"になる
- [ ] 完了済みタスクは再度完了できない（エラー表示）
- [ ] 完了時刻が自動記録される
- [ ] 完了後、担当者にSlack通知が送られる
```

---

### Phase 2: Plan（技術設計）

**How を記述** - アーキテクチャと技術詳細を決定

#### 含まれるもの
- アーキテクチャ決定
- API設計
- データモデル設計
- 技術スタック選定
- クラス・メソッド設計

#### 実践例

```markdown
# Technical Design: タスク完了機能

## Architecture Decision
- Clean Architecture 4層構造を採用
- Domain層にcomplete()メソッドを追加
- Use Case層でSlack通知を処理

## API Design
### Endpoint
PUT /api/v1/tasks/{task_id}/complete

### Request
なし（IDのみ）

### Response
{
  "task_id": "uuid",
  "status": "completed",
  "completed_at": "2025-10-16T10:30:00Z"
}

## Data Model Changes
Task {
  id: UUID
  status: TaskStatus  // PENDING → COMPLETED
  completed_at: datetime | None  // ← 新規追加
  updated_at: datetime
}

## Domain Logic
- Task.complete() メソッド追加
- 完了済みタスクの再完了を防ぐバリデーション
- completed_at, updated_at の自動設定

## Technology Stack
- FastAPI (REST API)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Slack SDK (通知)
```

---

### Phase 3: Tasks（タスク分解）

**実装可能な小単位に分解** - 各タスクはテスト可能で独立している

#### 含まれるもの
- 小さく分割された実装タスク
- 各タスクのDefinition of Done
- タスク間の依存関係
- 実装順序

#### 実践例

```markdown
# Implementation Tasks: タスク完了機能

## Task 1: Domain層 - Task.complete()メソッド実装
**Definition of Done:**
- [ ] Task.complete()メソッド実装
- [ ] 完了済みタスクの再完了を防ぐバリデーション
- [ ] completed_atタイムスタンプ自動設定
- [ ] Unit Test作成（3テストケース以上）
- [ ] テストパス

**依存**: なし

## Task 2: Alembicマイグレーション - completed_atカラム追加
**Definition of Done:**
- [ ] マイグレーションファイル作成
- [ ] upgrade/downgrade動作確認
- [ ] 既存データの互換性確認

**依存**: Task 1（モデル定義確定後）

## Task 3: Use Case層 - CompleteTaskUseCase実装
**Definition of Done:**
- [ ] CompleteTaskUseCase作成
- [ ] DTOパラメータ定義（CompleteTaskDTO）
- [ ] リポジトリ経由でタスク取得・保存
- [ ] Unit Test作成（モック使用）
- [ ] テストパス

**依存**: Task 1

## Task 4: Adapters層 - REST APIエンドポイント実装
**Definition of Done:**
- [ ] PUT /api/v1/tasks/{id}/complete エンドポイント実装
- [ ] リクエスト/レスポンススキーマ定義
- [ ] Use Case呼び出し
- [ ] Integration Test作成（実DB使用）
- [ ] テストパス

**依存**: Task 2, Task 3

## Task 5: Slack通知機能実装
**Definition of Done:**
- [ ] Use Case内でSlackClient呼び出し
- [ ] 通知メッセージフォーマット定義
- [ ] エラーハンドリング
- [ ] Unit Test作成（Slack APIモック）
- [ ] テストパス

**依存**: Task 3

## Task 6: E2Eテスト
**Definition of Done:**
- [ ] Slack Bot経由でタスク完了のE2Eテスト作成
- [ ] テストパス

**依存**: Task 4, Task 5
```

---

### Phase 4: Implementation（実装）

**TDDサイクルで各Taskを実装** - Red → Green → Refactor

#### Task単位の開発サイクル

```
1. 🔴 Red: Test作成（失敗確認）
   ↓
2. 🟢 Green: 最小実装（テストを通す）
   ↓
3. 🔵 Refactor: リファクタリング
   ↓
4. Commit（pre-commit自動テスト）
   ↓
5. 次のTaskへ
```

#### 実践例：Task 1の実装

##### Step 1: 🔴 Red - Test作成

```python
# tests/unit/domain/models/test_task.py

import pytest
from datetime import datetime, UTC
from contexts.personal_tasks.domain.models.task import Task, TaskStatus


class TestTaskCompletion:
    """Task.complete()のテスト"""

    def test_complete_task_changes_status_to_completed(self):
        """タスク完了でステータスがCOMPLETEDになる"""
        # Given: Pending状態のタスク
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        assert task.status == TaskStatus.PENDING
        assert task.completed_at is None

        # When: 完了する
        task.complete()

        # Then: ステータスがCOMPLETEDになる
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    def test_complete_already_completed_task_raises_error(self):
        """完了済みタスクの再完了はエラー"""
        # Given: 完了済みタスク
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        task.complete()

        # When & Then: 再度完了しようとするとエラー
        with pytest.raises(ValueError, match="Already completed"):
            task.complete()

    def test_complete_updates_timestamp(self):
        """完了時にタイムスタンプが更新される"""
        # Given: タスク作成
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        original_updated_at = task.updated_at

        # When: 完了する
        import time
        time.sleep(0.01)
        task.complete()

        # Then: updated_atが更新される
        assert task.updated_at > original_updated_at
```

**この時点でテスト実行 → 失敗する（🔴 Red）**

##### Step 2: 🟢 Green - 最小実装

```python
# contexts/personal_tasks/domain/models/task.py

from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import UUID
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Task:
    id: UUID
    title: str
    assignee_user_id: str
    creator_user_id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    @classmethod
    def create(cls, title: str, assignee_user_id: str, creator_user_id: str):
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            title=title,
            assignee_user_id=assignee_user_id,
            creator_user_id=creator_user_id,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            completed_at=None
        )

    def complete(self) -> None:
        """タスクを完了する"""
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Already completed")

        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
```

**テスト実行 → 成功する（🟢 Green）**

##### Step 3: 🔵 Refactor - リファクタリング

```python
# contexts/personal_tasks/domain/models/task.py

    def complete(self) -> None:
        """タスクを完了する

        Raises:
            ValueError: 既に完了済みの場合
        """
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Already completed")

        self._mark_as_completed()

    def _mark_as_completed(self) -> None:
        """完了状態にマークする（内部メソッド）"""
        now = datetime.now(UTC)
        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now
```

**テスト実行 → 成功を維持（🔵 Refactor完了）**

##### Step 4: Commit

```bash
git add contexts/personal_tasks/domain/models/task.py
git add tests/unit/domain/models/test_task.py

git commit -m "feat(personal-tasks): Add Task.complete() method with TDD

- Add complete() method to Task model
- Add validation for already completed tasks
- Add completed_at timestamp field
- Add comprehensive unit tests (3 test cases)

Tests: All passing (3/3)
Relates-to: #v6-phase1-task1"

# Pre-commit hookが自動実行される
# → Unit tests実行
# → Lint実行
# → 全て成功したらCommit完了
```

---

## 🔴🟢🔵 2. Test-Driven Development (TDD)

### TDDサイクル

```
🔴 Red    → テストを書く（失敗する）
🟢 Green  → 最小限の実装で通す
🔵 Refactor → リファクタリング

↓ 繰り返し
```

### 本プロジェクトでのTDDルール

#### ルール1: テストなしでコードを書かない

**SDDのPhase 4（Implementation）で必ずTDDを使う**

#### ルール2: テストは3段階（Given-When-Then）

```python
def test_example():
    # Given（前提条件）: 初期状態を準備
    task = create_test_task()

    # When（実行）: テスト対象を実行
    result = task.complete()

    # Then（検証）: 期待通りの結果を確認
    assert result.status == TaskStatus.COMPLETED
```

#### ルール3: テストの粒度

| テスト種別 | 目的 | 実行頻度 |
|-----------|------|---------|
| **単体テスト (Unit Test)** | 1つのクラス/関数の動作確認 | コミット前（毎回） |
| **統合テスト (Integration Test)** | 複数コンポーネントの連携確認 | コミット前（毎回） |
| **E2Eテスト (End-to-End Test)** | システム全体の動作確認 | Phase完了時 |

---

## 🏗️ 3. Clean Architecture + DDD

### レイヤー間のテスト戦略

```
Domain層（ユニットテスト）
    ↑
Application層（ユニットテスト + モック）
    ↑
Adapters層（統合テスト）
    ↑
Infrastructure層（統合テスト）
```

#### Domain層のテスト

**Pure Unit Test - 依存なし**

```python
# tests/unit/domain/models/test_task.py

def test_task_complete_changes_status():
    """ドメインロジックのテスト（依存なし）"""
    task = Task(...)
    task.complete()
    assert task.status == TaskStatus.COMPLETED
```

#### Application層のテスト

**Unit Test with Mocks - リポジトリをモック**

```python
# tests/unit/application/use_cases/test_complete_task.py

from unittest.mock import AsyncMock

async def test_complete_task_use_case():
    # Given: モックリポジトリ
    mock_repo = AsyncMock()
    task = create_test_task(status=TaskStatus.PENDING)
    mock_repo.find_by_id.return_value = task

    use_case = CompleteTaskUseCase(task_repository=mock_repo)

    # When: ユースケース実行
    result = await use_case.execute(CompleteTaskDTO(task_id=task.id))

    # Then: タスクが完了
    assert result.status == TaskStatus.COMPLETED
    mock_repo.save.assert_called_once()
```

#### Adapters/Infrastructure層のテスト

**Integration Test - 実際のDBを使う**

```python
# tests/integration/adapters/secondary/test_postgresql_task_repository.py

@pytest.mark.integration
async def test_save_and_find_task(db_session):
    """統合テスト（実DB使用）"""
    repo = TaskRepository(db_session)
    task = Task.create(...)

    # 保存
    saved = await repo.save(task)
    await db_session.commit()

    # 取得
    found = await repo.find_by_id(saved.id)
    assert found.title == task.title
```

---

## 🔄 完全な開発フロー

### Phase単位の進め方

```
Phase 1: Specify（仕様定義）
  → ユーザーストーリー + 受け入れ基準

Phase 2: Plan（技術設計）
  → アーキテクチャ・API・データモデル設計

Phase 3: Tasks（タスク分解）
  → 実装可能な小単位に分解 + Definition of Done

Phase 4: Implementation（各Task）
  ├─ 🔴 Red: Test作成
  ├─ 🟢 Green: 実装
  ├─ 🔵 Refactor: リファクタリング
  └─ Commit（pre-commit自動テスト）
```

### Task単位の開発リズム

```
Specify → Plan → Tasks → Test → Code → Commit
                              ↺ Repeat
```

---

## 🔀 Git戦略

### ブランチ戦略

```
main（本番）
  ↑
  merge（Phase完了時のみ）
  ↑
feature/phase-N（Phase作業ブランチ）
  ↑
  rebase（Task完了ごと）
  ↑
feature/phase-N-task-M（Task作業ブランチ）
```

### Commit戦略

#### Commit頻度
- **Task完了ごとにCommit**（小さく頻繁に）
- 1 Task = 1-3 Commits

#### Commit Message規約

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `test`: テスト追加・修正
- `refactor`: リファクタリング
- `docs`: ドキュメント
- `chore`: ビルド・設定変更

**Scope:**
- `personal-tasks`: Personal Tasks Context
- `work-tasks`: Work Tasks Context
- `shared`: Shared Kernel
- `acl`: Anti-Corruption Layer
- `infra`: Infrastructure

**例:**
```
feat(personal-tasks): Add Task.complete() method with TDD

- Add complete() method to Task model
- Add validation for already completed tasks
- Add completed_at timestamp field
- Add comprehensive unit tests (3 test cases)

Tests: All passing (3/3)
Relates-to: #v6-phase1-task1
```

### Pre-commit Hook設定

```bash
# .git/hooks/pre-commit（自動設定済み）

#!/bin/bash
set -e

echo "🧪 Running tests before commit..."

# 1. Unit Tests（高速）
uv run pytest tests/ -m "not integration" -v

# 2. Linting
uv run ruff check src/
uv run mypy src/

# 3. Integration Tests（変更ファイルに応じて）
if git diff --cached --name-only | grep -q "adapters/secondary"; then
    echo "🔗 Running integration tests..."
    uv run pytest tests/ -m integration -v
fi

echo "✅ All checks passed!"
```

---

## 🚨 方針変更時の対応プロトコル

### 即座に作業停止すべき状況

1. **アーキテクチャ違反を発見**
   - 例: Domain層がInfrastructure層に依存している
   - 例: 新しいレイヤーを追加しようとしている

2. **ビジネスロジックの根本的な変更が必要**
   - 例: TaskStatusの定義を変える必要がある
   - 例: Personal TasksとWork Tasksの境界が曖昧になってきた

3. **実装の複雑度が予想を超える**
   - 例: 1 Taskの実装に3日以上かかりそう
   - 例: Phase 2（Plan）で設計しきれない複雑さ

4. **テストが書けない（設計が悪い可能性）**
   - 例: モックが複雑すぎる
   - 例: 依存関係が循環している

5. **仕様が曖昧・矛盾している**
   - 例: Acceptance Criteriaが実装不可能
   - 例: Technical Designと仕様が矛盾

### 報告フォーマット

```markdown
## 🚨 方針変更の提案

### 状況
- 現在の作業: Phase X Task Y
- 発見した問題: [具体的な問題]

### 問題の詳細
[コード例やログ]

### 提案
- Option 1: [提案1]
- Option 2: [提案2]

### 影響範囲
- 影響するPhase/Task: [リスト]
- 追加で必要な日数: [見積もり]

### 判断を仰ぎたい点
[Yes/No で答えられる質問形式]
```

---

## 📊 品質指標（Definition of Done）

### Task完了の定義

- [ ] Spec（Phase 1）に記載されている
- [ ] Technical Design（Phase 2）に記載されている
- [ ] Task（Phase 3）に分解されている
- [ ] テストが書かれている（TDD 🔴）
- [ ] テストが全て通る（TDD 🟢）
- [ ] リファクタリング済み（TDD 🔵）
- [ ] Lintエラーなし（ruff, mypy）
- [ ] Commitメッセージが規約に従っている
- [ ] Pre-commit hookが成功

### Phase完了の定義

- [ ] Phase 1: Specify完了（仕様文書作成）
- [ ] Phase 2: Plan完了（技術設計文書作成）
- [ ] Phase 3: Tasks完了（タスク分解完了）
- [ ] Phase 4: 全Task実装完了
- [ ] 全テストパス（unit + integration + e2e）
- [ ] 本番環境にデプロイ可能
- [ ] ドキュメント更新完了

---

## 🧪 テスト環境設定

### テストディレクトリ構造

```
tests/
├── unit/                        # 単体テスト（依存なし）
│   ├── domain/
│   │   ├── models/
│   │   └── services/
│   └── application/
│       └── use_cases/
│
├── integration/                 # 統合テスト（DB等使用）
│   ├── adapters/
│   │   ├── primary/
│   │   └── secondary/
│   └── infrastructure/
│
├── e2e/                         # E2Eテスト
│   ├── test_slack_bot_flow.py
│   └── test_work_tasks_cli_flow.py
│
└── conftest.py                  # Pytest設定・Fixture
```

### Pytest設定

```toml
# pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# マーカー定義
markers = [
    "unit: Unit tests (no external dependencies)",
    "integration: Integration tests (use database, etc.)",
    "e2e: End-to-end tests",
    "slow: Tests that take more than 1 second",
]

# 非同期テスト設定
asyncio_mode = "auto"

# カバレッジ設定
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "-v",
]
```

### テスト実行コマンド

```bash
# 1. 全テスト実行
uv run pytest

# 2. 単体テストのみ（高速）
uv run pytest -m unit

# 3. 統合テストのみ
uv run pytest -m integration

# 4. 特定のファイルのみ
uv run pytest tests/unit/domain/models/test_task.py

# 5. カバレッジ付き
uv run pytest --cov=src --cov-report=html

# 6. 失敗したテストのみ再実行
uv run pytest --lf

# 7. 並列実行（高速化）
uv run pytest -n auto
```

---

## 📚 実装例：Phase 1-4の完全フロー

nakamura-misaki v6.0.0の具体例で4つのPhaseを実践。

### Phase 1: Specify（仕様定義）

```markdown
# Feature: Personal TasksとWork Tasksの統合

## User Story
システム管理者として、個人タスク（Personal Tasks）と業務タスク（Work Tasks）を
1つのシステムで管理したい。

なぜなら：
- 両方のタスクを統一されたインターフェース（AI Agent）で操作したい
- 個人タスクを業務タスクに変換する機能が必要
- ドメインの独立性を保ちつつ統合したい

## Acceptance Criteria

### Personal Tasks（個人タスク管理）
- [ ] Slack Bot経由でタスク作成・完了・一覧表示ができる
- [ ] タスクはPostgreSQLに保存される
- [ ] 従来のv5.1.0機能がそのまま動作する

### Work Tasks（業務タスク管理）
- [ ] CLI経由でタスク作成・スタッフ割り当てができる
- [ ] タスクはYAMLファイルに保存される
- [ ] スキルベースの自動割り当てが動作する

### 統合機能
- [ ] Personal TaskをWork Taskに変換できる
- [ ] 2つのタスク種別は互いに独立している（依存しない）
- [ ] AI AgentはContext判定して適切なToolを呼び出す

### 非機能要件
- [ ] トークン消費量はv5.1.0と同等（~1800 tokens）
- [ ] 既存データの移行は不要
- [ ] 本番環境へのデプロイが可能
```

---

### Phase 2: Plan（技術設計）

```markdown
# Technical Design: Personal Tasks + Work Tasks統合

## Architecture Decision

### 1. DDD Bounded Context分離
- **Personal Tasks Context**: 個人タスク管理ドメイン
- **Work Tasks Context**: 業務タスク管理ドメイン
- **Shared Kernel**: 両Contextで共有する最小限の部品
- **Anti-Corruption Layer**: Context間の通訳

### 2. Clean Architecture 4層構造（各Context）
```
Domain層（ビジネスルール）
    ↑
Application層（ユースケース）
    ↑
Adapters層（UI・永続化）
    ↑
Infrastructure層（技術詳細）
```

### 3. 依存性の方向
- Adapters/Infrastructure → Application → Domain
- Domainは誰にも依存しない

---

## Data Models

### Personal Tasks Context

#### Domain Model
```python
@dataclass
class PersonalTask:
    """個人タスク（集約ルート）"""
    id: UUID
    title: str
    assignee_user_id: str  # Slack User ID
    creator_user_id: str
    status: TaskStatus
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

#### Database Schema (PostgreSQL)
```sql
CREATE TABLE personal_tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    assignee_user_id VARCHAR(50) NOT NULL,
    creator_user_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    due_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

---

### Work Tasks Context

#### Domain Model
```python
@dataclass
class WorkTask:
    """業務タスク（集約ルート）"""
    id: str  # "T20251016-001"
    type: TaskType  # 査定 | 検品 | 出品 | 修理
    description: str
    assigned_to: str | None  # スタッフ名
    status: TaskStatus
    priority: Priority
    estimated_minutes: int
    actual_minutes: int | None
    created_at: datetime

@dataclass
class Staff:
    """スタッフ（エンティティ）"""
    name: str
    employee_id: str
    skills: dict[TaskType, Skill]
    constraints: StaffConstraints
```

#### File Storage (YAML)
```yaml
# data/tasks/active/2025-10-16.yaml
metadata:
  date: "2025-10-16"
  generated_at: "2025-10-16T08:30:00+09:00"

tasks:
  - id: "T20251016-001"
    type: 査定
    description: "iPhone 14 Pro 256GB"
    assigned_to: 細谷
    status: pending
    priority: high
    estimated_minutes: 15
```

---

### Shared Kernel

#### Value Objects
```python
# shared_kernel/domain/value_objects/task_status.py
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

#### Infrastructure
```python
# shared_kernel/infrastructure/claude_client.py
class ClaudeClient:
    """Claude API呼び出しクライアント（両Contextで共有）"""
    async def chat(self, system_prompt, user_message, tools):
        # ...
```

---

## API Design

### Personal Tasks API (REST)

#### Endpoint: タスク完了
```
PUT /api/v1/tasks/{task_id}/complete

Request: なし（IDのみ）

Response:
{
  "task_id": "uuid",
  "status": "completed",
  "completed_at": "2025-10-16T10:30:00Z"
}
```

### Work Tasks API (CLI)

#### Command: タスク追加
```bash
uv run python scripts/add_task.py \
  --type 査定 \
  --description "iPhone 14" \
  --assign 細谷
```

---

## Technology Stack

| 層 | Personal Tasks | Work Tasks | Shared |
|----|---------------|-----------|--------|
| **Domain** | Python dataclass | Python dataclass | Enum |
| **Application** | DTO, Use Cases | DTO, Use Cases | - |
| **Adapters** | FastAPI, Slack SDK | CLI Scripts | Claude SDK |
| **Infrastructure** | SQLAlchemy, AsyncPG | PyYAML, Pydantic | PostgreSQL |

---

## ディレクトリ構造

```
nakamura-misaki/
├── src/
│   ├── shared_kernel/
│   │   ├── domain/
│   │   │   └── value_objects/
│   │   └── infrastructure/
│   │       ├── claude_client.py
│   │       └── slack_client.py
│   │
│   ├── contexts/
│   │   ├── personal_tasks/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── adapters/
│   │   │   └── infrastructure/
│   │   │
│   │   └── work_tasks/
│   │       ├── domain/
│   │       ├── application/
│   │       ├── adapters/
│   │       └── infrastructure/
│   │
│   └── anti_corruption_layer/
│       ├── personal_to_work_adapter.py
│       └── work_to_personal_adapter.py
│
├── data/  # Work Tasks用YAMLデータ
│   ├── config/
│   └── tasks/
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```
```

---

### Phase 3: Tasks（タスク分解）

```markdown
# Implementation Tasks: Phase 1 - Context基盤構築

## Step 1.1: Personal Tasks Context移行

### Task 1.1.1: ディレクトリ構造作成
**Definition of Done:**
- [ ] `contexts/personal_tasks/` 配下の全ディレクトリ作成
- [ ] `tests/unit/`, `tests/integration/`, `tests/e2e/` 作成
- [ ] ディレクトリ構造確認スクリプト実行成功

**依存**: なし
**見積もり**: 30分

---

### Task 1.1.2: Domain層 - Taskモデル移動 + TDD
**Definition of Done:**
- [ ] `tests/unit/domain/models/test_task.py` 作成（6テストケース）
- [ ] `contexts/personal_tasks/domain/models/task.py` 実装
- [ ] Task.create(), complete(), reassign() メソッド動作
- [ ] 全Unit Testパス
- [ ] Commit完了

**依存**: Task 1.1.1
**見積もり**: 2時間

**テストケース**:
1. test_create_task_with_minimum_fields
2. test_create_task_with_all_fields
3. test_complete_task_changes_status
4. test_complete_already_completed_task_raises_error
5. test_reassign_task_changes_assignee
6. test_reassign_updates_timestamp

---

### Task 1.1.3: Domain層 - Conversationモデル移動 + TDD
**Definition of Done:**
- [ ] `tests/unit/domain/models/test_conversation.py` 作成
- [ ] `contexts/personal_tasks/domain/models/conversation.py` 実装
- [ ] 全Unit Testパス
- [ ] Commit完了

**依存**: Task 1.1.1
**見積もり**: 1時間

---

### Task 1.1.4: Application層 - Use Cases移動 + TDD
**Definition of Done:**
- [ ] 各Use Caseごとにテスト作成（モック使用）
- [ ] 5つのUse Caseファイル移動
  - RegisterTaskUseCase
  - CompleteTaskUseCase
  - UpdateTaskUseCase
  - QueryUserTasksUseCase
  - QueryTodayTasksUseCase (削除予定だが一旦移動)
- [ ] 全Unit Testパス（モックリポジトリ使用）
- [ ] Commit（Use Case単位）

**依存**: Task 1.1.2
**見積もり**: 4時間（Use Case×5）

---

### Task 1.1.5: Adapters層 - Repository実装移動 + Integration Test
**Definition of Done:**
- [ ] `tests/integration/adapters/secondary/test_postgresql_task_repository.py` 作成
- [ ] `contexts/personal_tasks/adapters/secondary/postgresql_task_repository.py` 移動
- [ ] 実DB使用のIntegration Testパス
- [ ] Commit完了

**依存**: Task 1.1.2
**見積もり**: 2時間

---

### Task 1.1.6: Infrastructure層 - DIContainer分離 + テスト
**Definition of Done:**
- [ ] `PersonalTasksDIContainer` 作成
- [ ] 既存DIContainerから分離
- [ ] Container動作確認テスト作成
- [ ] Commit完了

**依存**: Task 1.1.4, Task 1.1.5
**見積もり**: 2時間

---

### Task 1.1.7: Import文修正 + 動作確認
**Definition of Done:**
- [ ] 全Import文を新構造に修正
- [ ] 全テストパス（unit + integration）
- [ ] 本番環境デプロイ
- [ ] Slack Botの動作確認（実際にメッセージ送信）
- [ ] Commit完了

**依存**: Task 1.1.6
**見積もり**: 3時間

**Step 1.1合計見積もり**: 14.5時間（約2日）

---

## Step 1.2: Shared Kernel抽出

### Task 1.2.1: Value Objects抽出 + TDD
**Definition of Done:**
- [ ] `tests/unit/shared_kernel/domain/test_value_objects.py` 作成
- [ ] UserId, TaskStatus実装
- [ ] 全Unit Testパス
- [ ] Personal Tasks Contextから参照するよう修正
- [ ] Commit完了

**依存**: Task 1.1.7
**見積もり**: 1.5時間

---

### Task 1.2.2: Infrastructure抽出 + TDD
**Definition of Done:**
- [ ] ClaudeClient, SlackClient テスト作成
- [ ] `shared_kernel/infrastructure/` に移動
- [ ] 全テストパス
- [ ] Personal Tasks Contextから参照するよう修正
- [ ] Commit完了

**依存**: Task 1.2.1
**見積もり**: 2時間

---

### Task 1.2.3: 本番デプロイ + 動作確認
**Definition of Done:**
- [ ] 全テストパス（unit + integration）
- [ ] 本番環境デプロイ
- [ ] トークン消費量確認（~1800 tokensを維持）
- [ ] Slack Botの全機能動作確認

**依存**: Task 1.2.2
**見積もり**: 1時間

**Step 1.2合計見積もり**: 4.5時間（約0.5日）

---

**Phase 1合計見積もり**: 19時間（約2.5日）
```

---

### Phase 4: Implementation（TDDで実装）

**Task 1.1.2の実装例**は前述の「Phase 4: Implementation」セクションを参照。

---

## 🎓 まとめ

### 開発の流れ

```
Phase 1: Specify（仕様定義）
  ↓
Phase 2: Plan（技術設計）
  ↓
Phase 3: Tasks（タスク分解）
  ↓
Phase 4: Implementation（各Task）
  ├─ 🔴 Red: Test作成
  ├─ 🟢 Green: 実装
  ├─ 🔵 Refactor: リファクタリング
  └─ Commit
```

### 方針変更時は即座に報告

- アーキテクチャ違反
- ビジネスロジック変更
- 実装の複雑度超過
- テストが書けない
- 仕様が曖昧

→ **作業停止 → 報告 → 判断を仰ぐ**

---

## 📚 参考資料

### Spec-Driven Development
- AWS Kiro IDE (2024-2025)
- GitHub Spec Kit
- TechTarget: "AWS Kiro coding agents highlight spec-driven development"

### Test-Driven Development
- Kent Beck "Test Driven Development: By Example"
- Martin Fowler "Refactoring"

### アーキテクチャ
- Clean Architecture（Robert C. Martin）
- Domain-Driven Design（Eric Evans）
- Hexagonal Architecture（Alistair Cockburn）

---

**最終更新**: 2025-10-16
**作成者**: Claude Code
**関連ドキュメント**: [INTEGRATION_PLAN.md](./INTEGRATION_PLAN.md)
