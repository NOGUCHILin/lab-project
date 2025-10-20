# nakamura-misaki v5.0.0

**中村美咲 - 人格としてのタスク管理アシスタント**

**現在のバージョン**: v5.0.0 (Implementation Complete)
**前バージョン**: v4.0.0 (Deprecated)

---

> 📊 **進捗状況**: [`PROJECT_STATUS.md`](PROJECT_STATUS.md) で実装状況・次のアクションを確認してください

---

## 🎯 概要

nakamura-misakiは、**Slackチーム内でユーザーとして存在する人格**です。
Slackでの会話を通じてタスク管理を行い、Claudeを活用した自然言語理解により、柔軟で直感的なタスク操作を実現します。

**重要**: nakamura-misakiはBotではなく、Slack User Token (`xoxp-`) で動作する人格的アシスタントです。

### v5.0.0（実装完了）

- **自然言語駆動型**: Claude Tool Use APIによる柔軟なタスク理解
- **会話履歴保持**: 24時間TTLでコンテキストを保った対話
- **雑談対応**: タスク以外のメッセージにも自然に応答
- **7つのTool**: Task管理4個 + Handoff管理3個

**実装サマリー**: [V5_MIGRATION_SUMMARY.md](V5_MIGRATION_SUMMARY.md)
**移行計画**: [claudedocs/v5-migration-plan.md](claudedocs/v5-migration-plan.md)

---

## ✨ 主要機能

### v5.0.0

- 🤖 **自然言語理解**: 「明日までにレポート書く」でタスク登録
- 💭 **会話履歴**: 24時間TTLで前後の文脈を保持
- 🎨 **柔軟な表現**: 「あのレポート終わった」でタスク完了
- 😊 **雑談対応**: 「おはよう」「疲れた」にも自然に反応
- 🎯 **タスク管理**: 登録・一覧・更新・完了
- 🤝 **ハンドオフ**: チーム間でのタスク引き継ぎ
- 💬 **Slack統合**: Events APIでメッセージ受信
- 📊 **チーム機能**: タスク統計・ボトルネック検出
- 🔒 **セキュア**: sops-nixによる秘密情報管理

---

## 🏗️ 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|------|-----------|
| **言語** | Python | 3.12 |
| **Web Framework** | FastAPI | 0.115+ |
| **AI** | Claude 3.5 Sonnet | via Anthropic API |
| **Database** | PostgreSQL + pgvector | 16 |
| **ORM** | SQLAlchemy | 2.0 (async) |
| **Messaging** | Slack Events API | - |
| **Deployment** | NixOS + deploy-rs | - |
| **Secrets** | sops-nix | - |

---

## 📂 プロジェクト構造

```
nakamura-misaki/
├── src/
│   ├── adapters/              # アダプター層
│   │   ├── primary/           # 入力（REST API, Slack Webhook）
│   │   │   ├── api/           # FastAPI アプリケーション
│   │   │   │   ├── routes/    # エンドポイント定義
│   │   │   │   └── app.py     # Application Factory
│   │   │   └── slack_event_handler.py
│   │   └── secondary/         # 出力（DB, Slack API, Claude API）
│   │       └── repositories/  # PostgreSQL リポジトリ
│   ├── application/           # アプリケーション層
│   │   ├── dto/               # Data Transfer Objects
│   │   └── use_cases/         # ビジネスロジック
│   ├── domain/                # ドメイン層
│   │   ├── models/            # エンティティ
│   │   └── repositories/      # リポジトリインターフェース
│   └── infrastructure/        # インフラ層
│       ├── database/          # DB接続・スキーマ
│       └── di.py              # DI Container
├── admin-ui/                  # Admin Dashboard（Next.js）
├── alembic/                   # DBマイグレーション
├── docs/                      # アーキテクチャドキュメント
├── claudedocs/                # 開発計画・詳細資料
├── CLAUDE.md                  # プロジェクト指示書
└── README.md                  # このファイル
```

詳細なアーキテクチャ: [docs/ARCHITECTURE_V4.md](docs/ARCHITECTURE_V4.md)

---

## 🚀 起動方法

### 前提条件

- NixOS環境
- PostgreSQL 16 (pgvector拡張有効)
- Slack App設定済み（Events API, **User Token**）
- Anthropic API Key

### 環境変数

```bash
# sops-nix経由で管理（平文での保存禁止）
# 注: SLACK_BOT_TOKEN変数名だが、実際はUser Token (xoxp-) を使用
SLACK_BOT_TOKEN=xoxp-...  # User Token（人格として動作）
SLACK_SIGNING_SECRET=...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki
```

### ローカル開発

```bash
# プロジェクトルートで
cd nakamura-misaki

# 依存関係インストール
uv sync

# マイグレーション実行
uv run alembic upgrade head

# サーバー起動
uv run uvicorn src.adapters.primary.api.app:app --reload --port 10000
```

### 本番デプロイ

```bash
# mainブランチにpushで自動デプロイ
git push origin main

# デプロイ状況確認
gh run watch
```

NixOS設定: [`nixos-config/modules/services/registry/nakamura-misaki-api.nix`](../nixos-config/modules/services/registry/nakamura-misaki-api.nix)

---

## 🌐 API エンドポイント

### Slack Webhook

| Method | Path | 説明 |
|--------|------|------|
| POST | `/webhook/slack` | Slack Events受信 |

### REST API (Tasks)

| Method | Path | 説明 |
|--------|------|------|
| POST | `/api/tasks` | タスク作成 |
| GET | `/api/tasks` | タスク一覧（user_id, status指定可） |
| PATCH | `/api/tasks/{id}` | タスク更新 |
| POST | `/api/tasks/{id}/complete` | タスク完了 |

### REST API (Handoffs)

| Method | Path | 説明 |
|--------|------|------|
| POST | `/api/handoffs` | ハンドオフ作成 |
| GET | `/api/handoffs` | ハンドオフ一覧 |
| POST | `/api/handoffs/{id}/complete` | ハンドオフ完了 |

### Health Check

| Method | Path | 説明 |
|--------|------|------|
| GET | `/health` | サービス状態確認 |

**OpenAPI Docs**: `http://localhost:10000/docs`

---

## 💬 Slackでの使い方（v4.0.0）

### タスク操作コマンド

| 操作 | コマンド例 |
|-----|-----------|
| **登録** | `「レポート作成」をやる` |
| | `「会議資料」を明日までに実施` |
| **一覧** | `今日のタスク` |
| | `タスク一覧` |
| | `進行中のタスクを見せて` |
| **完了** | `タスク完了 <task-id>` |

### ハンドオフコマンド

| 操作 | コマンド例 |
|-----|-----------|
| **作成** | `<task-id>を<@U123456>に引き継ぎ「途中まで完了」` |
| **一覧** | `引き継ぎ一覧` |
| **完了** | `ハンドオフ完了 <handoff-id>` |

**注意**: v4.0.0はパターンマッチング方式のため、正確なコマンド形式が必要です。
v5.0.0では自然な会話でタスク操作が可能になる予定です。

---

## 📊 運用

### ログ確認

```bash
# 本番サーバーで
ssh home-lab-01
journalctl -u nakamura-misaki-api.service -f
```

### サービス状態確認

```bash
systemctl status nakamura-misaki-api.service
```

### Tailscale公開状態

```bash
tailscale funnel status
# Port 10000でFunnel公開中
```

---

## 🧪 テスト

### 手動テスト

```bash
# ヘルスチェック
curl http://localhost:10000/health

# タスク一覧（要user_id）
curl "http://localhost:10000/api/tasks?user_id=U5D0CJKMH"

# タスク作成
curl -X POST http://localhost:10000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U5D0CJKMH","title":"Test Task"}'
```

### 自動テスト（将来実装予定）

```bash
uv run pytest tests/
```

---

## 🗺️ ロードマップ

### v4.0.0（現行） ✅

- [x] Hexagonal Architecture実装
- [x] PostgreSQL + pgvector統合
- [x] Slack Events API統合
- [x] コマンドパーサー実装
- [x] Admin UI（Next.js）
- [x] 構造化ログ実装

### v5.0.0（計画中） 🚧

- [ ] Claude Agent SDK統合
- [ ] 会話履歴管理
- [ ] 自然言語タスク操作
- [ ] 雑談対応
- [ ] Tool Use実装

詳細: [claudedocs/v5-migration-plan.md](claudedocs/v5-migration-plan.md)

### v6.0.0（構想）

- [ ] マルチチャネル対応（Discord, LINE等）
- [ ] タスク自動優先度付け
- [ ] スマート通知（最適なタイミング）
- [ ] モバイルアプリ

---

## 📚 関連ドキュメント

| ドキュメント | 内容 |
|------------|------|
| [CLAUDE.md](CLAUDE.md) | プロジェクト開発指針 |
| [docs/ARCHITECTURE_V4.md](docs/ARCHITECTURE_V4.md) | v4.0.0アーキテクチャ詳細 |
| [claudedocs/v5-migration-plan.md](claudedocs/v5-migration-plan.md) | v5.0.0移行計画 |
| [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) | デプロイ手順 |

---

## 🤝 開発方針

### コード規約

- **命名**: snake_case（Python標準）
- **型ヒント**: 必須（mypy検査）
- **Docstring**: Google Style
- **フォーマット**: Black + isort

### アーキテクチャ原則

- **Hexagonal Architecture**: ドメイン層の独立性維持
- **DI Container**: 依存性注入パターン
- **Repository Pattern**: データアクセス抽象化
- **Use Case駆動**: ビジネスロジックの明確化

---

## 📄 ライセンス

MIT License

---

## 🙏 謝辞

- **mementomoris**: 元プロジェクト
- **Claude Code**: AI開発支援
- **Anthropic**: Claude API提供

---

Generated with [Claude Code](https://claude.com/claude-code)
