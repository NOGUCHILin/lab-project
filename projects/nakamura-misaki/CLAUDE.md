# nakamura-misaki Project

**中村美咲 - 人格としてのタスク管理アシスタント**

**現在**: v4.0.0 (Hexagonal Architecture + Command Parsers)
**次期**: v5.0.0 (Claude Agent SDK + Tool Use)

---

> ⚠️ **新規セッション開始時**: まず [`PROJECT_STATUS.md`](PROJECT_STATUS.md) で進捗状況を確認してください

---

## 🎯 プロジェクト概要

### 重要: 中村美咲は人格です

**中村美咲（なかむら みさき）**は、Slackチーム内で**ユーザーとして存在する人格**です。

- **Botではない**: Slack上でユーザーアカウントとして振る舞う
- **User Token使用**: Slack User Token (`xoxp-`) で動作
- **人格的な応答**: Botとしてではなく、チームメンバーとして自然に会話

### 目的

Slackでの会話を通じて、チームのタスク・ハンドオフを管理する**人格的アシスタント**

### コア技術

- **v4.0.0**: FastAPI + 正規表現パーサー + PostgreSQL
- **v5.0.0**: Claude Agent SDK + Tool Use + 会話履歴管理

### アーキテクチャスタイル

**Hexagonal Architecture (Ports & Adapters)**

```
Primary Adapters (REST API, Slack Webhook)
    ↓
Application Layer (Use Cases)
    ↓
Domain Layer (Entities, Repository Interfaces)
    ↓
Secondary Adapters (PostgreSQL, Slack API, Claude API)
```

---

## 📂 ディレクトリ構成

```
src/
├── adapters/
│   ├── primary/           # 入力アダプター
│   │   ├── api/           # FastAPI (routes/, app.py)
│   │   └── slack_event_handler.py
│   └── secondary/         # 出力アダプター
│       └── repositories/  # PostgreSQL
├── application/
│   ├── dto/               # Data Transfer Objects
│   └── use_cases/         # ビジネスロジック
├── domain/
│   ├── models/            # エンティティ
│   └── repositories/      # リポジトリインターフェース
└── infrastructure/
    ├── database/          # DB接続・スキーマ
    └── di.py              # DI Container
```

---

## 🚀 よく使うコマンド

### ローカル開発

```bash
# 依存関係インストール
uv sync

# マイグレーション実行
uv run alembic upgrade head

# サーバー起動（ホットリロード有効）
uv run uvicorn src.adapters.primary.api.app:app --reload --port 10000

# OpenAPI Docs
open http://localhost:10000/docs
```

### 本番デプロイ

```bash
# mainブランチにpushで自動デプロイ
git push origin main

# デプロイ状況確認
gh run watch

# 本番ログ確認
ssh home-lab-01
journalctl -u nakamura-misaki-api.service -f
```

### データベース操作

```bash
# マイグレーション作成
uv run alembic revision --autogenerate -m "Add new table"

# マイグレーション適用
uv run alembic upgrade head

# ロールバック
uv run alembic downgrade -1
```

---

## ⚠️ 重要な制約

### v4.0.0 固有

- **コマンド駆動**: 正規表現パターンマッチングが必要
  - 例: `「タスク名」をやる`（自然な会話は未対応）
- **パーサー依存**: `TaskCommandParser`, `HandoffCommandParser`が必須
- **応答フォーマッター**: 固定テンプレートによる応答生成

### v5.0.0 で解決予定

- 自然言語理解により、柔軟な表現に対応
- 会話履歴保持によるコンテキスト理解
- 雑談対応

### 共通制約

- **Hexagonal Architecture厳守**: ドメイン層は外部依存なし
- **秘密情報管理**: sops-nix経由でのみ管理（平文コミット禁止）
- **DI Container必須**: Use Case構築時は`DIContainer`経由

---

## 🏗️ 開発ガイドライン

### アーキテクチャ原則

1. **ドメイン層の独立性**: エンティティ・リポジトリインターフェースは外部依存なし
2. **Use Case駆動**: ビジネスロジックはUse Caseに集約
3. **Repository Pattern**: データアクセスは抽象化
4. **DI Container**: 依存性注入で疎結合を維持

### コード規約

- **命名**: snake_case（Python標準）
- **型ヒント**: 必須（mypy検査）
- **Docstring**: Google Style
- **フォーマット**: Black + isort
- **非同期**: async/await必須（FastAPI, SQLAlchemy 2.0）

### v5.0.0 開発方針

**削除対象**:
- `src/adapters/primary/task_command_parser.py`
- `src/adapters/primary/handoff_command_parser.py`
- `src/adapters/primary/task_response_formatter.py`
- `src/adapters/primary/handoff_response_formatter.py`

**新規追加**:
- `src/domain/services/conversation_manager.py`
- `src/domain/services/claude_agent_service.py`
- `src/adapters/primary/tools/` (Tool実装)
- `src/adapters/secondary/repositories/conversation_repository.py`

---

## 📚 ドキュメント

### プロジェクトルート

- `README.md`: プロジェクト概要・起動方法
- `CLAUDE.md`: このファイル（開発指針）

### docs/

- `ARCHITECTURE_V4.md`: v4.0.0アーキテクチャ詳細
- `DEPLOYMENT_GUIDE.md`: デプロイ手順

### claudedocs/

- `v5-migration-plan.md`: v5.0.0移行計画（詳細設計）

---

## 🧪 テスト方針（TDD必須）

### ⚠️ **重要: テスト駆動開発（TDD）を厳守**

**すべての新機能はTDDサイクルで実装する**:

1. **Red**: テストを書いて失敗させる
2. **Green**: 最小限の実装でテストを通す
3. **Refactor**: リファクタリング

### テスト構成

```
tests/
├── unit/               # ユニットテスト（外部依存なし）
│   └── contexts/
│       ├── personal_tasks/
│       ├── project_management/  # Phase 1
│       └── ...
├── integration/        # インテグレーションテスト（DB必須）
│   └── contexts/
└── e2e/               # E2Eテスト（API経由）
```

### pre-commit自動実行

すべてのコミット前に自動実行：
- `pytest-unit`: ユニットテスト（高速）
- `pytest-integration`: インテグレーションテスト（条件付き）

### 手動テスト（API検証用）

```bash
# ヘルスチェック
curl http://localhost:10000/health

# タスク一覧
curl "http://localhost:10000/api/tasks?user_id=U5D0CJKMH"

# タスク作成
curl -X POST http://localhost:10000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U5D0CJKMH","title":"Test Task"}'
```

**詳細**: [`claudedocs/testing-strategy.md`](claudedocs/testing-strategy.md)

---

## 🔐 秘密情報管理

### sops-nix経由

すべての秘密情報は `sops-nix` で暗号化して管理：

```bash
# 秘密情報編集（age鍵が必要）
sops nixos-config/secrets/nakamura-misaki.yaml
```

### 環境変数（NixOS経由で注入）

```nix
# nakamura-misaki-api.nix
ExecStart = pkgs.writeShellScript "start-nakamura-api" ''
  # 注: SLACK_BOT_TOKEN変数名だが、実際はUser Token (xoxp-) が設定される
  export SLACK_BOT_TOKEN=$(cat ${config.sops.secrets.slack_bot_token.path})  # User Token
  export SLACK_SIGNING_SECRET=$(cat ${config.sops.secrets.slack_signing_secret.path})
  export ANTHROPIC_API_KEY=$(cat ${config.sops.secrets.anthropic_api_key.path})
  export DATABASE_URL="postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki"
  # ...
'';
```

---

## 🚨 よくあるトラブル

### 1. マイグレーション失敗

**原因**: データベース接続エラー

**解決**:
```bash
# PostgreSQL起動確認
systemctl status postgresql.service

# データベース存在確認
psql -U nakamura_misaki -d nakamura_misaki -c "SELECT version();"
```

### 2. Slackイベント受信しない

**原因**: Tailscale Funnel設定ミス

**解決**:
```bash
# Funnel状態確認
tailscale funnel status

# 期待: Port 10000でFunnel公開中
```

### 3. ログが出ない

**原因**: `PYTHONUNBUFFERED=1`未設定

**解決**:
```bash
# NixOS設定で確認
grep PYTHONUNBUFFERED nixos-config/modules/services/registry/nakamura-misaki-api.nix
```

---

## 📖 参考資料

### 外部リンク

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Anthropic API](https://docs.anthropic.com/)
- [Slack Events API](https://api.slack.com/events-api)

### 内部ドキュメント

- v5.0.0移行計画: [`claudedocs/v5-migration-plan.md`](claudedocs/v5-migration-plan.md)
- アーキテクチャ詳細: [`docs/ARCHITECTURE_V4.md`](docs/ARCHITECTURE_V4.md)

---

最終更新: 2025-10-15（v5.0.0移行計画策定）
