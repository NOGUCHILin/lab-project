# nakamura-misaki Project

**中村美咲 - 人格としてのタスク管理アシスタント**

**現在**: v4.0.0 (Hexagonal Architecture + Command Parsers)
**次期**: v5.0.0 (Claude Agent SDK + Tool Use)

---

## 🎯 新規セッション開始時のガイド

> ⚠️ **必読**: まず [`PROJECT_STATUS.md`](PROJECT_STATUS.md) で現在の進捗状況を確認してください

**現在**: Phase 1 - Project Management Context（テスト実装中、99テスト完了）

---

## 📂 プロジェクト構成

```
nakamura-misaki/
├── src/contexts/          # Bounded Contexts（Hexagonal Architecture）
│   ├── personal_tasks/
│   ├── project_management/  # Phase 1実装中
│   ├── conversations/
│   ├── workforce_management/
│   └── handoffs/
├── tests/
│   ├── unit/              # ユニットテスト（外部依存なし）
│   ├── integration/       # インテグレーションテスト（DB使用）
│   └── e2e/              # E2Eテスト
├── claudedocs/           # 詳細ドキュメント（実装計画、テスト戦略等）
├── docs/                 # アーキテクチャ・デプロイ手順
├── PROJECT_STATUS.md     # Phase 1-4の進捗状況
├── CLAUDE.md            # このファイル（開発ガイド）
└── README.md            # プロジェクト概要・起動方法
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

## 🏗️ アーキテクチャ原則（厳守）

1. **Hexagonal Architecture**: Domain層は外部依存なし
2. **TDD必須**: Red→Green→Refactor サイクル厳守
3. **新機能 = 新Bounded Context**: 既存Contextを肥大化させない
4. **Repository Pattern**: データアクセスは抽象化
5. **DI Container**: 依存性注入で疎結合を維持

**詳細**: [`docs/ARCHITECTURE_V4.md`](docs/ARCHITECTURE_V4.md)

---

## 📚 詳細ドキュメント（`claudedocs/`配下）

実装計画・テスト戦略などの詳細は以下を参照：

| ドキュメント | 内容 |
|-------------|------|
| **`PROJECT_STATUS.md`** | **Phase 1-4の進捗状況（最重要）** |
| `claudedocs/IMPLEMENTATION_PLAN_PHASE1-4.md` | Phase 1-4全体計画・実装チェックリスト |
| `claudedocs/testing-strategy.md` | TDD戦略・AAA Pattern・カバレッジ目標 |
| `docs/ARCHITECTURE_V4.md` | Hexagonal Architecture詳細 |

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

**現在のカバレッジ**: Domain 100%, Application 100%, Tools 100% ✅

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

最終更新: 2025-10-26（Phase 1テスト実装中、ドキュメント構造整理）
