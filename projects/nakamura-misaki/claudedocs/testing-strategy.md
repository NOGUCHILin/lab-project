# Testing Strategy - TDD必須

**nakamura-misaki プロジェクトのテスト戦略**

すべての新機能・変更は**テスト駆動開発（TDD）**で実装すること。

---

## 🎯 TDDの3原則

### 1. Red - 失敗するテストを書く

**最初にテストを書き、失敗を確認する**

```python
# 例: tests/unit/contexts/project_management/domain/entities/test_project.py

def test_create_project_with_valid_data():
    """プロジェクト作成 - 正常系"""
    # Arrange
    name = "新規プロジェクト"
    owner_user_id = "U123456"

    # Act
    project = Project.create(
        name=name,
        owner_user_id=owner_user_id,
    )

    # Assert
    assert project.name == name
    assert project.owner_user_id == owner_user_id
    assert project.status == ProjectStatus.ACTIVE
    assert len(project.task_ids) == 0
```

**実行**: `pytest tests/unit/` → ❌ **FAIL**（実装がないため）

### 2. Green - 最小限の実装でテストを通す

**テストが通る最小限のコードを実装する**

```python
# src/contexts/project_management/domain/entities/project.py

class Project:
    @classmethod
    def create(cls, name: str, owner_user_id: str) -> "Project":
        """Factory method for creating new project"""
        return cls(
            project_id=uuid4(),
            name=name,
            owner_user_id=owner_user_id,
            status=ProjectStatus.ACTIVE,
            task_ids=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
```

**実行**: `pytest tests/unit/` → ✅ **PASS**

### 3. Refactor - リファクタリング

**テストを通したまま、コードを改善する**

- 重複除去
- 命名改善
- パフォーマンス最適化

**重要**: リファクタリング中も常に`pytest`を実行してグリーンを維持

---

## 📋 テストレベルと責務

### Unit Tests（ユニットテスト）

**対象**: 単一のクラス・関数（外部依存なし）

**配置**: `tests/unit/contexts/<context_name>/`

**特徴**:
- ✅ 高速実行（<1秒）
- ✅ 外部依存なし（DB, API, ファイルシステム不要）
- ✅ モック・スタブ活用
- ✅ pre-commit hookで必ず実行

**例**:
```python
# tests/unit/contexts/project_management/domain/entities/test_project.py

def test_add_task_to_project():
    """プロジェクトにタスク追加"""
    project = Project.create(name="Test", owner_user_id="U123")
    task_id = uuid4()

    project.add_task(task_id)

    assert task_id in project.task_ids
    assert len(project.task_ids) == 1

def test_add_duplicate_task_raises_error():
    """重複タスク追加でエラー"""
    project = Project.create(name="Test", owner_user_id="U123")
    task_id = uuid4()
    project.add_task(task_id)

    with pytest.raises(ValueError, match="already in project"):
        project.add_task(task_id)
```

### Integration Tests（インテグレーションテスト）

**対象**: 複数コンポーネント統合（DB, Repository等）

**配置**: `tests/integration/contexts/<context_name>/`

**特徴**:
- ⏱️ 中速実行（数秒）
- 🗄️ PostgreSQL必須（テストDB）
- 🔄 トランザクションロールバック
- 🔀 pre-commit hookで条件付き実行

**例**:
```python
# tests/integration/contexts/project_management/test_project_repository.py

@pytest.mark.integration
async def test_save_and_find_project(db_session):
    """プロジェクト保存・取得"""
    # Arrange
    repo = PostgreSQLProjectRepository(db_session)
    project = Project.create(name="Test Project", owner_user_id="U123")

    # Act
    await repo.save(project)
    found = await repo.find_by_id(project.project_id)

    # Assert
    assert found is not None
    assert found.name == "Test Project"
    assert found.owner_user_id == "U123"
```

### E2E Tests（エンドツーエンドテスト）

**対象**: API経由の全体フロー

**配置**: `tests/e2e/`

**特徴**:
- 🐌 低速実行（10秒以上）
- 🌐 FastAPI TestClient使用
- 🔗 全レイヤー統合
- 🎯 重要なユーザーシナリオのみ

**例**:
```python
# tests/e2e/test_project_api.py

@pytest.mark.e2e
async def test_create_project_via_api(client):
    """API経由でプロジェクト作成"""
    response = client.post(
        "/api/projects",
        json={"name": "API Test Project", "owner_user_id": "U123"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Test Project"
```

---

## 🔧 テストツール・ライブラリ

### pytest

**メインテストフレームワーク**

```bash
# すべてのテスト実行
pytest

# ユニットテストのみ
pytest tests/unit/

# 特定のファイル
pytest tests/unit/contexts/project_management/domain/entities/test_project.py

# 特定のテスト
pytest tests/unit/contexts/project_management/domain/entities/test_project.py::test_create_project

# カバレッジ付き
pytest --cov=src --cov-report=html
```

### pytest-asyncio

**非同期テスト対応**

```python
import pytest

@pytest.mark.asyncio
async def test_async_use_case():
    """非同期Use Caseのテスト"""
    result = await some_async_function()
    assert result == expected
```

### pytest Fixtures

**テストデータ・モック準備**

```python
# tests/conftest.py

@pytest.fixture
def sample_project():
    """テスト用プロジェクトFixture"""
    return Project.create(name="Test Project", owner_user_id="U123")

@pytest.fixture
async def db_session():
    """テスト用DBセッションFixture（トランザクションロールバック）"""
    async with async_sessionmaker() as session:
        async with session.begin():
            yield session
            await session.rollback()
```

### unittest.mock

**モック・スタブ作成**

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_use_case_with_mock():
    """Use Caseテスト - リポジトリモック"""
    # Arrange
    mock_repo = AsyncMock(spec=ProjectRepository)
    mock_repo.save.return_value = None
    use_case = CreateProjectUseCase(mock_repo)

    # Act
    dto = CreateProjectDTO(name="Test", owner_user_id="U123")
    result = await use_case.execute(dto)

    # Assert
    mock_repo.save.assert_called_once()
    assert result.name == "Test"
```

---

## 📐 テスト構成パターン

### AAA Pattern（Arrange-Act-Assert）

**すべてのテストはAAA構造に従う**:

```python
def test_example():
    # Arrange（準備）: テストデータ・モック準備
    project = Project.create(name="Test", owner_user_id="U123")
    task_id = uuid4()

    # Act（実行）: テスト対象の実行
    project.add_task(task_id)

    # Assert（検証）: 結果検証
    assert task_id in project.task_ids
```

### Given-When-Then（BDD風）

**複雑なシナリオはBDD風に記述**:

```python
def test_project_completion_percentage():
    """Given: プロジェクトに3つのタスク（1つ完了）
       When: 進捗を計算
       Then: 完了率33.33%"""
    # Given
    project = Project.create(name="Test", owner_user_id="U123")
    project.add_task(uuid4())  # pending
    project.add_task(uuid4())  # pending
    completed_task_id = uuid4()
    project.add_task(completed_task_id)  # completed

    # When
    # (Use Caseでタスクステータスを取得して計算)

    # Then
    assert project.completion_percentage == 33.33
```

---

## 🚀 TDDワークフロー（実践例）

### ケーススタディ: Phase 2「Task Dependencies」実装

#### ステップ1: Red - テストを書く

```python
# tests/unit/contexts/task_dependencies/domain/entities/test_task_dependency.py

def test_create_task_dependency():
    """タスク依存関係作成"""
    blocker_task_id = uuid4()
    blocked_task_id = uuid4()

    dependency = TaskDependency.create(
        blocker_task_id=blocker_task_id,
        blocked_task_id=blocked_task_id,
    )

    assert dependency.blocker_task_id == blocker_task_id
    assert dependency.blocked_task_id == blocked_task_id
    assert dependency.status == DependencyStatus.ACTIVE
```

**実行**: `pytest tests/unit/` → ❌ **FAIL**（`TaskDependency`クラスが存在しない）

#### ステップ2: Green - 最小実装

```python
# src/contexts/task_dependencies/domain/entities/task_dependency.py

@dataclass
class TaskDependency:
    dependency_id: UUID
    blocker_task_id: UUID
    blocked_task_id: UUID
    status: DependencyStatus
    created_at: datetime

    @classmethod
    def create(cls, blocker_task_id: UUID, blocked_task_id: UUID) -> "TaskDependency":
        return cls(
            dependency_id=uuid4(),
            blocker_task_id=blocker_task_id,
            blocked_task_id=blocked_task_id,
            status=DependencyStatus.ACTIVE,
            created_at=datetime.now(),
        )
```

**実行**: `pytest tests/unit/` → ✅ **PASS**

#### ステップ3: 次のテスト追加（循環依存検証）

```python
def test_prevent_circular_dependency():
    """循環依存を防ぐ"""
    task_a = uuid4()
    task_b = uuid4()

    # A → B は許可
    dep1 = TaskDependency.create(task_a, task_b)

    # B → A は禁止（循環）
    with pytest.raises(ValueError, match="circular dependency"):
        TaskDependency.create(task_b, task_a, existing_deps=[dep1])
```

**実行**: `pytest tests/unit/` → ❌ **FAIL**

→ **循環検出ロジック実装** → ✅ **PASS**

#### ステップ4: Refactor

- ドメインロジックをEntity内に移動
- バリデーションを専用メソッドに分離
- テストケースを整理

---

## 📊 カバレッジ目標

### 最低カバレッジ要件

| レイヤー | 目標カバレッジ | 理由 |
|---------|--------------|------|
| **Domain** | **90%+** | ビジネスロジックの中核 |
| **Application** | **85%+** | Use Caseの網羅 |
| **Infrastructure** | **70%+** | Repository実装 |
| **Tools** | **80%+** | Claude Tool Use API |

### カバレッジ測定

```bash
# カバレッジ測定
pytest --cov=src --cov-report=html

# レポート確認
open htmlcov/index.html
```

---

## ✅ pre-commit Hooks

### pytest-unit（必須）

**すべてのコミット前に自動実行**

```yaml
# .pre-commit-config.yaml
- id: pytest-unit
  name: pytest-unit
  entry: uv run pytest tests/unit/ -v
  language: system
  pass_filenames: false
  always_run: true
```

### pytest-integration（条件付き）

**`tests/integration/`配下のファイル変更時のみ**

```yaml
- id: pytest-integration (conditional)
  name: pytest-integration (conditional)
  entry: uv run pytest tests/integration/ -v -m integration
  language: system
  files: ^tests/integration/
  pass_filenames: false
```

---

## 🎓 TDDベストプラクティス

### 1. テストファーストを徹底

❌ **NG**: 実装してからテストを書く
```python
# 実装を先に書く
def create_project(...):
    ...

# 後からテストを追加
def test_create_project():
    ...
```

✅ **OK**: テストを先に書く
```python
# 1. テストを書く
def test_create_project():
    project = Project.create(...)
    assert project.name == "Test"

# 2. 実装する
def create_project(...):
    ...
```

### 2. 1テスト1責務

❌ **NG**: 複数の検証を1テストに詰め込む
```python
def test_project_operations():
    project = Project.create(...)
    project.add_task(...)
    project.complete()
    project.archive()
    # 複数の検証...
```

✅ **OK**: 1テスト1検証
```python
def test_create_project():
    ...

def test_add_task_to_project():
    ...

def test_complete_project():
    ...
```

### 3. テストは読みやすく

- **明確な命名**: `test_<何をテストするか>_<期待される結果>`
- **AAA構造**: Arrange → Act → Assert
- **Docstring**: 日本語で意図を明記

```python
def test_add_task_to_full_project_raises_error():
    """定員に達したプロジェクトへのタスク追加でエラー"""
    # Arrange
    project = Project.create(name="Test", owner_user_id="U123", max_tasks=2)
    project.add_task(uuid4())
    project.add_task(uuid4())

    # Act & Assert
    with pytest.raises(ValueError, match="project is full"):
        project.add_task(uuid4())
```

### 4. モックは最小限に

❌ **NG**: 不必要なモック
```python
# Domain層のテストでRepositoryをモック（不要）
mock_repo = MagicMock()
entity = DomainEntity(repo=mock_repo)
```

✅ **OK**: 外部依存のみモック
```python
# Use Caseテストで Repository をモック（必要）
mock_repo = AsyncMock(spec=ProjectRepository)
use_case = CreateProjectUseCase(mock_repo)
```

---

## 📚 参考資料

- [pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)
- [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)

---

最終更新: 2025-10-26（TDD戦略確立）
