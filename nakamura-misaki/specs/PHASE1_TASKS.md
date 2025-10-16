# Phase 3: Tasks - Context基盤構築の実装タスク分解

**nakamura-misaki v6.0.0 - Phase 1実装タスク**

---

## 🎯 タスク分解の方針

Phase 2: Planで設計した内容を、**1つのCommitで完了できる小単位**に分解。

### タスクの基準

- ✅ **1タスク = 30分〜2時間**
- ✅ **独立してテスト可能**
- ✅ **明確なDefinition of Done**
- ✅ **TDDサイクル適用可能**（Spec → Test → Code → Commit）

---

## 📊 タスク一覧サマリー

| Step | タスク数 | 合計見積もり | 依存関係 |
|------|---------|------------|---------|
| Step 1: 基盤準備 | 2 | 1時間 | なし |
| Step 2: Domain層 | 5 | 4時間 | Step 1 |
| Step 3: Shared Kernel | 3 | 1.5時間 | Step 1 |
| Step 4: Application層 | 6 | 3.5時間 | Step 2, 3 |
| Step 5: Adapters層 | 7 | 5時間 | Step 4 |
| Step 6: Infrastructure層 | 4 | 2.5時間 | Step 5 |
| Step 7: 統合とテスト | 4 | 3.5時間 | Step 6 |
| **合計** | **31** | **21時間** | - |

**推奨スケジュール**: 3日間（1日7時間×3日）

---

## 📋 Step 1: 基盤準備（1時間）

### Task 1.1: ディレクトリ構造作成

**目的**: Phase 2で設計したディレクトリ構造を作成

**Definition of Done**:
- [ ] `contexts/personal_tasks/` 配下の全ディレクトリ作成
- [ ] 各ディレクトリに `__init__.py` 配置
- [ ] `tests/unit/`, `tests/integration/`, `tests/e2e/` 作成
- [ ] `specs/` ディレクトリ作成（既存）
- [ ] ディレクトリ構造確認スクリプト実行成功

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のディレクトリ構造を確認
# 2. 実装: mkdir -p で構造作成
# 3. 検証: ディレクトリ存在確認
# 4. Commit
```

**実装コマンド**:
```bash
# ディレクトリ作成
mkdir -p src/contexts/personal_tasks/{domain/{models,repositories,services},application/{use_cases,dto},adapters/{primary/{api/routes,tools},secondary},infrastructure}
mkdir -p src/shared_kernel/{domain/value_objects,infrastructure}
mkdir -p tests/{unit/{personal_tasks/{domain/{models,services},application/use_cases},shared_kernel/domain},integration/personal_tasks/adapters/secondary,e2e}

# __init__.py 作成
find src/contexts -type d -exec touch {}/__init__.py \;
find src/shared_kernel -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;

# 確認
tree src/contexts src/shared_kernel tests -L 4
```

**検証方法**:
```bash
# ディレクトリ数確認
find src/contexts/personal_tasks -type d | wc -l  # 期待値: 14
find src/shared_kernel -type d | wc -l            # 期待値: 5
find tests -type d | wc -l                        # 期待値: 12
```

**見積もり**: 30分

**依存**: なし

**Commit Message**:
```
chore(structure): Create directory structure for Phase 1

- Add contexts/personal_tasks/ with 4-layer structure
- Add shared_kernel/ with domain and infrastructure
- Add tests/ structure (unit/integration/e2e)
- Add __init__.py to all directories

Relates-to: #phase1-task1.1
```

---

### Task 1.2: pytest設定とconftest.py作成

**目的**: テスト環境の基盤を整備

**Definition of Done**:
- [ ] `tests/conftest.py` 作成
- [ ] DB Fixture定義
- [ ] pytest設定確認（pyproject.toml）
- [ ] サンプルテスト実行成功

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のテスト戦略を確認
# 2. Test: サンプルテスト作成
# 3. 実装: conftest.py 作成
# 4. 検証: pytest実行成功
# 5. Commit
```

**実装内容**:
```python
# tests/conftest.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def event_loop():
    """イベントループFixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine():
    """DB Engine Fixture（テスト用）"""
    engine = create_async_engine(
        "postgresql+asyncpg://nakamura_misaki:@localhost:5432/nakamura_misaki_test",
        echo=False
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """DB Session Fixture"""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# サンプルテスト
# tests/test_sample.py
def test_sample():
    """サンプルテスト"""
    assert True
```

**検証方法**:
```bash
uv run pytest tests/test_sample.py -v
```

**見積もり**: 30分

**依存**: Task 1.1

**Commit Message**:
```
test(config): Add pytest configuration and fixtures

- Add conftest.py with DB fixtures
- Add event_loop fixture for async tests
- Add sample test to verify setup
- Verify pytest runs successfully

Relates-to: #phase1-task1.2
```

---

## 📋 Step 2: Domain層（4時間）

### Task 2.1: TaskStatus Enum実装 + Test

**目的**: Task Domain Modelで使うEnum定義

**Definition of Done**:
- [ ] `TaskStatus` Enum実装
- [ ] Unit Test作成（3ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のTaskStatus定義
# 2. 🔴 Red: tests/unit/personal_tasks/domain/models/test_task_status.py 作成
# 3. 🟢 Green: 実装
# 4. 🔵 Refactor
# 5. Commit
```

**Test実装**:
```python
# tests/unit/personal_tasks/domain/models/test_task_status.py

import pytest
from contexts.personal_tasks.domain.models.task import TaskStatus


class TestTaskStatus:
    """TaskStatus Enumのテスト"""

    def test_all_statuses_exist(self):
        """全てのステータスが存在する"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"

    def test_status_from_string(self):
        """文字列からEnumに変換できる"""
        status = TaskStatus("pending")
        assert status == TaskStatus.PENDING

    def test_invalid_status_raises_error(self):
        """不正なステータスはエラー"""
        with pytest.raises(ValueError):
            TaskStatus("invalid")
```

**実装**:
```python
# contexts/personal_tasks/domain/models/task.py

from enum import Enum


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

**見積もり**: 20分

**依存**: Task 1.1

**Commit Message**:
```
feat(personal-tasks): Add TaskStatus enum with TDD

- Add TaskStatus enum with 3 statuses
- Add unit tests (3 test cases)
- All tests passing

Tests: 3/3 passing
Relates-to: #phase1-task2.1
```

---

### Task 2.2: Task Domain Model実装（Part 1: 基本構造）

**目的**: Task集約ルートの基本構造を実装

**Definition of Done**:
- [ ] `Task` dataclass定義
- [ ] `create()` ファクトリメソッド実装
- [ ] Unit Test作成（5ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のTask Model定義
# 2. 🔴 Red: tests/unit/personal_tasks/domain/models/test_task.py 作成
# 3. 🟢 Green: Task dataclass + create() 実装
# 4. 🔵 Refactor
# 5. Commit
```

**Test実装**:
```python
# tests/unit/personal_tasks/domain/models/test_task.py

import pytest
from datetime import datetime, UTC
from uuid import UUID

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
        assert isinstance(task.id, UUID)
        assert task.title == "レポート作成"
        assert task.assignee_user_id == "U12345"
        assert task.creator_user_id == "U12345"
        assert task.status == TaskStatus.PENDING
        assert task.description is None
        assert task.due_at is None
        assert task.completed_at is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_with_all_fields(self):
        """全フィールド指定でタスク作成"""
        # Given
        due_date = datetime(2025, 10, 20, tzinfo=UTC)

        # When
        task = Task.create(
            title="レポート作成",
            assignee_user_id="U12345",
            creator_user_id="U12345",
            description="詳細説明",
            due_at=due_date
        )

        # Then
        assert task.description == "詳細説明"
        assert task.due_at == due_date

    def test_create_task_with_empty_title_raises_error(self):
        """空のタイトルでエラー"""
        # When & Then
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task.create(
                title="",
                assignee_user_id="U12345",
                creator_user_id="U12345"
            )

    def test_create_task_trims_whitespace_from_title(self):
        """タイトルの空白がトリムされる"""
        # When
        task = Task.create(
            title="  レポート作成  ",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        # Then
        assert task.title == "レポート作成"

    def test_created_at_and_updated_at_are_same_on_creation(self):
        """作成時はcreated_atとupdated_atが同じ"""
        # When
        task = Task.create(
            title="テスト",
            assignee_user_id="U12345",
            creator_user_id="U12345"
        )

        # Then
        assert task.created_at == task.updated_at
```

**実装**:
```python
# contexts/personal_tasks/domain/models/task.py

from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import UUID, uuid4
from enum import Enum


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Task:
    """個人タスク（集約ルート）"""
    id: UUID
    title: str
    description: str | None
    assignee_user_id: str
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
        """ファクトリメソッド：新しいタスクを作成"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

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
```

**見積もり**: 1時間

**依存**: Task 2.1

**Commit Message**:
```
feat(personal-tasks): Add Task domain model with create method

- Add Task dataclass with all fields
- Add create() factory method
- Add input validation (title cannot be empty)
- Add unit tests (5 test cases)

Tests: 5/5 passing
Relates-to: #phase1-task2.2
```

---

### Task 2.3: Task Domain Model実装（Part 2: complete()メソッド）

**目的**: タスク完了ビジネスロジック実装

**Definition of Done**:
- [ ] `complete()` メソッド実装
- [ ] Unit Test作成（3ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のcomplete()定義
# 2. 🔴 Red: TestTaskCompletion クラス追加
# 3. 🟢 Green: complete() 実装
# 4. 🔵 Refactor
# 5. Commit
```

**Test実装**:
```python
# tests/unit/personal_tasks/domain/models/test_task.py に追加

class TestTaskCompletion:
    """Task完了のテスト"""

    def test_complete_task_changes_status_to_completed(self):
        """完了でステータスがCOMPLETEDになる"""
        # Given
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        assert task.status == TaskStatus.PENDING
        assert task.completed_at is None

        # When
        task.complete()

        # Then
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    def test_complete_already_completed_task_raises_error(self):
        """完了済みタスクの再完了はエラー"""
        # Given
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        task.complete()

        # When & Then
        with pytest.raises(ValueError, match="already completed"):
            task.complete()

    def test_complete_updates_timestamp(self):
        """完了時にupdated_atが更新される"""
        # Given
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        original_updated_at = task.updated_at

        # When
        import time
        time.sleep(0.01)
        task.complete()

        # Then
        assert task.updated_at > original_updated_at
```

**実装**:
```python
# contexts/personal_tasks/domain/models/task.py に追加

    def complete(self) -> None:
        """タスクを完了する

        Raises:
            ValueError: 既に完了済みの場合
        """
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Task is already completed")

        now = datetime.now(UTC)
        self.status = TaskStatus.COMPLETED
        self.completed_at = now
        self.updated_at = now
```

**見積もり**: 30分

**依存**: Task 2.2

**Commit Message**:
```
feat(personal-tasks): Add Task.complete() method with TDD

- Add complete() method to Task model
- Add validation for already completed tasks
- Add completed_at timestamp update
- Add unit tests (3 test cases)

Tests: 8/8 passing (cumulative)
Relates-to: #phase1-task2.3
```

---

### Task 2.4: Task Domain Model実装（Part 3: reassign()とupdate()）

**目的**: タスク更新ビジネスロジック実装

**Definition of Done**:
- [ ] `reassign()` メソッド実装
- [ ] `update()` メソッド実装
- [ ] Unit Test作成（5ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のreassign(), update()定義
# 2. 🔴 Red: TestTaskReassignment, TestTaskUpdate クラス追加
# 3. 🟢 Green: reassign(), update() 実装
# 4. 🔵 Refactor
# 5. Commit
```

**Test実装**:
```python
# tests/unit/personal_tasks/domain/models/test_task.py に追加

class TestTaskReassignment:
    """Task担当者変更のテスト"""

    def test_reassign_changes_assignee(self):
        """担当者変更が正しく動作する"""
        # Given
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When
        task.reassign(new_assignee_user_id="U456")

        # Then
        assert task.assignee_user_id == "U456"

    def test_reassign_with_empty_user_id_raises_error(self):
        """空のuser_idはエラー"""
        # Given
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When & Then
        with pytest.raises(ValueError, match="Assignee user ID cannot be empty"):
            task.reassign(new_assignee_user_id="")


class TestTaskUpdate:
    """Task更新のテスト"""

    def test_update_title(self):
        """タイトル更新"""
        # Given
        task = Task.create(
            title="旧タイトル",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When
        task.update(title="新タイトル")

        # Then
        assert task.title == "新タイトル"

    def test_update_description(self):
        """説明更新"""
        # Given
        task = Task.create(
            title="テスト",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When
        task.update(description="新しい説明")

        # Then
        assert task.description == "新しい説明"

    def test_update_with_empty_title_raises_error(self):
        """空のタイトルはエラー"""
        # Given
        task = Task.create(
            title="テスト",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When & Then
        with pytest.raises(ValueError, match="title cannot be empty"):
            task.update(title="")
```

**実装**:
```python
# contexts/personal_tasks/domain/models/task.py に追加

    def reassign(self, new_assignee_user_id: str) -> None:
        """担当者を変更する

        Args:
            new_assignee_user_id: 新しい担当者のSlack User ID

        Raises:
            ValueError: new_assignee_user_idが空の場合
        """
        if not new_assignee_user_id:
            raise ValueError("Assignee user ID cannot be empty")

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

**見積もり**: 45分

**依存**: Task 2.3

**Commit Message**:
```
feat(personal-tasks): Add Task.reassign() and update() methods

- Add reassign() method for changing assignee
- Add update() method for updating task fields
- Add input validation
- Add unit tests (5 test cases)

Tests: 13/13 passing (cumulative)
Relates-to: #phase1-task2.4
```

---

### Task 2.5: TaskRepository Interface定義

**目的**: Repository抽象化層を定義

**Definition of Done**:
- [ ] `TaskRepository` ABC定義
- [ ] 5つのメソッド定義（save, find_by_id, find_by_assignee, find_today_tasks, delete）
- [ ] 完全な型ヒントとdocstring
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のTaskRepository定義
# 2. 実装: TaskRepository ABC定義（テストは実装時に書く）
# 3. Commit
```

**実装**:
```python
# contexts/personal_tasks/domain/repositories/task_repository.py

from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime

from ..models.task import Task


class TaskRepository(ABC):
    """タスクリポジトリインターフェース"""

    @abstractmethod
    async def save(self, task: Task) -> Task:
        """タスクを保存

        Args:
            task: 保存するタスク

        Returns:
            保存されたタスク
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

**見積もり**: 30分

**依存**: Task 2.2

**Commit Message**:
```
feat(personal-tasks): Add TaskRepository interface

- Add TaskRepository ABC with 5 methods
- Add complete type hints and docstrings
- Define contract for repository implementations

Relates-to: #phase1-task2.5
```

---

## 📋 Step 3: Shared Kernel（1.5時間）

### Task 3.1: UserId Value Object実装 + Test

**目的**: ユーザーID値オブジェクト実装

**Definition of Done**:
- [ ] `UserId` 値オブジェクト実装
- [ ] Unit Test作成（3ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のUserId定義
# 2. 🔴 Red: tests/unit/shared_kernel/domain/test_value_objects.py 作成
# 3. 🟢 Green: UserId 実装
# 4. 🔵 Refactor
# 5. Commit
```

**Test実装**:
```python
# tests/unit/shared_kernel/domain/test_value_objects.py

import pytest
from shared_kernel.domain.value_objects.user_id import UserId


class TestUserId:
    """UserId値オブジェクトのテスト"""

    def test_create_valid_user_id(self):
        """有効なUser IDで作成"""
        # When
        user_id = UserId("U12345")

        # Then
        assert user_id.value == "U12345"

    def test_empty_user_id_raises_error(self):
        """空のUser IDはエラー"""
        # When & Then
        with pytest.raises(ValueError, match="UserId cannot be empty"):
            UserId("")

    def test_invalid_format_user_id_raises_error(self):
        """Slack形式でないUser IDはエラー"""
        # When & Then
        with pytest.raises(ValueError, match="must start with 'U'"):
            UserId("INVALID")
```

**実装**:
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
```

**見積もり**: 30分

**依存**: Task 1.1

**Commit Message**:
```
feat(shared): Add UserId value object with TDD

- Add UserId immutable value object
- Add validation (must start with 'U')
- Add unit tests (3 test cases)

Tests: 3/3 passing
Relates-to: #phase1-task3.1
```

---

### Task 3.2: TaskStatus Value Object移動

**目的**: TaskStatusをShared Kernelに移動

**Definition of Done**:
- [ ] `TaskStatus` をshared_kernelに移動
- [ ] personal_tasksから参照するよう修正
- [ ] 全テストパス
- [ ] Commit完了

**実装**:
```bash
# 1. TaskStatusをshared_kernelに移動
mv contexts/personal_tasks/domain/models/task.py shared_kernel/domain/value_objects/task_status.py

# 2. task.pyを再作成し、TaskStatusをimport
# 3. テスト実行
```

**実装コード**:
```python
# shared_kernel/domain/value_objects/task_status.py

from enum import Enum


class TaskStatus(Enum):
    """タスクステータス（値オブジェクト）

    両Context（Personal/Work）で共通
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# contexts/personal_tasks/domain/models/task.py
# 冒頭に追加
from shared_kernel.domain.value_objects.task_status import TaskStatus
```

**見積もり**: 15分

**依存**: Task 2.4, Task 3.1

**Commit Message**:
```
refactor(shared): Move TaskStatus to shared_kernel

- Move TaskStatus from personal_tasks to shared_kernel
- Update imports in personal_tasks
- All tests still passing

Relates-to: #phase1-task3.2
```

---

### Task 3.3: ClaudeClient, SlackClient移動

**目的**: 既存のClaudeClient, SlackClientをShared Kernelに移動

**Definition of Done**:
- [ ] 既存の`claude_adapter.py`を`shared_kernel/infrastructure/claude_client.py`に移動
- [ ] 既存の`slack_adapter.py`を`shared_kernel/infrastructure/slack_client.py`に移動
- [ ] Import文を全て修正
- [ ] 全テストパス（既存テストがあれば）
- [ ] Commit完了

**実装**:
```bash
# 既存ファイルの確認
ls -la src/adapters/secondary/claude_adapter.py
ls -la src/adapters/secondary/slack_adapter.py

# 移動
mv src/adapters/secondary/claude_adapter.py shared_kernel/infrastructure/claude_client.py
mv src/adapters/secondary/slack_adapter.py shared_kernel/infrastructure/slack_client.py

# Import文修正（複数ファイル）
# - src/adapters/primary/slack_event_handler.py
# - src/domain/services/claude_agent_service.py
# 等
```

**見積もり**: 45分

**依存**: Task 3.2

**Commit Message**:
```
refactor(shared): Move ClaudeClient and SlackClient to shared_kernel

- Move claude_adapter.py to shared_kernel/infrastructure/claude_client.py
- Move slack_adapter.py to shared_kernel/infrastructure/slack_client.py
- Update all import statements
- All existing tests passing

Relates-to: #phase1-task3.3
```

---

## 📋 Step 4: Application層（3.5時間）

### Task 4.1: DTO定義

**目的**: Application層で使うデータ転送オブジェクト定義

**Definition of Done**:
- [ ] `RegisterTaskDTO`, `CompleteTaskDTO`, `UpdateTaskDTO`, `TaskDTO` 定義
- [ ] `TaskDTO.from_domain()` 実装
- [ ] Unit Test作成（2ケース）
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のDTO定義
# 2. 🔴 Red: tests/unit/personal_tasks/application/dto/test_task_dto.py 作成
# 3. 🟢 Green: DTO実装
# 4. Commit
```

**Test実装**:
```python
# tests/unit/personal_tasks/application/dto/test_task_dto.py

from datetime import datetime, UTC
from uuid import uuid4

from contexts.personal_tasks.domain.models.task import Task, TaskStatus
from contexts.personal_tasks.application.dto.task_dto import TaskDTO


class TestTaskDTO:
    """TaskDTO変換のテスト"""

    def test_from_domain_converts_correctly(self):
        """Domain ModelからDTOに正しく変換される"""
        # Given
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123",
            description="説明",
            due_at=datetime(2025, 10, 20, tzinfo=UTC)
        )

        # When
        dto = TaskDTO.from_domain(task)

        # Then
        assert dto.id == task.id
        assert dto.title == "テストタスク"
        assert dto.status == "pending"  # Enum.value
        assert dto.description == "説明"
        assert dto.due_at == task.due_at

    def test_from_domain_with_completed_task(self):
        """完了済みタスクの変換"""
        # Given
        task = Task.create(
            title="テスト",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        task.complete()

        # When
        dto = TaskDTO.from_domain(task)

        # Then
        assert dto.status == "completed"
        assert dto.completed_at is not None
```

**実装**:
```python
# contexts/personal_tasks/application/dto/task_dto.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ...domain.models.task import Task


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

**見積もり**: 30分

**依存**: Task 2.4

**Commit Message**:
```
feat(personal-tasks): Add Task DTOs

- Add RegisterTaskDTO, CompleteTaskDTO, UpdateTaskDTO
- Add TaskDTO with from_domain() converter
- Add unit tests (2 test cases)

Tests: 2/2 passing
Relates-to: #phase1-task4.1
```

---

### Task 4.2: RegisterTaskUseCase実装 + Test

**目的**: タスク登録ユースケース実装

**Definition of Done**:
- [ ] `RegisterTaskUseCase` 実装
- [ ] Unit Test作成（モック使用、3ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のRegisterTaskUseCase定義
# 2. 🔴 Red: tests/unit/personal_tasks/application/use_cases/test_register_task.py
# 3. 🟢 Green: RegisterTaskUseCase 実装
# 4. 🔵 Refactor
# 5. Commit
```

**Test実装**:
```python
# tests/unit/personal_tasks/application/use_cases/test_register_task.py

import pytest
from unittest.mock import AsyncMock
from datetime import datetime, UTC

from contexts.personal_tasks.application.use_cases.register_task import RegisterTaskUseCase
from contexts.personal_tasks.application.dto.task_dto import RegisterTaskDTO
from contexts.personal_tasks.domain.models.task import Task


@pytest.mark.asyncio
class TestRegisterTaskUseCase:
    """RegisterTaskUseCaseのテスト"""

    async def test_execute_creates_and_saves_task(self):
        """タスクを作成して保存する"""
        # Given
        mock_repo = AsyncMock()
        task = Task.create(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        mock_repo.save.return_value = task

        use_case = RegisterTaskUseCase(task_repository=mock_repo)
        dto = RegisterTaskDTO(
            title="テストタスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When
        result = await use_case.execute(dto)

        # Then
        assert result.title == "テストタスク"
        assert result.status == "pending"
        mock_repo.save.assert_called_once()

    async def test_execute_with_all_fields(self):
        """全フィールド指定で登録"""
        # Given
        mock_repo = AsyncMock()
        due_date = datetime(2025, 10, 20, tzinfo=UTC)
        task = Task.create(
            title="テスト",
            assignee_user_id="U123",
            creator_user_id="U123",
            description="説明",
            due_at=due_date
        )
        mock_repo.save.return_value = task

        use_case = RegisterTaskUseCase(task_repository=mock_repo)
        dto = RegisterTaskDTO(
            title="テスト",
            assignee_user_id="U123",
            creator_user_id="U123",
            description="説明",
            due_at=due_date
        )

        # When
        result = await use_case.execute(dto)

        # Then
        assert result.description == "説明"
        assert result.due_at == due_date

    async def test_execute_with_empty_title_raises_error(self):
        """空のタイトルはエラー"""
        # Given
        mock_repo = AsyncMock()
        use_case = RegisterTaskUseCase(task_repository=mock_repo)
        dto = RegisterTaskDTO(
            title="",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When & Then
        with pytest.raises(ValueError, match="title cannot be empty"):
            await use_case.execute(dto)
```

**実装**:
```python
# contexts/personal_tasks/application/use_cases/register_task.py

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

**見積もり**: 45分

**依存**: Task 2.5, Task 4.1

**Commit Message**:
```
feat(personal-tasks): Add RegisterTaskUseCase with TDD

- Add RegisterTaskUseCase implementation
- Use repository interface for persistence
- Add unit tests with mock (3 test cases)

Tests: 3/3 passing
Relates-to: #phase1-task4.2
```

---

### Task 4.3: CompleteTaskUseCase実装 + Test

**目的**: タスク完了ユースケース実装

**見積もり**: 30分
**依存**: Task 4.2
**実装**: Task 4.2と同様のパターン

---

### Task 4.4: UpdateTaskUseCase実装 + Test

**目的**: タスク更新ユースケース実装

**見積もり**: 30分
**依存**: Task 4.3
**実装**: Task 4.2と同様のパターン

---

### Task 4.5: QueryUserTasksUseCase実装 + Test

**目的**: タスク一覧取得ユースケース実装

**見積もり**: 30分
**依存**: Task 4.4
**実装**: Task 4.2と同様のパターン

---

### Task 4.6: Conversation Model + Repository Interface

**目的**: Conversationドメインモデルとリポジトリ定義

**Definition of Done**:
- [ ] `Conversation`, `Message` 実装
- [ ] `ConversationRepository` インターフェース定義
- [ ] Unit Test作成（3ケース）
- [ ] Commit完了

**見積もり**: 1時間

**依存**: Task 2.5

**Commit Message**:
```
feat(personal-tasks): Add Conversation model and repository

- Add Conversation and Message domain models
- Add ConversationRepository interface
- Add unit tests (3 test cases)

Tests: 3/3 passing
Relates-to: #phase1-task4.6
```

---

## 📋 Step 5: Adapters層（5時間）

### Task 5.1: PostgreSQLTaskRepository実装 + Integration Test

**目的**: TaskRepositoryのPostgreSQL実装

**Definition of Done**:
- [ ] `PostgreSQLTaskRepository` 実装（5メソッド）
- [ ] Integration Test作成（実DB使用、5ケース）
- [ ] 全テストパス
- [ ] Commit完了

**TDDフロー**:
```bash
# 1. Spec確認: PHASE1_PLAN.md のPostgreSQLTaskRepository定義
# 2. 🔴 Red: tests/integration/personal_tasks/adapters/secondary/test_postgresql_task_repository.py
# 3. 🟢 Green: PostgreSQLTaskRepository 実装
# 4. Commit
```

**Test実装**:
```python
# tests/integration/personal_tasks/adapters/secondary/test_postgresql_task_repository.py

import pytest
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from contexts.personal_tasks.domain.models.task import Task
from contexts.personal_tasks.adapters.secondary.postgresql_task_repository import (
    PostgreSQLTaskRepository
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPostgreSQLTaskRepository:
    """PostgreSQLTaskRepository統合テスト"""

    async def test_save_and_find_by_id(self, db_session: AsyncSession):
        """保存と取得"""
        # Given
        repo = PostgreSQLTaskRepository(db_session)
        task = Task.create(
            title="統合テスト用タスク",
            assignee_user_id="U123",
            creator_user_id="U123"
        )

        # When
        saved = await repo.save(task)
        await db_session.commit()

        found = await repo.find_by_id(saved.id)

        # Then
        assert found is not None
        assert found.title == "統合テスト用タスク"
        assert found.id == saved.id

    async def test_find_by_assignee(self, db_session: AsyncSession):
        """担当者でタスク検索"""
        # Given
        repo = PostgreSQLTaskRepository(db_session)
        task1 = Task.create(
            title="タスク1",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        task2 = Task.create(
            title="タスク2",
            assignee_user_id="U123",
            creator_user_id="U123"
        )
        task3 = Task.create(
            title="タスク3",
            assignee_user_id="U456",
            creator_user_id="U456"
        )

        await repo.save(task1)
        await repo.save(task2)
        await repo.save(task3)
        await db_session.commit()

        # When
        user_tasks = await repo.find_by_assignee("U123")

        # Then
        assert len(user_tasks) == 2
        assert all(t.assignee_user_id == "U123" for t in user_tasks)

    # 他のテストケース（find_today_tasks, delete等）も同様に実装
```

**見積もり**: 2時間

**依存**: Task 2.5, Task 1.2（conftest.py）

**Commit Message**:
```
feat(personal-tasks): Add PostgreSQLTaskRepository implementation

- Implement all 5 repository methods
- Add integration tests with real DB (5 test cases)
- All tests passing

Tests: 5/5 passing
Relates-to: #phase1-task5.1
```

---

### Task 5.2〜5.7: 残りのAdapters層実装

- Task 5.2: PostgreSQLConversationRepository (1h)
- Task 5.3: TaskTools実装（Claude用Tool定義4つ）(1h)
- Task 5.4: SlackEventHandler移動・リファクタ (1h)
- Task 5.5: REST API Routes移動 (30min)
- Task 5.6: BaseToolクラス移動 (15min)
- Task 5.7: Adapters層統合テスト (45min)

---

## 📋 Step 6: Infrastructure層（2.5時間）

### Task 6.1: DIContainer実装

### Task 6.2: Database接続設定

### Task 6.3: Config設定

### Task 6.4: main.pyエントリーポイント更新

---

## 📋 Step 7: 統合とテスト（3.5時間）

### Task 7.1: Import文一括修正

### Task 7.2: E2Eテスト実装・実行

### Task 7.3: 本番環境デプロイ

### Task 7.4: 動作確認・トークン消費量確認

---

## 📊 実装順序とマイルストーン

### Day 1（7時間）
- Step 1: 基盤準備（1h）
- Step 2: Domain層（4h）
- Step 3: Shared Kernel（1.5h）
- 休憩: 0.5h

### Day 2（7時間）
- Step 4: Application層（3.5h）
- Step 5: Adapters層（前半2.5h）
- 休憩: 1h

### Day 3（7時間）
- Step 5: Adapters層（後半2.5h）
- Step 6: Infrastructure層（2.5h）
- Step 7: 統合とテスト（2h）

---

## ✅ 実装完了チェックリスト

### Step 1完了
- [ ] Task 1.1: ディレクトリ構造
- [ ] Task 1.2: pytest設定

### Step 2完了
- [ ] Task 2.1: TaskStatus
- [ ] Task 2.2: Task create()
- [ ] Task 2.3: Task complete()
- [ ] Task 2.4: Task reassign/update
- [ ] Task 2.5: TaskRepository Interface

### Step 3完了
- [ ] Task 3.1: UserId
- [ ] Task 3.2: TaskStatus移動
- [ ] Task 3.3: ClaudeClient/SlackClient移動

### Step 4完了
- [ ] Task 4.1: DTO定義
- [ ] Task 4.2: RegisterTaskUseCase
- [ ] Task 4.3: CompleteTaskUseCase
- [ ] Task 4.4: UpdateTaskUseCase
- [ ] Task 4.5: QueryUserTasksUseCase
- [ ] Task 4.6: Conversation Model

### Step 5完了
- [ ] Task 5.1: PostgreSQLTaskRepository
- [ ] Task 5.2: PostgreSQLConversationRepository
- [ ] Task 5.3: TaskTools
- [ ] Task 5.4: SlackEventHandler
- [ ] Task 5.5: REST API Routes
- [ ] Task 5.6: BaseToolクラス
- [ ] Task 5.7: Adapters統合テスト

### Step 6完了
- [ ] Task 6.1: DIContainer
- [ ] Task 6.2: Database接続
- [ ] Task 6.3: Config
- [ ] Task 6.4: main.py更新

### Step 7完了
- [ ] Task 7.1: Import修正
- [ ] Task 7.2: E2Eテスト
- [ ] Task 7.3: デプロイ
- [ ] Task 7.4: 動作確認

---

**作成日**: 2025-10-16
**作成者**: Claude Code
**レビュー**: 野口凜
**ステータス**: Draft → Review中
**次のステップ**: 承認後、Task 1.1から実装開始
