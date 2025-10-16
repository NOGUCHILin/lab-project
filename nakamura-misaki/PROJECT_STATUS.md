# nakamura-misaki - Project Status

**最終更新**: 2025-10-16
**現在のバージョン**: v5.0.0 (Production)
**次期バージョン**: v6.0.0 (Planning Phase)

---

## 🎯 プロジェクト概要

**nakamura-misaki**は、Slackでの会話を通じてタスク管理を行うAIアシスタントです。

### 現在の状態（v5.0.0）

- ✅ **本番稼働中**（NixOS環境、Tailscale Funnel経由で公開）
- ✅ 自然言語駆動型タスク管理（Claude Tool Use API）
- ✅ 会話履歴管理（24時間TTL、PostgreSQL）
- ✅ 雑談対応（タスク以外のメッセージにも応答）
- ✅ Hexagonal Architecture実装
- ✅ PostgreSQL + pgvector統合
- ✅ Slack Events API統合
- ✅ 構造化ログ実装

### 次のステップ（v6.0.0）

- 📋 **構想フェーズ**
- 🎯 マルチチャネル対応（Discord, LINE等）
- 🎯 タスク自動優先度付け
- 🎯 スマート通知（最適なタイミング）

---

## 📊 実装状況

### v5.0.0（現行バージョン）

| 機能 | ステータス | 最終更新 |
|-----|----------|---------|
| **Claude Tool Use API統合** | ✅ 完了 | 2025-10-16 |
| **会話履歴管理** | ✅ 完了 | 2025-10-16 |
| **自然言語タスク操作** | ✅ 完了 | 2025-10-16 |
| **Task Tools（4個）** | ✅ 完了 | 2025-10-16 |
| **Handoff Tools（3個）** | ✅ 完了 | 2025-10-16 |
| **Domain Layer** | ✅ 完了 | 2025-10-14 |
| **Application Layer** | ✅ 完了 | 2025-10-14 |
| **PostgreSQL Repositories** | ✅ 完了 | 2025-10-14 |
| **Slack Event Handler V5** | ✅ 完了 | 2025-10-16 |
| **REST API (Tasks)** | ✅ 完了 | 2025-10-14 |
| **REST API (Handoffs)** | ✅ 完了 | 2025-10-14 |
| **構造化ログ** | ✅ 完了 | 2025-10-15 |
| **Admin UI** | 🚧 部分実装 | - |
| **Team Use Cases** | 🚧 スケルトンのみ | - |

**本番環境**: ✅ 稼働中
- URL: `https://<tailscale-hostname>:10000/webhook/slack`
- サービス: `nakamura-misaki-api.service` (v5.0.0)
- ログレベル: INFO

---

### v6.0.0（構想段階）

今後の機能拡張候補：

- タスク依存関係管理
- サブタスク機能
- 定期タスク（Recurrence）
- チームダッシュボード完成
- マルチチャネル対応（Discord, LINE）
- ベクトル検索活用（類似タスク提案）

**詳細**: 今後策定予定

---

## 🗂️ ドキュメント構成

### 必読（新規セッション開始時）

1. **[README.md](README.md)** - プロジェクト概要、起動方法、技術スタック
2. **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - このファイル（進捗状況）
3. **[CLAUDE.md](CLAUDE.md)** - 開発ガイドライン、重要な制約

### アーキテクチャ

- **[docs/ARCHITECTURE_V4.md](docs/ARCHITECTURE_V4.md)** - v4.0.0詳細設計（現行）
- **[claudedocs/v5-migration-plan.md](claudedocs/v5-migration-plan.md)** - v5.0.0移行計画（次期）

### 実装記録

- **[docs/REFACTORING_SUMMARY_2025-10-15.md](docs/REFACTORING_SUMMARY_2025-10-15.md)** - v4.0.0リファクタリング記録
- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - デプロイ手順

---

## 🚀 最近の変更履歴

### 2025-10-16

**v5.0.0本番リリース完了**

- ✅ Claude Tool Use API統合（自然言語タスク操作）
- ✅ 会話履歴管理実装（PostgreSQL、24時間TTL）
- ✅ Task Tools実装（register, list, update, complete）
- ✅ Handoff Tools実装（create, list, complete）
- ✅ SlackEventHandlerV5統合
- ✅ 本番環境デプロイ・動作確認完了
- ✅ バックグラウンド処理実装（Slack retryバグ対策）
- ✅ Bot自身のメッセージ無視（無限ループ対策）

**主要コミット**:
- `a6e3f06`: v5.0.0実装（Claude Tool Use API）
- `bc2bb14`: Slackメッセージをバックグラウンド処理化
- `12edd4a`: Bot自身のメッセージを無視

### 2025-10-15

**構造化ログ実装完了**

- ✅ 全APIルート（slack, tasks, handoffs）にログ追加
- ✅ app.pyでログレベル設定（環境変数`LOG_LEVEL`）
- ✅ NixOS設定に`PYTHONUNBUFFERED=1`追加

### 2025-10-14

**v4.0.0アーキテクチャリファクタリング完了**

- ✅ Hexagonal Architecture実装
- ✅ FastAPI Application Factory導入
- ✅ routes/フォルダ分割（slack, tasks, handoffs, team, admin）

---

## 🔍 現在の技術スタック

### Backend

- **Python**: 3.12
- **Web Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 16 + pgvector
- **AI**: Anthropic Claude 3.5 Sonnet

### Infrastructure

- **Deployment**: NixOS + deploy-rs
- **Secrets Management**: sops-nix
- **Reverse Proxy**: Tailscale Funnel (Port 10000)
- **Service Manager**: systemd

### External APIs

- **Slack**: Events API + Bot Token (xoxb-)
- **Claude**: Anthropic API (Messages API)

---

## 📂 ディレクトリ構成

```
nakamura-misaki/
├── src/
│   ├── adapters/
│   │   ├── primary/
│   │   │   ├── api/               # FastAPI (v4.0.0)
│   │   │   │   ├── routes/        # エンドポイント
│   │   │   │   └── app.py         # Application Factory
│   │   │   ├── tools/             # (v5.0.0予定)
│   │   │   ├── slack_event_handler.py
│   │   │   ├── task_command_parser.py      # v5.0.0で削除予定
│   │   │   ├── handoff_command_parser.py   # v5.0.0で削除予定
│   │   │   ├── task_response_formatter.py  # v5.0.0で削除予定
│   │   │   └── handoff_response_formatter.py # v5.0.0で削除予定
│   │   └── secondary/
│   │       └── repositories/      # PostgreSQL
│   ├── application/
│   │   ├── dto/
│   │   └── use_cases/             # ビジネスロジック
│   ├── domain/
│   │   ├── models/                # エンティティ
│   │   ├── repositories/          # インターフェース
│   │   └── services/              # (v5.0.0で追加予定)
│   └── infrastructure/
│       ├── database/
│       └── di.py
├── alembic/                       # DBマイグレーション
├── admin-ui/                      # Next.js (部分実装)
├── docs/                          # アーキテクチャ・実装記録
├── claudedocs/                    # 詳細計画
├── README.md
├── CLAUDE.md
└── PROJECT_STATUS.md              # このファイル
```

---

## 🎯 v5.0.0 実装計画（概要）

### Phase 1: 基盤構築

**目的**: 会話履歴管理のためのDBテーブル・リポジトリ作成

**タスク**:
- [ ] `conversations`テーブル作成（Alembicマイグレーション）
- [ ] `Conversation`エンティティ作成
- [ ] `ConversationRepository`実装
- [ ] `ConversationManager`ドメインサービス実装

**成果物**:
```
alembic/versions/xxx_add_conversations_table.py
src/domain/entities/conversation.py
src/adapters/secondary/repositories/conversation_repository.py
src/domain/services/conversation_manager.py
```

---

### Phase 2: Tool実装

**目的**: Claude Tool Useで呼び出すタスク操作Toolを実装

**タスク**:
- [ ] `BaseTool`抽象クラス作成
- [ ] `TaskTools`実装（register, list, complete, update）
- [ ] `HandoffTools`実装（create, list, complete）
- [ ] `ContextTools`実装（get_current_context）

**成果物**:
```
src/adapters/primary/tools/base_tool.py
src/adapters/primary/tools/task_tools.py
src/adapters/primary/tools/handoff_tools.py
src/adapters/primary/tools/context_tools.py
```

---

### Phase 3: Claude Agent Service

**目的**: Claude Messages API + Tool Useの統合

**タスク**:
- [ ] `ClaudeAgentService`作成
- [ ] Tool Use APIラッパー実装
- [ ] System Prompt管理
- [ ] Tool呼び出しディスパッチャー実装

**成果物**:
```
src/domain/services/claude_agent_service.py
```

---

### Phase 4: SlackEventHandler統合

**目的**: 既存のSlackEventHandlerをClaude Agent Service経由に変更

**タスク**:
- [ ] SlackEventHandlerリファクタリング
- [ ] ConversationManager統合
- [ ] ClaudeAgentService統合
- [ ] パーサー・フォーマッター削除

**削除するファイル**:
```
src/adapters/primary/task_command_parser.py
src/adapters/primary/handoff_command_parser.py
src/adapters/primary/task_response_formatter.py
src/adapters/primary/handoff_response_formatter.py
```

---

### Phase 5-8

- **Phase 5**: REST API見直し（必要性判断）
- **Phase 6**: 環境変数・NixOS設定更新
- **Phase 7**: ログ・モニタリング強化
- **Phase 8**: テスト・検証（5つのシナリオ）

**詳細**: [`claudedocs/v5-migration-plan.md`](claudedocs/v5-migration-plan.md)

---

## 🚨 重要な注意事項

### 新規セッション開始時のチェックリスト

1. **現在のバージョン確認**: v5.0.0（本番稼働中）
2. **次期バージョン**: v6.0.0（構想段階）
3. **実装状況**: v5.0.0完了、本番環境で稼働中
4. **最後のデプロイ**: 2025-10-16（v5.0.0本番リリース）

### 重要な実装詳細

✅ **自然言語タスク管理**: Claude Tool Use APIで実装済み
✅ **会話履歴**: PostgreSQL conversationsテーブルで管理（24時間TTL）
✅ **Tool定義**: Task Tools 4個 + Handoff Tools 3個
✅ **Slack統合**: Events API経由、バックグラウンド処理対応

---

## 🔗 関連リソース

### コードリポジトリ

- **Main**: `/Users/noguchilin/dev/lab-project/nakamura-misaki/`
- **NixOS Config**: `/Users/noguchilin/dev/lab-project/nixos-config/`

### 本番環境

- **サービス**: `nakamura-misaki-api.service`
- **ポート**: 10000（Tailscale Funnel経由）
- **ログ**: `journalctl -u nakamura-misaki-api.service -f`

### Slack

- **Webhook URL**: `https://<tailscale-hostname>:10000/webhook/slack`
- **Bot Token**: sops-nix管理（`/run/secrets/slack_bot_token`）

---

## 📝 次のアクション（v6.0.0検討時）

今後の機能拡張を検討する際の手順：

1. **ユーザーフィードバックの収集**
   - 現在のv5.0.0の使用感をヒアリング
   - 優先度の高い機能を特定

2. **技術的負債の解消**
   - Alembicマイグレーション導入
   - 古いコード（src/main.py等）の削除
   - ドキュメント整理

3. **v6.0.0要件定義**
   - 機能仕様策定
   - アーキテクチャ設計
   - 実装計画作成

---

**最終更新者**: Claude Code
**更新履歴**: [Git Log](https://github.com/NOGUCHILin/lab-project/commits/main/nakamura-misaki/PROJECT_STATUS.md)
