# nakamura-misaki 機能拡張実装計画（Phase 1-4）

**作成日**: 2025-10-26
**ステータス**: 🚧 Phase 1 実装中
**アーキテクチャ**: Hexagonal Architecture + DDD Bounded Context

---

## 🎯 目的

プレスリリース・ユースケースで謳われている機能を**アーキテクチャを壊さずに**実装する。

### 現状の課題
- チーム管理系機能が未実装（約40%）
- プロジェクト管理機能がない
- タスク依存関係管理がない
- リマインダー機能がない
- ボトルネック検出がない

---

## 🏗️ アーキテクチャ原則（厳守）

1. ✅ **新機能 = 新Bounded Context** - 既存Contextを肥大化させない
2. ✅ **Domain層の独立性** - 外部依存なし、純粋なビジネスロジック
3. ✅ **Repository Pattern** - DBアクセスは抽象化
4. ✅ **Tools層の薄さ** - Use Caseへの委譲のみ
5. ✅ **Context間通信はApplication層** - Domain層は他Contextを知らない

---

## 📋 新Bounded Context一覧

| # | Context名 | 責務 | Phase |
|---|----------|------|-------|
| 1 | Project Management | プロジェクト管理、進捗可視化 | Phase 1 |
| 2 | Task Dependencies | タスク依存関係、ブロッカー検出 | Phase 2 |
| 3 | Team Analytics | チーム統計、ボトルネック検出、日次レポート | Phase 3 |
| 4 | Notifications | リマインダー、通知管理 | Phase 4 |

---

## 📅 Phase 1: Project Management Context（2週間）

**目標**: プロジェクト管理の基礎実装

### 新テーブル

#### projects
```sql
CREATE TABLE projects (
    project_id      UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    owner_user_id   VARCHAR(100),
    deadline        TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP
);
```

#### project_tasks
```sql
CREATE TABLE project_tasks (
    id              UUID PRIMARY KEY,
    project_id      UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    task_id         UUID REFERENCES tasks(id) ON DELETE CASCADE,
    position        INTEGER,
    created_at      TIMESTAMP,
    UNIQUE (project_id, task_id)
);

CREATE INDEX idx_project_tasks_project ON project_tasks(project_id);
```

### ディレクトリ構造

```
src/contexts/project_management/
├── domain/
│   ├── entities/
│   │   ├── project.py              # Project Entity
│   │   └── project_task.py         # ProjectTask Entity
│   ├── repositories/
│   │   └── project_repository.py   # Interface
│   └── value_objects/
│       └── project_status.py       # ENUM: active, completed, archived
│
├── application/
│   ├── dto/
│   │   └── project_dto.py
│   └── use_cases/
│       ├── create_project.py
│       ├── add_task_to_project.py
│       ├── get_project_progress.py
│       └── archive_project.py
│
├── infrastructure/
│   └── repositories/
│       └── postgresql_project_repository.py
│
└── adapters/
    └── primary/
        └── tools/
            └── project_tools.py    # Claude Tool Use
```

### 新ツール

```python
- create_project(name, description, deadline, owner_user_id)
- add_task_to_project(project_id, task_id)
- remove_task_from_project(project_id, task_id)
- get_project_progress(project_id)
- list_projects(owner_user_id, status)
- archive_project(project_id)
```

### 実装チェックリスト

- [ ] Migration作成（002_add_project_management.py）
- [ ] Domain層実装
  - [ ] ProjectStatus Value Object
  - [ ] Project Entity
  - [ ] ProjectTask Entity
  - [ ] ProjectRepository Interface
- [ ] Infrastructure層実装
  - [ ] PostgreSQLProjectRepository
  - [ ] Schema定義（ProjectTable, ProjectTaskTable）
- [ ] Application層実装
  - [ ] ProjectDTO
  - [ ] CreateProjectUseCase
  - [ ] AddTaskToProjectUseCase
  - [ ] GetProjectProgressUseCase
  - [ ] ArchiveProjectUseCase
- [ ] Tools層実装
  - [ ] ProjectTools
- [ ] DIContainer統合
- [ ] SlackEventHandler統合
- [ ] テスト
  - [ ] Unit Tests（Domain, Use Cases）
  - [ ] Integration Tests（Repository）
  - [ ] Tool Tests

### 完了条件

- [ ] Claudeが「プロジェクト作ってタスク3つ追加して」で実行可能
- [ ] `get_project_progress()` で進捗率が正しく表示
- [ ] プロジェクトアーカイブが動作

---

## 📅 Phase 2: Task Dependencies Context（1週間）

**目標**: タスク依存関係管理

### 新テーブル

#### task_dependencies
```sql
CREATE TABLE task_dependencies (
    id                  UUID PRIMARY KEY,
    blocking_task_id    UUID REFERENCES tasks(id) ON DELETE CASCADE,
    blocked_task_id     UUID REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_type     VARCHAR(20) DEFAULT 'blocks',
    created_at          TIMESTAMP,
    UNIQUE (blocking_task_id, blocked_task_id),
    CHECK (blocking_task_id != blocked_task_id)
);

CREATE INDEX idx_dependencies_blocking ON task_dependencies(blocking_task_id);
CREATE INDEX idx_dependencies_blocked ON task_dependencies(blocked_task_id);
```

### 新ツール

```python
- add_task_dependency(blocking_task_id, blocked_task_id)
- remove_task_dependency(blocking_task_id, blocked_task_id)
- check_task_blockers(task_id)
- can_start_task(task_id)
- get_dependency_chain(task_id)
```

### 実装チェックリスト

- [ ] Migration作成（003_add_task_dependencies.py）
- [ ] Domain層実装
- [ ] Infrastructure層実装
- [ ] Application層実装
- [ ] Tools層実装
- [ ] DIContainer統合
- [ ] テスト

### 完了条件

- [ ] 「タスクAの後にタスクB」で依存関係設定可能
- [ ] ブロックされたタスク開始時に警告表示
- [ ] 依存関係の循環検出

---

## 📅 Phase 3: Team Analytics Context（2週間）

**目標**: チーム統計・ボトルネック検出

### 新テーブル

#### daily_summaries
```sql
CREATE TABLE daily_summaries (
    id                  UUID PRIMARY KEY,
    date                DATE NOT NULL,
    user_id             VARCHAR(100),
    tasks_completed     INTEGER DEFAULT 0,
    tasks_pending       INTEGER DEFAULT 0,
    summary_text        TEXT,
    created_at          TIMESTAMP,
    UNIQUE (date, user_id)
);

CREATE INDEX idx_daily_summaries_date ON daily_summaries(date);
CREATE INDEX idx_daily_summaries_user ON daily_summaries(user_id);
```

#### team_metrics
```sql
CREATE TABLE team_metrics (
    id              UUID PRIMARY KEY,
    date            DATE NOT NULL,
    metric_type     VARCHAR(50),
    metric_value    FLOAT,
    metadata        JSONB,
    created_at      TIMESTAMP
);

CREATE INDEX idx_team_metrics_date ON team_metrics(date);
CREATE INDEX idx_team_metrics_type ON team_metrics(metric_type);
```

### 新ツール

```python
- detect_bottleneck()
- get_team_workload()
- generate_daily_report(date)
- get_user_statistics(user_id)
- calculate_completion_rate(start_date, end_date)
```

### 実装チェックリスト

- [ ] Migration作成（004_add_team_analytics.py）
- [ ] Domain層実装（Domain Services含む）
- [ ] Infrastructure層実装
- [ ] Application層実装
- [ ] Tools層実装
- [ ] 定期実行スクリプト（cron job）
- [ ] DIContainer統合
- [ ] テスト

### 完了条件

- [ ] ボトルネック検出が動作（タスク10個以上のユーザー検出）
- [ ] 日次レポート自動生成
- [ ] チーム負荷可視化

---

## 📅 Phase 4: Notifications Context + 既存拡張（1週間）

**目標**: リマインダー・優先度管理

### 新テーブル

#### notifications
```sql
CREATE TABLE notifications (
    id                  UUID PRIMARY KEY,
    user_id             VARCHAR(100),
    notification_type   VARCHAR(50),
    task_id             UUID REFERENCES tasks(id) ON DELETE CASCADE,
    content             TEXT,
    sent_at             TIMESTAMP,
    read_at             TIMESTAMP,
    created_at          TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_sent ON notifications(sent_at);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
```

### tasks テーブル拡張
```sql
ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 5;
ALTER TABLE tasks ADD COLUMN progress_percent INTEGER DEFAULT 0
  CHECK (progress_percent >= 0 AND progress_percent <= 100);
ALTER TABLE tasks ADD COLUMN estimated_hours FLOAT;

CREATE INDEX idx_tasks_priority ON tasks(priority);
```

### 新ツール

```python
# Notifications Context
- send_reminder(task_id, message)
- get_overdue_tasks(user_id)
- get_due_soon_tasks(user_id, hours=24)
- mark_notification_read(notification_id)

# Personal Tasks Context拡張
- update_task_priority(task_id, priority)
- update_task_progress(task_id, progress_percent)
```

### 実装チェックリスト

- [ ] Migration作成（005_add_notifications.py, 006_extend_tasks_table.py）
- [ ] Domain層実装
- [ ] Infrastructure層実装
- [ ] Application層実装
- [ ] Tools層実装
- [ ] Personal Tasks Context拡張
- [ ] 定期実行スクリプト（リマインダー送信）
- [ ] DIContainer統合
- [ ] テスト

### 完了条件

- [ ] 期限24時間前にリマインダー送信
- [ ] 優先度順タスク表示
- [ ] 進捗率更新が動作

---

## 🧪 テスト戦略

### 各Phase共通
1. **Unit Tests**: Domain層・Use Case層（外部依存モック）
2. **Integration Tests**: Repository層（実DB使用）
3. **Tool Tests**: Tools層（Use Caseモック）
4. **E2E Tests**: Slack Event → Claude → Tool実行（最小限）

```bash
# Phaseごとにテスト実行
pytest tests/unit/contexts/project_management/
pytest tests/integration/contexts/project_management/
```

---

## 📦 DIContainer更新パターン

```python
# src/infrastructure/di.py

class DIContainer:
    def __init__(self, session: AsyncSession, slack_client: AsyncWebClient):
        self._session = session
        self._slack_client = slack_client

        # Phase 1追加
        self._project_repository = None

        # Phase 2追加
        self._dependency_repository = None

        # Phase 3追加
        self._analytics_repository = None

        # Phase 4追加
        self._notification_repository = None

    @property
    def project_repository(self):
        if self._project_repository is None:
            from src.contexts.project_management.infrastructure.repositories import (
                PostgreSQLProjectRepository
            )
            self._project_repository = PostgreSQLProjectRepository(self._session)
        return self._project_repository
```

---

## 🔄 Context間通信パターン

### ✅ 良い例: Application層でOrchestration

```python
class AddTaskToProjectUseCase:  # Project Management Context
    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository  # Personal Tasks Contextのリポジトリ
    ):
        self._project_repo = project_repository
        self._task_repo = task_repository

    async def execute(self, project_id: UUID, task_id: UUID):
        # 1. タスクの存在確認（Personal Tasks Context）
        task = await self._task_repo.find_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        # 2. プロジェクトに追加（Project Management Context）
        project = await self._project_repo.find_by_id(project_id)
        project.add_task_id(task_id)  # UUIDのみ保持
        await self._project_repo.save(project)
```

---

## 🎯 最終的なBounded Context構成

```
src/contexts/
├── personal_tasks/         # 既存（Phase 4で拡張）
├── conversations/          # 既存
├── workforce_management/   # 既存
├── handoffs/              # 既存（将来削除検討）
├── project_management/    # 新規 Phase 1 ✨
├── task_dependencies/     # 新規 Phase 2 ✨
├── team_analytics/        # 新規 Phase 3 ✨
└── notifications/         # 新規 Phase 4 ✨
```

---

## 📊 進捗トラッキング

| Phase | ステータス | 開始日 | 完了日 | 担当 |
|-------|-----------|--------|--------|------|
| Phase 1 | 🚧 実装中 | 2025-10-26 | - | Claude Code |
| Phase 2 | ⏸️ 未着手 | - | - | - |
| Phase 3 | ⏸️ 未着手 | - | - | - |
| Phase 4 | ⏸️ 未着手 | - | - | - |

---

## 📝 変更履歴

| 日付 | Phase | 変更内容 |
|------|-------|---------|
| 2025-10-26 | - | 初版作成 |

---

## 🔗 関連ドキュメント

- [CLAUDE.md](../CLAUDE.md) - プロジェクト概要
- [ARCHITECTURE_V4.md](../docs/ARCHITECTURE_V4.md) - アーキテクチャ詳細
- [PRESS_RELEASE.md](../docs/PRESS_RELEASE.md) - 機能仕様
