# Structure: nakamura-misaki Architecture

## Directory Structure

```
nakamura-misaki/
├── .kiro/
│   └── steering/           # Kiro仕様（このファイル）
│       ├── product.md      # プロダクトビジョン
│       ├── structure.md    # アーキテクチャ（このファイル）
│       └── tech.md         # 技術スタック
├── features/               # 機能ごとのKiro仕様
│   ├── phase-0-system-prompt/
│   ├── phase-1-database/
│   ├── phase-2-task-api/
│   ├── phase-3-handoff/
│   └── phase-4-team-hub/
├── config/
│   ├── prompts/            # システムプロンプト（JSON）
│   │   ├── default.json    # v4.0.0草薙素子風プロンプト
│   │   ├── technical.json  # 技術サポート用（非推奨）
│   │   └── schedule.json   # スケジュール管理用
│   └── settings.yaml       # アプリケーション設定
├── src/
│   ├── domain/             # ドメイン層（ビジネスロジック）
│   │   ├── models/         # エンティティ・値オブジェクト
│   │   ├── repositories/   # リポジトリインターフェース
│   │   └── services/       # ドメインサービス
│   ├── application/        # アプリケーション層（ユースケース）
│   │   ├── use_cases/      # ユースケース実装
│   │   └── dto/            # データ転送オブジェクト
│   ├── adapters/           # アダプター層（外部接続）
│   │   ├── primary/        # 入力アダプター（Slack, API）
│   │   └── secondary/      # 出力アダプター（Claude, DB, File）
│   └── infrastructure/     # インフラ層（起動・設定）
│       ├── main.py         # エントリーポイント
│       └── di.py           # 依存性注入
├── tests/
│   ├── unit/               # 単体テスト
│   ├── integration/        # 統合テスト
│   └── e2e/                # E2Eテスト
├── docs/
│   ├── PRESS_RELEASE.md    # Working Backwards
│   └── IMPLEMENTATION_PLAN.md
└── claudedocs/             # Claude Code用詳細ドキュメント
    ├── architecture.md     # アーキテクチャ詳細
    ├── deployment.md       # デプロイ手順
    └── troubleshooting.md  # トラブルシューティング
```

## Architectural Pattern: Hexagonal Architecture (Ports & Adapters)

### Core Principles

1. **依存性の方向**: 外側 → 内側（domain層への依存のみ）
2. **インターフェース分離**: Port（インターフェース）とAdapter（実装）を分離
3. **テスト容易性**: domain層は外部依存なしでテスト可能
4. **交換可能性**: Adapterは容易に交換可能（例: File → PostgreSQL）

### Layer Responsibilities

#### Domain Layer (`src/domain/`)
- **責務**: ビジネスロジック・ルールの定義
- **依存**: なし（純粋なPython）
- **例**:
  - `models/task.py`: タスクエンティティ（期限切れ判定ロジック含む）
  - `models/handoff.py`: ハンドオフエンティティ
  - `repositories/task_repository.py`: タスクリポジトリインターフェース
  - `services/task_service.py`: タスク管理ドメインサービス

#### Application Layer (`src/application/`)
- **責務**: ユースケースの実行・オーケストレーション
- **依存**: domain層のみ
- **例**:
  - `use_cases/register_task.py`: タスク登録ユースケース
  - `use_cases/query_today_tasks.py`: 今日のタスク取得ユースケース
  - `dto/task_dto.py`: タスクDTO

#### Adapters Layer (`src/adapters/`)

**Primary Adapters (入力)**:
- **責務**: 外部からの入力を受け取り、ユースケースを呼び出す
- **依存**: application層・domain層
- **例**:
  - `primary/slack_event_adapter.py`: Slackイベントハンドラー
  - `primary/api_adapter.py`: REST APIエンドポイント

**Secondary Adapters (出力)**:
- **責務**: domain層のインターフェースを実装し、外部リソースにアクセス
- **依存**: domain層（インターフェース実装）
- **例**:
  - `secondary/claude_adapter.py`: Claude API呼び出し
  - `secondary/task_repository_adapter.py`: PostgreSQLタスクリポジトリ実装
  - `secondary/prompt_repository_adapter.py`: JSONファイルプロンプトリポジトリ

#### Infrastructure Layer (`src/infrastructure/`)
- **責務**: アプリケーション起動・依存性注入・設定管理
- **依存**: 全層
- **例**:
  - `main.py`: FastAPIアプリケーション起動
  - `di.py`: 依存性注入コンテナ（Adapterのインスタンス化）

### Data Flow Example: "タスク登録"

```
1. User (Slack) → 2. Primary Adapter → 3. Use Case → 4. Domain Service → 5. Repository Interface → 6. Secondary Adapter → 7. PostgreSQL
                                                                                                    ↓
                                                                                            8. Claude Adapter → Claude API
```

**Detailed Steps**:
1. ユーザーがSlackで `@中村美咲 タスク登録: API統合 期限: 明日15時`
2. `SlackEventAdapter` がイベントを受信
3. `RegisterTaskUseCase` を呼び出し（DTOで渡す）
4. `TaskService` でバリデーション・ビジネスルール適用
5. `TaskRepository` インターフェース経由で保存
6. `PostgreSQLTaskRepositoryAdapter` が実際のDB操作
7. PostgreSQLにINSERT
8. `ClaudeAdapter` で確認メッセージ生成 → Slackに返信

## Naming Conventions

### Files
- Python: `snake_case.py`
- Config: `kebab-case.json`, `kebab-case.yaml`
- Docs: `UPPER_SNAKE_CASE.md` (重要ドキュメント), `kebab-case.md` (詳細ドキュメント)
- Kiro: `lowercase.md`

### Code
- Classes: `PascalCase`
- Functions/Methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Modules
- Domain Models: `{entity_name}.py` (例: `task.py`, `handoff.py`)
- Repositories: `{entity_name}_repository.py` (インターフェース), `{entity_name}_repository_adapter.py` (実装)
- Use Cases: `{verb}_{entity_name}.py` (例: `register_task.py`, `query_today_tasks.py`)
- Adapters: `{service_name}_adapter.py` (例: `claude_adapter.py`, `slack_event_adapter.py`)

## Design Constraints

### MUST Follow
1. **依存性の方向**: 必ず外側 → 内側（domain層は外部依存なし）
2. **インターフェース経由**: domain層からの外部アクセスは必ずインターフェース経由
3. **DTO使用**: Layer間のデータ受け渡しはDTOを使用（Entityを直接渡さない）
4. **非同期処理**: I/Oを伴う処理は必ず `async`/`await`
5. **型ヒント**: 全ての関数・メソッドに型ヒントを記述

### MUST NOT Do
1. ❌ domain層から外部ライブラリ（FastAPI, Slack SDK等）をimport
2. ❌ use_case層から直接DB・API操作（必ずrepository経由）
3. ❌ Entity/ValueObjectをJSONシリアライズ（DTO変換必須）
4. ❌ グローバル変数の使用（DIコンテナ経由）
5. ❌ Adapter層のビジネスロジック記述（domain層に移動）

## Testing Strategy

### Unit Tests (`tests/unit/`)
- **対象**: domain層・application層
- **モック**: 外部依存はモック（例: repository, claude_adapter）
- **カバレッジ目標**: 80%以上

### Integration Tests (`tests/integration/`)
- **対象**: Adapter層（実際のDB・API接続）
- **環境**: Docker Composeでテスト環境構築
- **データ**: テストデータは各テストでセットアップ・クリーンアップ

### E2E Tests (`tests/e2e/`)
- **対象**: Slack → nakamura-misaki → DB → Claude の全体フロー
- **環境**: テスト用Slackワークスペース
- **シナリオ**: 主要ユーザーストーリーをカバー

## Migration Strategy

### Phase 0 → Phase 1 (File → PostgreSQL)

**Before** (Phase 0):
- `JsonTaskRepository` (File-based)
- `JsonPromptRepository` (File-based)

**After** (Phase 1):
- `PostgreSQLTaskRepository` (DB-based)
- `JsonPromptRepository` (変更なし - v4.0ではプロンプトはJSONのまま)

**Migration Steps**:
1. PostgreSQLスキーマ作成
2. `PostgreSQLTaskRepository` 実装
3. `di.py` で `JsonTaskRepository` → `PostgreSQLTaskRepository` に切り替え
4. 既存ファイルデータをPostgreSQLにインポート
5. 動作確認後、ファイル削除

**Key Point**: インターフェース（`TaskRepository`）は変更なし → ビジネスロジックは無変更
