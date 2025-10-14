# Tech: nakamura-misaki Technology Stack

## Core Technologies

### Programming Language
- **Python 3.12+**
  - Why: 豊富なライブラリ、非同期処理サポート、型ヒント
  - Package Manager: `uv` (高速依存管理)

### Web Framework
- **FastAPI 0.115+**
  - Why: 非同期サポート、自動APIドキュメント、型安全性
  - Use Cases:
    - Slack Event API受信
    - ヘルスチェックエンドポイント
    - Admin UI API（Phase 2以降）

### AI Model
- **Claude 3.5 Sonnet (via Claude Agent SDK)**
  - Why: 高度な推論能力、長いコンテキスト、日本語対応
  - SDK: `claude-agent-sdk` (Anthropic公式、旧claude-code-sdk)
  - API: Claude API v1

### Database
- **PostgreSQL 16+**
  - Why: ACID保証、JSON型サポート、拡張性
  - Extension: `pgvector` (ベクトル検索用)
  - Use Cases:
    - タスク管理（structured data）
    - ハンドオフ情報
    - ノート検索（vector search）

### Vector Database
- **pgvector (PostgreSQL extension)**
  - Why: PostgreSQL統合、追加サービス不要
  - Use Cases:
    - 過去のノートからの意味検索
    - 関連タスクの推薦
  - Note: Vector生成はClaude APIで実施（追加コストなし）

### Chat Platform
- **Slack API**
  - Authentication: User Token (xoxp-)
  - SDK: `slack-bolt` (Python)
  - APIs:
    - Events API: メッセージ受信
    - Web API: メッセージ送信、ユーザー情報取得

### Deployment
- **NixOS (Declarative Configuration)**
  - Why: 再現可能性、宣言的設定、バージョン管理
  - Service: systemd unit
  - Reverse Proxy: Tailscale Funnel (ポート10000)

### CI/CD
- **GitHub Actions**
  - Trigger: `main` ブランチへのpush
  - Steps:
    1. Linting (ruff)
    2. Type Check (pyright)
    3. Unit Tests (pytest)
    4. Deploy to NixOS (SSH経由)

## Libraries

### Core Dependencies

```toml
[dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = "^0.30.0"
slack-bolt = "^1.18.0"
claude-agent-sdk = "^1.0.0"     # Anthropic公式SDK（旧claude-code-sdk）
psycopg = {extras = ["binary", "pool"], version = "^3.2.0"}
sqlalchemy = "^2.0.0"
pgvector = "^0.3.0"
pydantic = "^2.9.0"
pydantic-settings = "^2.5.0"
python-dateutil = "^2.8.0"      # Phase 2: 日時解析用
```

### Development Dependencies

```toml
[dev-dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^5.0.0"
ruff = "^0.6.0"                 # Linter & Formatter
pyright = "^1.1.0"              # Type Checker
httpx = "^0.27.0"               # HTTP Client for Testing
```

## Environment Variables

### Required

```bash
# Slack
SLACK_BOT_TOKEN=xoxp-...        # User Token（必須）
SLACK_APP_TOKEN=xapp-...        # Socket Mode用（オプション）
SLACK_SIGNING_SECRET=...        # Event API検証用

# Claude
ANTHROPIC_API_KEY=sk-ant-...    # Claude API Key

# Database (Phase 1以降)
DATABASE_URL=postgresql://user:pass@host:5432/nakamura_misaki

# Application
WORKSPACE_PATH=/path/to/workspace
PROMPTS_DIR=/path/to/config/prompts
LOG_LEVEL=INFO
```

## Technical Constraints

### Performance
- **Response Time**: 5秒以内にSlack返信（Claude API呼び出し含む）
- **Concurrent Requests**: 10リクエスト/秒まで対応
- **Database Connections**: Pool size 10-20

### Security
- **Secrets Management**: sops-nix経由で暗号化（NixOS環境）
- **API Authentication**: Slack Signing Secret検証必須
- **User Token**: 適切なスコープ設定（`chat:write`, `users:read`, `channels:history`）

### Scalability
- **Phase 0-1**: Single Server（NixOS）
- **Phase 2以降**: Horizontal Scaling検討（複数インスタンス + Load Balancer）

### Reliability
- **Error Handling**: 全ての外部API呼び出しでリトライ機構
- **Logging**: 構造化ログ（JSON形式）
- **Health Check**: `/health` エンドポイント（DB接続確認含む）
- **Monitoring**: systemd journalctl + Tailscale status

## Development Tools

### Code Quality
- **Formatter**: ruff (Black互換)
- **Linter**: ruff (Flake8互換 + 追加ルール)
- **Type Checker**: pyright (VSCode統合)

### Testing
- **Test Framework**: pytest
- **Coverage**: pytest-cov (目標: 80%以上)
- **Async Testing**: pytest-asyncio

### Local Development
```bash
# 仮想環境セットアップ
uv venv
source .venv/bin/activate

# 依存関係インストール
uv pip install -e ".[dev]"

# 開発サーバー起動
uv run uvicorn src.infrastructure.main:app --reload --port 8000

# テスト実行
uv run pytest tests/

# 型チェック
uv run pyright src/

# Linting
uv run ruff check src/
```

## External Services

### Anthropic Claude API
- **Endpoint**: `https://api.anthropic.com/v1/messages`
- **Model**: `claude-3-5-sonnet-20241022`
- **Max Tokens**: 8192 (output)
- **Temperature**: 0.7 (デフォルト)

### Slack API
- **Base URL**: `https://slack.com/api/`
- **Rate Limits**:
  - Tier 3: 50+ requests/minute
  - Tier 4: 100+ requests/minute
- **Socket Mode**: オプション（Event API代替）


## Architecture Decisions (ADRs)

### ADR-001: Why Claude 3.5 Sonnet?
- **Context**: AI modelの選定
- **Decision**: Claude 3.5 Sonnet
- **Rationale**:
  - 高度な推論能力（タスク理解・意図解釈）
  - 長いコンテキスト（200K tokens）
  - 日本語対応（草薙素子風の性格表現）
  - Anthropic Context Engineering対応
- **Alternatives**: GPT-4, Gemini Pro
- **Status**: Accepted

### ADR-002: Why PostgreSQL + pgvector?
- **Context**: データストア選定
- **Decision**: PostgreSQL 16 + pgvector
- **Rationale**:
  - Structured data (タスク) + Vector search (ノート) を統合
  - ACID保証（タスク管理で重要）
  - 運用実績豊富
  - Supabase対応
- **Alternatives**: MongoDB + Pinecone, Separate DBs
- **Status**: Accepted

### ADR-003: Why User Token (not Bot Token)?
- **Context**: Slack認証方式
- **Decision**: User Token (xoxp-)
- **Rationale**:
  - 人間の従業員と同じ権限で動作
  - DM・チャンネルで区別なく動作
  - "Bot"アイコンが表示されない
- **Tradeoffs**: セキュリティリスク（Tokenの厳重管理必要）
- **Status**: Accepted

### ADR-004: Why Hexagonal Architecture?
- **Context**: アーキテクチャパターン選定
- **Decision**: Hexagonal Architecture (Ports & Adapters)
- **Rationale**:
  - ビジネスロジックの独立性
  - テスト容易性（外部依存なし）
  - Adapter交換容易性（File → DB移行）
- **Alternatives**: Layered Architecture, Clean Architecture
- **Status**: Accepted

### ADR-005: Why Kiro Specification-First?
- **Context**: 開発方法論
- **Decision**: AWS Kiro Specification-First Development
- **Rationale**:
  - 仕様を先に書くことで認識齟齬を防ぐ
  - AI生成コードの品質向上
  - ドキュメントが常に最新
- **Alternatives**: TDD, BDD
- **Status**: Accepted
