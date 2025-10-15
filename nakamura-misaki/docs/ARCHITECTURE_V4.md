# nakamura-misaki v4.0.0 - Architecture Documentation

**最終更新**: 2025-10-15
**ステータス**: ✅ Production Ready

---

## 🏗️ アーキテクチャスタイル

### Hexagonal Architecture (Ports & Adapters)

nakamura-misaki は **Hexagonal Architecture** を採用し、ビジネスロジックを外部依存から完全に分離しています。

```
┌─────────────────────────────────────────────────────────┐
│                    Primary Adapters                     │
│  (入力: ユーザーからのリクエストを受け付ける)              │
├─────────────────────────────────────────────────────────┤
│  ┌─ REST API (/api/*)                                   │
│  │   - GET /api/tasks (タスク一覧)                       │
│  │   - POST /api/tasks (タスク作成)                      │
│  │   - PATCH /api/tasks/{id} (タスク更新)               │
│  │   - POST /api/tasks/{id}/complete (タスク完了)       │
│  │   - GET /api/handoffs (ハンドオフ一覧)               │
│  │   - POST /api/handoffs (ハンドオフ作成)              │
│  │   - GET /api/team/tasks (チームタスク)               │
│  │   - GET /api/team/stats (チーム統計)                 │
│  │                                                       │
│  ┌─ Slack Events (/webhook/slack)                       │
│  │   - POST /webhook/slack (Slack Events API)          │
│  │   - URL Verification                                 │
│  │   - Message Events                                   │
│  │                                                       │
│  └─ Admin UI (/admin)                                   │
│      - GET /admin (Dashboard)                           │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│  (ビジネスロジック: Use Cases + DTOs)                    │
├─────────────────────────────────────────────────────────┤
│  Task Use Cases:                                        │
│    - RegisterTaskUseCase                                │
│    - QueryTodayTasksUseCase                             │
│    - QueryUserTasksUseCase                              │
│    - CompleteTaskUseCase                                │
│    - UpdateTaskUseCase                                  │
│                                                         │
│  Handoff Use Cases:                                     │
│    - RegisterHandoffUseCase                             │
│    - QueryHandoffsByUserUseCase                         │
│    - CompleteHandoffUseCase                             │
│    - SendHandoffReminderUseCase                         │
│                                                         │
│  Team Use Cases:                                        │
│    - DetectBottleneckUseCase                            │
│    - QueryTeamStatsUseCase                              │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     Domain Layer                        │
│  (エンティティ + リポジトリインターフェース)              │
├─────────────────────────────────────────────────────────┤
│  Entities:                                              │
│    - Task (タスクエンティティ)                          │
│    - Handoff (ハンドオフエンティティ)                   │
│    - Note (ノートエンティティ + pgvector)               │
│    - Session (セッションエンティティ)                   │
│                                                         │
│  Repository Interfaces (Ports):                         │
│    - TaskRepository                                     │
│    - HandoffRepository                                  │
│    - NoteRepository                                     │
│    - SessionRepository                                  │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Secondary Adapters                    │
│  (出力: 外部システムへアクセスする)                      │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL Adapters:                                   │
│    - PostgreSQLTaskRepository                           │
│    - PostgreSQLHandoffRepository                        │
│    - PostgreSQLNoteRepository                           │
│                                                         │
│  External API Adapters:                                 │
│    - SlackAdapter (Slack API Client)                    │
│    - ClaudeAdapter (Anthropic API Client)               │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 ディレクトリ構成

```
src/
├── adapters/                # アダプター層
│   ├── primary/             # 入力アダプター
│   │   ├── api/             # FastAPI ルーティング（新設計）
│   │   │   ├── __init__.py
│   │   │   ├── app.py       # Application Factory
│   │   │   ├── dependencies.py  # DI設定
│   │   │   └── routes/
│   │   │       ├── slack.py       # /webhook/slack
│   │   │       ├── tasks.py       # /api/tasks
│   │   │       ├── handoffs.py    # /api/handoffs
│   │   │       ├── team.py        # /api/team
│   │   │       └── admin.py       # /admin
│   │   ├── api.py           # 後方互換エントリーポイント
│   │   ├── slack_event_handler.py
│   │   ├── task_command_parser.py
│   │   ├── task_response_formatter.py
│   │   ├── handoff_command_parser.py
│   │   └── handoff_response_formatter.py
│   └── secondary/           # 出力アダプター
│       ├── postgresql_task_repository.py
│       ├── postgresql_handoff_repository.py
│       ├── postgresql_note_repository.py
│       ├── slack_adapter.py
│       └── claude_adapter.py
│
├── application/             # アプリケーション層
│   ├── dto/
│   │   ├── task_dto.py
│   │   └── handoff_dto.py
│   └── use_cases/
│       ├── register_task.py
│       ├── query_today_tasks.py
│       ├── complete_task.py
│       ├── update_task.py
│       ├── register_handoff.py
│       ├── query_handoffs_by_user.py
│       ├── complete_handoff.py
│       ├── send_handoff_reminder.py
│       ├── detect_bottleneck.py
│       └── query_team_stats.py
│
├── domain/                  # ドメイン層
│   ├── models/
│   │   ├── task.py
│   │   ├── handoff.py
│   │   ├── note.py
│   │   └── session.py
│   └── repositories/
│       ├── task_repository.py
│       ├── handoff_repository.py
│       ├── note_repository.py
│       └── session_repository.py
│
└── infrastructure/          # インフラ層
    ├── database/
    │   ├── schema.py        # SQLAlchemy Models
    │   └── manager.py       # DB接続管理
    └── di.py                # DI Container
```

---

## 🌐 API エンドポイント設計

### 1. Slack Events API

| Method | Path | 目的 | 実装 |
|--------|------|------|------|
| POST | `/webhook/slack` | Slack Events受信 | ✅ [routes/slack.py](../src/adapters/primary/api/routes/slack.py) |

**重要**: `/slack/events` から `/webhook/slack` に変更（Tailscale Funnel設定と統一）

### 2. REST API (Tasks)

| Method | Path | 目的 | 実装 |
|--------|------|------|------|
| POST | `/api/tasks` | タスク作成 | ✅ [routes/tasks.py](../src/adapters/primary/api/routes/tasks.py) |
| GET | `/api/tasks` | タスク一覧 | ✅ [routes/tasks.py](../src/adapters/primary/api/routes/tasks.py) |
| GET | `/api/tasks/{id}` | タスク取得 | 🚧 未実装 |
| PATCH | `/api/tasks/{id}` | タスク更新 | ✅ [routes/tasks.py](../src/adapters/primary/api/routes/tasks.py) |
| POST | `/api/tasks/{id}/complete` | タスク完了 | ✅ [routes/tasks.py](../src/adapters/primary/api/routes/tasks.py) |

### 3. REST API (Handoffs)

| Method | Path | 目的 | 実装 |
|--------|------|------|------|
| POST | `/api/handoffs` | ハンドオフ作成 | ✅ [routes/handoffs.py](../src/adapters/primary/api/routes/handoffs.py) |
| GET | `/api/handoffs` | ハンドオフ一覧 | ✅ [routes/handoffs.py](../src/adapters/primary/api/routes/handoffs.py) |
| POST | `/api/handoffs/{id}/complete` | ハンドオフ完了 | ✅ [routes/handoffs.py](../src/adapters/primary/api/routes/handoffs.py) |

### 4. REST API (Team)

| Method | Path | 目的 | 実装 |
|--------|------|------|------|
| GET | `/api/team/tasks` | チーム全体タスク | 🚧 未実装 |
| GET | `/api/team/stats` | チーム統計 | 🚧 未実装 |
| GET | `/api/team/bottlenecks` | ボトルネック検出 | 🚧 未実装 |

### 5. Admin UI

| Method | Path | 目的 | 実装 |
|--------|------|------|------|
| GET | `/admin` | Admin Dashboard | 🚧 未実装 |

### 6. Health Check

| Method | Path | 目的 | 実装 |
|--------|------|------|------|
| GET | `/health` | ヘルスチェック | ✅ [app.py](../src/adapters/primary/api/app.py) |

---

## 🔄 データフロー

### Slack メッセージ受信フロー

```
1. Slack Events API
   ↓ POST /webhook/slack
2. routes/slack.py
   ↓ 署名検証
3. SlackEventHandler
   ↓ コマンド解析
4. TaskCommandParser / HandoffCommandParser
   ↓ DTO作成
5. RegisterTaskUseCase / RegisterHandoffUseCase
   ↓ Repository経由
6. PostgreSQLTaskRepository
   ↓ DB書き込み
7. Slack API
   ↓ 応答メッセージ送信
8. User
```

### REST API フロー

```
1. HTTP Client (curl, Postman, etc.)
   ↓ GET /api/tasks?user_id=U123
2. routes/tasks.py
   ↓ DI経由でセッション取得
3. QueryTodayTasksUseCase
   ↓ Repository経由
4. PostgreSQLTaskRepository
   ↓ SELECT * FROM tasks
5. Task Entity
   ↓ DTO変換
6. TaskResponse (JSON)
   ↓ HTTP 200 OK
7. HTTP Client
```

---

## 🧪 テスト戦略

### Unit Tests

| レイヤー | テスト対象 | 場所 |
|---------|----------|------|
| Domain | Entity + Business Logic | `tests/unit/domain/` |
| Application | Use Cases | `tests/unit/application/` |
| Adapters | Command Parsers | `tests/unit/adapters/` |

### Integration Tests

| テスト対象 | 場所 |
|-----------|------|
| Repository + Database | `tests/integration/repositories/` |
| API Endpoints | `tests/integration/api/` |

### E2E Tests

| テスト対象 | 場所 |
|-----------|------|
| Slack Events + Database + API | `tests/e2e/` |

---

## 🔧 依存性注入 (DI)

### DIContainer ([infrastructure/di.py](../src/infrastructure/di.py))

```python
class DIContainer:
    def __init__(
        self,
        session: AsyncSession,
        claude_client: Anthropic,
        slack_client: AsyncWebClient
    ):
        self._session = session
        self._claude_client = claude_client
        self._slack_client = slack_client

    def build_register_task_use_case(self) -> RegisterTaskUseCase:
        repo = PostgreSQLTaskRepository(self._session)
        return RegisterTaskUseCase(repo)

    # ... 他のUse Caseも同様
```

### FastAPI Dependency ([api/dependencies.py](../src/adapters/primary/api/dependencies.py))

```python
async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = request.app.state.async_session_maker
    async with async_session_maker() as session:
        yield session
```

---

## 📊 実装完了状況

### ✅ 完全実装

- Domain Layer (100%)
- Application Layer Use Cases (100%)
- PostgreSQL Repositories (100%)
- Slack Event Handler (100%)
- REST API (Tasks) (80% - GET /{id} 未実装)
- REST API (Handoffs) (100%)

### 🚧 部分実装

- REST API (Team) (0% - スケルトンのみ)
- Admin UI (0% - スケルトンのみ)

### 🎯 次のステップ

1. **Team Use Cases の実装** (`DetectBottleneckUseCase`, `QueryTeamStatsUseCase`)
2. **Admin UI の実装** (Jinja2 + Tailwind CSS)
3. **E2E テストの追加**

---

Generated with [Claude Code](https://claude.com/claude-code)
