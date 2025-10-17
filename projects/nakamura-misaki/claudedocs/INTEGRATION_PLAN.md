# nakamura-misaki + staff-task-system 統合実装計画

**DDD + Clean Architecture + Spec-Driven Development + TDD による2つのタスク管理システムの統合設計**

---

## 📚 関連ドキュメント

| ドキュメント | 内容 |
|------------|------|
| **[DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md)** | 開発思想・方法論（Spec-Driven + TDD + Clean Architecture） |
| **INTEGRATION_PLAN.md** | このファイル - 統合アーキテクチャ設計 |
| **[V5_MIGRATION_SUMMARY.md](./V5_MIGRATION_SUMMARY.md)** | v5.0.0/v5.1.0の変更履歴 |

**重要**: 実装前に必ず [DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md) を読んでください。

---

## 🎯 統合の目的

### 背景
- **nakamura-misaki v5.1.0**: 個人向けタスク管理AIアシスタント（Slack Bot）
- **staff-task-system**: 業務向けスキルベースタスク割り当てシステム（YAML/File-based）

### なぜ統合するのか？
両システムは「タスク管理」という同じドメインを扱うが、**ビジネスルールが異なる**：

| 観点 | Personal Tasks | Work Tasks |
|------|---------------|-----------|
| **管理対象** | 個人のTODO | 業務タスク（査定/検品/出品/修理） |
| **割り当て方式** | 自分で作成・自由に変更 | スキルベース自動割り当て |
| **期限** | 任意 | 見積もり時間必須 |
| **スキル** | なし | スキルレベル・速度係数で管理 |
| **UI** | Slack Bot（AI Agent） | CLI Scripts（Claude Code） |
| **ストレージ** | PostgreSQL | YAML Files |

→ **統合により、両方のタスクを1つのシステムで管理しつつ、ドメインの独立性を保つ**

---

## 📐 アーキテクチャ設計原則

### 1. Bounded Context による縦割り（ドメイン分離）

```
nakamura-misaki/
├── shared_kernel/              # 共有カーネル
│   ├── domain/
│   │   └── value_objects/
│   │       ├── user_id.py
│   │       └── task_status.py
│   └── infrastructure/
│       ├── claude_client.py
│       ├── slack_client.py
│       └── prompt_templates.py
│
├── contexts/
│   ├── personal_tasks/         # Bounded Context 1
│   │   ├── domain/
│   │   ├── application/
│   │   ├── adapters/
│   │   └── infrastructure/
│   │
│   └── work_tasks/             # Bounded Context 2
│       ├── domain/
│       ├── application/
│       ├── adapters/
│       └── infrastructure/
│
└── anti_corruption_layer/      # 腐敗防止層（Context間通訳）
    ├── personal_to_work_adapter.py
    └── work_to_personal_adapter.py
```

### 2. Clean Architecture による横割り（レイヤー分離）

各Bounded Contextは標準的な4層構造：

```
contexts/personal_tasks/
├── domain/              # 1層目：ドメイン層
│   ├── models/
│   │   └── task.py     # PersonalTask（集約ルート）
│   ├── repositories/   # インターフェース定義
│   │   └── task_repository.py
│   └── services/       # ドメインサービス
│       └── intent_classifier.py
│
├── application/         # 2層目：アプリケーション層
│   ├── use_cases/      # ユースケース
│   │   ├── register_task.py
│   │   ├── complete_task.py
│   │   └── handle_user_message.py  # AI Agent司令塔
│   └── dto/            # データ転送オブジェクト
│       └── task_dto.py
│
├── adapters/            # 3層目：アダプター層
│   ├── primary/        # 入力側（UI）
│   │   ├── slack_event_handler.py  # Slack UI
│   │   └── tools/
│   │       └── task_tools.py       # AI Agent Tool定義
│   └── secondary/      # 出力側（永続化）
│       └── postgresql_task_repository.py
│
└── infrastructure/      # 4層目：インフラ層
    ├── di_container.py  # 依存性注入
    └── database.py      # DB接続管理
```

---

## 🧩 各層の責務と配置ルール

### AI Agent機能の配置

| AI機能 | 配置層 | 理由 |
|-------|--------|------|
| **System Prompt** | Infrastructure層 | Claude APIへの技術的入力 |
| **Tool定義** | Adapters層（Primary） | Claudeとのインターフェース |
| **意図理解（Intent Classification）** | Domain層（Services） | ビジネスルール（「登録」「完了」等の判定） |
| **会話オーケストレーション** | Application層（Use Cases） | AI Agent全体の司令塔 |
| **Claude API Client** | Infrastructure層 | 外部API呼び出しの技術詳細 |

**重要**: AIエージェントを独立したContextにはしない（UIの一種として既存4層に配置）

---

## 📊 Contextごとのドメインモデル

### Personal Tasks Context

#### Domain Models
```python
# contexts/personal_tasks/domain/models/task.py

@dataclass
class PersonalTask:
    """個人タスク（集約ルート）"""
    id: UUID
    title: str
    description: str | None
    assignee_user_id: str      # Slack User ID
    creator_user_id: str
    status: TaskStatus         # pending | in_progress | completed
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime

    def complete(self) -> None:
        """タスク完了（ドメインロジック）"""
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Already completed")
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now(UTC)

    def reassign(self, new_assignee: str) -> None:
        """担当者変更"""
        self.assignee_user_id = new_assignee
        self.updated_at = datetime.now(UTC)
```

#### Ubiquitous Language（ユビキタス言語）
- **Task**: 個人が管理する TODO
- **assignee**: 担当者（自分または他人）
- **due_at**: 期限（任意）

---

### Work Tasks Context

#### Domain Models
```python
# contexts/work_tasks/domain/models/work_task.py

@dataclass
class WorkTask:
    """業務タスク（集約ルート）"""
    id: str                    # "T20251015-001" 形式
    type: TaskType             # 査定 | 検品 | 出品 | 修理
    description: str
    assigned_to: str | None    # スタッフ名（細谷、江口、等）
    status: TaskStatus
    priority: Priority
    estimated_minutes: int     # 見積もり時間（必須）
    actual_minutes: int | None
    created_at: datetime

    def assign_to_staff(self, staff: Staff) -> None:
        """スキルベース割り当て（ドメインロジック）"""
        if not staff.can_perform(self.type):
            raise ValueError(f"{staff.name} cannot perform {self.type}")
        self.assigned_to = staff.name

    def complete_with_actual_time(self, actual_minutes: int) -> None:
        """実績時間付きで完了"""
        self.status = TaskStatus.COMPLETED
        self.actual_minutes = actual_minutes


@dataclass
class Staff:
    """スタッフ（エンティティ）"""
    name: str
    employee_id: str
    skills: dict[TaskType, Skill]  # スキル情報
    constraints: StaffConstraints   # 1日最大タスク数等

    def can_perform(self, task_type: TaskType) -> bool:
        """タスク実行可能判定"""
        return task_type in self.skills


@dataclass
class Skill:
    """スキル（値オブジェクト）"""
    level: int          # 1-3
    speed_factor: float # 1.0が標準
    certification: bool
```

#### Ubiquitous Language
- **WorkTask**: 業務タスク（査定/検品/出品/修理）
- **Staff**: スタッフ（細谷、江口、等）
- **Skill**: スキルレベル・速度係数
- **estimated_minutes**: 見積もり時間

---

## 🔗 Shared Kernel（共有カーネル）

両Contextで共有する最小限の部品。

### Value Objects

```python
# shared_kernel/domain/value_objects/user_id.py

@dataclass(frozen=True)
class UserId:
    """ユーザーID（値オブジェクト）"""
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("UserId cannot be empty")


# shared_kernel/domain/value_objects/task_status.py

class TaskStatus(Enum):
    """タスクステータス（両Contextで共通）"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

### Infrastructure

```python
# shared_kernel/infrastructure/claude_client.py

class ClaudeClient:
    """Claude API呼び出しクライアント（両Contextで共有）"""

    def __init__(self, api_key: str):
        self._client = AsyncAnthropic(api_key=api_key)

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict]
    ) -> ClaudeResponse:
        """Claude APIを呼び出す"""
        response = await self._client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=tools
        )
        return ClaudeResponse.from_api(response)


# shared_kernel/infrastructure/slack_client.py

class SlackClient:
    """Slack API呼び出しクライアント（両Contextで共有）"""
    # ... Slack通知機能
```

---

## 🛡️ Anti-Corruption Layer（腐敗防止層）

2つのContextの概念を通訳する層。

### ユースケース例：「個人タスクを業務タスクに変換」

```python
# anti_corruption_layer/personal_to_work_adapter.py

class PersonalToWorkTaskAdapter:
    """PersonalTask → WorkTask 変換"""

    def convert(self, personal_task: PersonalTask) -> WorkTask:
        """個人タスクを業務タスクに変換

        変換ルール:
        - PersonalTaskのdescriptionから業務種別を推測（査定/検品等）
        - estimated_minutesはデフォルト値を使用
        - assigned_toはSlack User IDからスタッフ名にマッピング
        """
        task_type = self._infer_task_type(personal_task.description)
        staff_name = self._map_slack_user_to_staff(personal_task.assignee_user_id)

        return WorkTask(
            id=self._generate_work_task_id(),
            type=task_type,
            description=personal_task.title,
            assigned_to=staff_name,
            status=self._convert_status(personal_task.status),
            priority=Priority.MEDIUM,
            estimated_minutes=self._get_default_estimate(task_type),
            actual_minutes=None,
            created_at=personal_task.created_at
        )

    def _infer_task_type(self, description: str | None) -> TaskType:
        """説明文から業務種別を推測"""
        if not description:
            return TaskType.KENPIN  # デフォルト

        if "査定" in description or "見積" in description:
            return TaskType.SATEI
        elif "検品" in description or "チェック" in description:
            return TaskType.KENPIN
        elif "出品" in description or "出す" in description:
            return TaskType.SHUPPIN
        elif "修理" in description:
            return TaskType.SHURI
        else:
            return TaskType.KENPIN
```

---

## 🔄 依存性注入とContext結合

### Infrastructure層での依存性解決

```python
# contexts/personal_tasks/infrastructure/di_container.py

class PersonalTasksDIContainer:
    """Personal Tasks Context専用のDIコンテナ"""

    def __init__(
        self,
        db_session,
        claude_client: ClaudeClient,  # Shared Kernelから注入
        slack_client: SlackClient     # Shared Kernelから注入
    ):
        self._session = db_session
        self._claude = claude_client
        self._slack = slack_client

        # リポジトリ（遅延初期化）
        self._task_repository = None
        self._conversation_repository = None

    @property
    def task_repository(self) -> TaskRepository:
        if self._task_repository is None:
            self._task_repository = PostgreSQLTaskRepository(self._session)
        return self._task_repository

    def build_handle_user_message_use_case(self) -> HandleUserMessageUseCase:
        """AI Agent司令塔UseCaseを構築"""
        return HandleUserMessageUseCase(
            claude_client=self._claude,
            task_repository=self.task_repository,
            conversation_repository=self.conversation_repository,
            intent_classifier=IntentClassifier()
        )


# contexts/work_tasks/infrastructure/di_container.py

class WorkTasksDIContainer:
    """Work Tasks Context専用のDIコンテナ"""

    def __init__(
        self,
        yaml_data_dir: Path,
        slack_client: SlackClient  # Shared Kernelから注入
    ):
        self._data_dir = yaml_data_dir
        self._slack = slack_client

        # リポジトリ（遅延初期化）
        self._work_task_repository = None
        self._staff_repository = None

    @property
    def work_task_repository(self) -> WorkTaskRepository:
        if self._work_task_repository is None:
            self._work_task_repository = YAMLWorkTaskRepository(self._data_dir)
        return self._work_task_repository
```

---

## 📂 ディレクトリ構造（実装後）

```
nakamura-misaki/
├── pyproject.toml
├── alembic/
│   ├── versions/
│   │   └── (personal_tasks用マイグレーション)
│   └── env.py
│
├── src/
│   ├── shared_kernel/
│   │   ├── domain/
│   │   │   └── value_objects/
│   │   │       ├── user_id.py
│   │   │       └── task_status.py
│   │   └── infrastructure/
│   │       ├── claude_client.py
│   │       ├── slack_client.py
│   │       └── prompt_templates.py
│   │
│   ├── contexts/
│   │   ├── __init__.py
│   │   │
│   │   ├── personal_tasks/
│   │   │   ├── domain/
│   │   │   │   ├── models/
│   │   │   │   │   ├── task.py
│   │   │   │   │   └── conversation.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── task_repository.py
│   │   │   │   │   └── conversation_repository.py
│   │   │   │   └── services/
│   │   │   │       └── intent_classifier.py
│   │   │   │
│   │   │   ├── application/
│   │   │   │   ├── use_cases/
│   │   │   │   │   ├── register_task.py
│   │   │   │   │   ├── complete_task.py
│   │   │   │   │   ├── update_task.py
│   │   │   │   │   ├── query_user_tasks.py
│   │   │   │   │   └── handle_user_message.py
│   │   │   │   └── dto/
│   │   │   │       └── task_dto.py
│   │   │   │
│   │   │   ├── adapters/
│   │   │   │   ├── primary/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   ├── app.py
│   │   │   │   │   │   └── routes/
│   │   │   │   │   │       └── slack.py
│   │   │   │   │   ├── slack_event_handler.py
│   │   │   │   │   └── tools/
│   │   │   │   │       └── task_tools.py
│   │   │   │   └── secondary/
│   │   │   │       ├── postgresql_task_repository.py
│   │   │   │       └── postgresql_conversation_repository.py
│   │   │   │
│   │   │   └── infrastructure/
│   │   │       ├── di_container.py
│   │   │       ├── database.py
│   │   │       └── config.py
│   │   │
│   │   └── work_tasks/
│   │       ├── domain/
│   │       │   ├── models/
│   │       │   │   ├── work_task.py
│   │       │   │   ├── staff.py
│   │       │   │   ├── skill.py
│   │       │   │   └── assignment_rule.py
│   │       │   ├── repositories/
│   │       │   │   ├── work_task_repository.py
│   │       │   │   ├── staff_repository.py
│   │       │   │   └── schedule_repository.py
│   │       │   └── services/
│   │       │       ├── assignment_service.py  # スキルベース割り当てロジック
│   │       │       └── workload_calculator.py
│   │       │
│   │       ├── application/
│   │       │   ├── use_cases/
│   │       │   │   ├── create_work_task.py
│   │       │   │   ├── assign_to_staff.py
│   │       │   │   ├── complete_work_task.py
│   │       │   │   ├── handle_absence.py
│   │       │   │   └── generate_daily_report.py
│   │       │   └── dto/
│   │       │       └── work_task_dto.py
│   │       │
│   │       ├── adapters/
│   │       │   ├── primary/
│   │       │   │   ├── cli/
│   │       │   │   │   ├── add_task.py
│   │       │   │   │   ├── update_task.py
│   │       │   │   │   ├── show_status.py
│   │       │   │   │   └── (その他CLIスクリプト)
│   │       │   │   └── tools/
│   │       │   │       └── work_task_tools.py  # AI Agent Tool
│   │       │   └── secondary/
│   │       │       ├── yaml_work_task_repository.py
│   │       │       ├── yaml_staff_repository.py
│   │       │       └── yaml_schedule_repository.py
│   │       │
│   │       └── infrastructure/
│   │           ├── di_container.py
│   │           ├── yaml_data_manager.py
│   │           └── config.py
│   │
│   ├── anti_corruption_layer/
│   │   ├── personal_to_work_adapter.py
│   │   └── work_to_personal_adapter.py
│   │
│   └── main.py  # エントリーポイント（統合DIコンテナ）
│
├── data/  # work_tasks用YAMLデータ
│   ├── config/
│   │   ├── staff.yaml
│   │   ├── task-types.yaml
│   │   └── schedule.yaml
│   ├── tasks/
│   │   ├── active/
│   │   └── archive/
│   └── reports/
│
└── claudedocs/
    ├── INTEGRATION_PLAN.md  # このファイル
    ├── PHASE1_MIGRATION.md  # Phase 1実装ガイド
    └── ARCHITECTURE.md      # アーキテクチャ詳細
```

---

## 🚀 段階的実装計画

### 開発方法論（Spec-Driven + TDD）

**全てのPhaseで以下のサイクルを遵守**：

```
Phase 1: Specify - ユーザーストーリー + 受け入れ基準
    ↓
Phase 2: Plan - 技術設計（アーキテクチャ・API・データモデル）
    ↓
Phase 3: Tasks - 実装タスク分解 + Definition of Done
    ↓
Phase 4: Implementation（各Task）
    1. 🔴 Red: Test作成
    2. 🟢 Green: 実装
    3. 🔵 Refactor: リファクタリング
    4. Commit（pre-commit自動テスト実行）
```

詳細は [DEVELOPMENT_PHILOSOPHY.md](./DEVELOPMENT_PHILOSOPHY.md) を参照。

---

### Phase 1: Context基盤構築（2-3日）

**目標**: 既存コードをBounded Context構造に分離

#### 開発フロー（Task単位）

各Taskは**Spec-Driven + TDD**の流れで進める：

1. **Spec確認** - Phase 1-3で定義された仕様・設計・タスクを確認
2. **Test作成** - `tests/unit/` または `tests/integration/` にテスト追加（🔴 Red）
3. **実装** - テストを通す（🟢 Green）
4. **Refactor** - コード改善（🔵 Refactor）
5. **Commit** - pre-commitでテスト自動実行

#### 1.1 Personal Tasks Context移行

##### Task 1.1.1: ディレクトリ構造作成

```bash
# 1. Usage: 理想的なディレクトリ構造をドキュメント化
# 2. Test: ディレクトリ存在確認テスト（オプション）
# 3. 実装: mkdir -p で構造作成
# 4. Commit
```

- [ ] `contexts/personal_tasks/` 配下の全ディレクトリ作成
- [ ] `tests/unit/`, `tests/integration/`, `tests/examples/` 作成

##### Task 1.1.2: Domainモデル移動 + テスト

```bash
# Spec-Driven + TDD フロー:
# 1. Spec確認: Phase 2（Plan）でTaskモデルの仕様を確認
# 2. 🔴 Red: tests/unit/domain/models/test_task.py 作成
# 3. 🟢 Green: src/domain/models/task.py → contexts/personal_tasks/domain/models/task.py
# 4. 🔵 Refactor: 必要に応じてリファクタリング
# 5. Commit
```

- [ ] Phase 2（Plan）のTaskモデル仕様を確認
- [ ] Unit Test作成（`tests/unit/domain/models/test_task.py`）
- [ ] `task.py`, `conversation.py` 移動・実装
- [ ] Commit: `feat(personal-tasks): Add Task domain model with TDD`

##### Task 1.1.3: Application層移動 + テスト

- [ ] Phase 2（Plan）のUse Case仕様を確認
- [ ] Unit Test作成（モックを使用）
- [ ] Use Caseファイル移動・実装
- [ ] Commit（Use Case単位）

##### Task 1.1.4: Adapters/Infrastructure層移動 + テスト

- [ ] Phase 2（Plan）のRepository仕様を確認
- [ ] Integration Test作成（実DB使用）
- [ ] ファイル移動・実装
- [ ] Commit

**成功基準**:
- v5.1.0と同じ動作（トークン消費量変わらず）
- 全テストパス（unit + integration）
- Pre-commit成功

#### 1.2 Shared Kernel抽出

##### Task 1.2.1: Value Objects抽出 + テスト

```bash
# Spec-Driven + TDD フロー:
# 1. Spec確認: Phase 2（Plan）のShared Kernel仕様を確認
# 2. 🔴 Red: tests/unit/shared_kernel/domain/test_value_objects.py 作成
# 3. 🟢 Green: UserId, TaskStatus 実装・抽出
# 4. 🔵 Refactor
# 5. Commit
```

- [ ] Phase 2（Plan）のShared Kernel仕様を確認
- [ ] Unit Test作成
- [ ] Value Objects実装・移動
- [ ] Commit: `feat(shared): Add shared value objects with TDD`

##### Task 1.2.2: Infrastructure抽出 + テスト

- [ ] Phase 2（Plan）のInfrastructure仕様を確認
- [ ] Unit Test作成（モック使用）
- [ ] ファイル移動・リファクタリング
- [ ] Commit: `feat(shared): Extract shared infrastructure`

**成功基準**:
- 既存機能が正常動作
- 全テストパス
- デプロイ成功

---

### Phase 2: Work Tasks Context実装（3-5日）

**目標**: staff-task-system機能を新Contextとして実装

**重要**: 全てのTaskでTDD+UDDサイクルを遵守（Usage → Test → Code → Commit）

#### 2.1 Domain層実装

##### Task 2.1.1: WorkTask集約ルート + テスト

```bash
# 1. Usage Example: tests/examples/usage_work_task_model.py
# 2. Test: tests/unit/work_tasks/domain/models/test_work_task.py
# 3. 実装: work_task.py
# 4. Commit
```

- [ ] Usage Example作成
- [ ] Unit Test作成
- [ ] WorkTaskモデル実装
- [ ] Commit: `feat(work-tasks): Add WorkTask domain model with UDD+TDD`

##### Task 2.1.2: Staff + Skill モデル + テスト

- [ ] Usage Example作成
- [ ] Unit Test作成
- [ ] Staff, Skillモデル実装
- [ ] Commit: `feat(work-tasks): Add Staff and Skill models with UDD+TDD`

##### Task 2.1.3: Repository インターフェース + テスト

- [ ] Usage Example作成
- [ ] Interface Test作成（実装は後で）
- [ ] Repository インターフェース定義
- [ ] Commit: `feat(work-tasks): Add repository interfaces`

##### Task 2.1.4: Domain Services + テスト

- [ ] Usage Example作成（AssignmentService）
- [ ] Unit Test作成
- [ ] スキルベース割り当てロジック実装
- [ ] Commit: `feat(work-tasks): Add assignment domain service with UDD+TDD`

**成功基準**:
- 全Domain層Unit Testパス
- Pydanticバリデーション成功

#### 2.2 Infrastructure層実装

- [ ] `work_tasks/infrastructure/` 作成
  - `yaml_data_manager.py`（YAMLファイルI/O）
  - `di_container.py`
- [ ] `work_tasks/adapters/secondary/` 実装
  - `yaml_work_task_repository.py`
  - `yaml_staff_repository.py`
  - `yaml_schedule_repository.py`

**成功基準**: YAMLファイル読み書き成功

#### 2.3 Application層実装

- [ ] `work_tasks/application/use_cases/` 実装
  - `create_work_task.py`
  - `assign_to_staff.py`
  - `complete_work_task.py`
  - `handle_absence.py`
  - `generate_daily_report.py`
- [ ] `work_tasks/application/dto/` 定義

**成功基準**: Use Case単体テスト成功

#### 2.4 Adapters層（CLI）実装

- [ ] `work_tasks/adapters/primary/cli/` 実装
  - `add_task.py`
  - `update_task.py`
  - `show_status.py`
  - その他19スクリプト移植

**成功基準**: staff-task-systemの全機能が動作

---

### Phase 3: Anti-Corruption Layer実装（2-3日）

**目標**: 2つのContextを相互運用可能にする

#### 3.1 変換アダプター実装

- [ ] `anti_corruption_layer/personal_to_work_adapter.py`
  - PersonalTask → WorkTask 変換
- [ ] `anti_corruption_layer/work_to_personal_adapter.py`
  - WorkTask → PersonalTask 変換（必要に応じて）

#### 3.2 統合Use Case実装

- [ ] `contexts/personal_tasks/application/use_cases/convert_to_work_task.py`
  - 「この個人タスクを業務タスクにする」機能
- [ ] Tool追加
  - `ConvertToWorkTaskTool`（AI Agent経由で実行）

**成功基準**:
- 「明日までにiPhone査定」→ Personal Task作成 → Work Task変換 → スタッフ割り当て
- 一連の流れが動作

---

### Phase 4: AI Agent統合（2-3日）

**目標**: 両ContextをAI Agentから操作可能にする

#### 4.1 Work Tasks用Tool実装

- [ ] `work_tasks/adapters/primary/tools/work_task_tools.py`
  - `CreateWorkTaskTool`
  - `AssignToStaffTool`
  - `CompleteWorkTaskTool`
  - `ShowStaffStatusTool`

#### 4.2 System Prompt統合

- [ ] `shared_kernel/infrastructure/prompt_templates.py` 更新
  - Personal Tasks用プロンプト
  - Work Tasks用プロンプト
  - 統合プロンプト（両方使用時）

#### 4.3 Slack Event Handler統合

- [ ] `contexts/personal_tasks/adapters/primary/slack_event_handler.py` 更新
  - Work Tasks用Toolも読み込み
  - Context判定ロジック追加

**成功基準**:
- Slackから「細谷さんに査定タスク追加して」で Work Task作成
- Slackから「明日までにレポート書く」で Personal Task作成
- AI Agentが自動判別して適切なContextのToolを呼び出す

---

### Phase 5: テスト・ドキュメント整備（2日）

#### 5.1 テスト追加

- [ ] Personal Tasks Context単体テスト
- [ ] Work Tasks Context単体テスト
- [ ] ACL統合テスト
- [ ] E2Eテスト（Slack Bot経由）

#### 5.2 ドキュメント更新

- [ ] `CLAUDE.md` 更新（新コマンド追加）
- [ ] `claudedocs/ARCHITECTURE.md` 詳細版作成
- [ ] `V6_MIGRATION_SUMMARY.md` 作成

#### 5.3 デプロイ

- [ ] NixOS設定更新（必要に応じて）
- [ ] 本番環境デプロイ
- [ ] 動作確認

**成功基準**: 全テストパス、ドキュメント完備、本番稼働

---

## 📊 見積もり

| Phase | 作業内容 | 見積もり日数 |
|-------|---------|------------|
| Phase 1 | Context基盤構築（リファクタリング） | 2-3日 |
| Phase 2 | Work Tasks Context実装 | 3-5日 |
| Phase 3 | Anti-Corruption Layer実装 | 2-3日 |
| Phase 4 | AI Agent統合 | 2-3日 |
| Phase 5 | テスト・ドキュメント整備 | 2日 |
| **合計** | | **11-16日** |

**リスク要因**:
- Phase 1のImport修正が予想以上に時間かかる可能性（+1-2日）
- YAML↔Pydanticバリデーション調整（+1日）
- AI Agentの自動判別ロジック調整（+1日）

**推奨スケジュール**: 3週間（余裕を持って）

---

## ⚠️ 重要な制約と注意事項

### 1. 既存機能の維持

- Phase 1完了後、nakamura-misaki v5.1.0の全機能が動作すること
- トークン消費量が増加しないこと（~1800 tokensを維持）

### 2. データ移行

- Personal Tasks: 既存PostgreSQLデータはそのまま使用（移行不要）
- Work Tasks: YAMLファイルベースで新規作成

### 3. Context独立性

- **Personal Tasks Context**は**Work Tasks Context**の存在を知らない（依存しない）
- 逆も同様
- 通訳は全て**Anti-Corruption Layer**経由

### 4. 依存性の方向

```
Adapters/Infrastructure
    ↓
Application
    ↓
Domain（誰にも依存しない）
```

この原則を**絶対に守る**。

### 5. Shared Kernelの最小化

Shared Kernelに入れるのは「本当に両Contextで共有すべきもの」だけ：
- ✅ `UserId`, `TaskStatus`（値オブジェクト）
- ✅ `ClaudeClient`, `SlackClient`（インフラ）
- ❌ `Task`モデル（各Contextで独自定義）
- ❌ ビジネスロジック

---

## 🔄 開発サイクルの実践

### Task開始前のチェックリスト

- [ ] DEVELOPMENT_PHILOSOPHY.mdを読んだ
- [ ] Usage Exampleを先に書く準備ができている
- [ ] テスト環境がセットアップ済み（`uv run pytest`が動く）
- [ ] Pre-commit hooksがインストール済み（`./scripts/setup-pre-commit.sh`）

### Commit前のチェックリスト

- [ ] Usage Exampleが書かれている（`tests/examples/`）
- [ ] Testが書かれている（`tests/unit/` or `tests/integration/`）
- [ ] 全テストが通る（`uv run pytest`）
- [ ] Lintエラーなし（`uv run ruff check`）
- [ ] 型チェックOK（`uv run mypy src/`）
- [ ] Commit messageが規約に従っている（`<type>(<scope>): <subject>`）

### 方針変更が必要な状況

以下の場合は**即座に作業を停止**し、報告する：

1. **アーキテクチャ違反を発見**
   - 例: Domain層がInfrastructure層に依存
   - 例: 新しいレイヤーを追加しようとしている

2. **ビジネスロジックの根本的変更が必要**
   - 例: TaskStatusの定義を変える必要がある

3. **実装の複雑度が予想を超える**
   - 例: 1 Taskが3日以上かかりそう

4. **Usage Exampleが自然に書けない**
   - 例: APIが複雑すぎて使用例が長くなる

→ **報告フォーマットは DEVELOPMENT_PHILOSOPHY.md を参照**

---

## 🎯 Phase 1詳細実装ガイド

Phase 1の具体的な手順は以下の通り：

### 実装の流れ（Task 1.1.2の例）

1. **Usage Example作成** (`tests/examples/usage_task_model.py`)
2. **Test作成** (`tests/unit/domain/models/test_task.py`) - 🔴 Red
3. **実装** (`contexts/personal_tasks/domain/models/task.py`) - 🟢 Green
4. **Refactor** - 🔵 Refactor
5. **Commit** - pre-commit自動実行

詳細なコード例は DEVELOPMENT_PHILOSOPHY.md の「実装例：Step 1.1.2のTDD+UDDフロー」を参照。

---

## 📚 参考資料

### アーキテクチャ原則
- Clean Architecture（Robert C. Martin）
- Domain-Driven Design（Eric Evans）
- Hexagonal Architecture（Alistair Cockburn）

### 既存ドキュメント
- [V5_MIGRATION_SUMMARY.md](./V5_MIGRATION_SUMMARY.md) - v5.0.0/v5.1.0の変更履歴
- [service-registry.md](../../claudedocs/service-registry.md) - NixOS統合環境の設計

### プロジェクトコンテキスト
- [lab-project/CLAUDE.md](../../CLAUDE.md) - Repository全体の制約
- [staff-task-system/README.md](../../../noguchisara-projects/work/staff-task-system/README.md) - Work Tasks仕様

---

**最終更新**: 2025-10-16
**作成者**: Claude Code
**バージョン**: v6.0.0-alpha
