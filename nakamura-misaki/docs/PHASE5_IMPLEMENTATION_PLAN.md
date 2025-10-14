# Phase 5: Slack Bot Integration - Implementation Plan

**作成日**: 2025-10-14
**ステータス**: 🚧 実装中（リカバリーフェーズ）

---

## 🎯 目的

Slack Events APIを使用して、nakamura-misaki v4.0.0をSlackワークスペースに統合し、ユーザートークン（xoxp-）経由でメッセージを受信・処理する。

---

## 📋 前提条件

### 完了済み
- ✅ Phase 0-4の実装
- ✅ PostgreSQL 16 + pgvector
- ✅ データベーステーブル
- ✅ Task/Handoff use cases
- ✅ Slack App作成（nakamura-misaki）
- ✅ User Token取得（xoxp-...）
- ✅ Signing Secret取得（5d3d6ff8...）

### 必要な情報
- Slack Bot Token: `/run/secrets/slack_bot_token`
- Slack Signing Secret: `/run/secrets/slack_signing_secret`
- Anthropic API Key: `/run/secrets/anthropic_api_key`
- Database URL: `postgresql+asyncpg://nakamura_misaki@localhost:5432/nakamura_misaki`

---

## 🏗️ アーキテクチャ

### システム構成

```
User Message (Slack)
    ↓
Slack Events API
    ↓ (HTTP POST with signature)
Tailscale Funnel (100.88.235.122:10000)
    ↓ (Reverse Proxy)
uvicorn (127.0.0.1:10000)
    ↓
FastAPI (/slack/events)
    ↓
Signature Verification
    ↓
SlackEventHandler
    ↓
Task/Handoff Use Cases
    ↓
PostgreSQL Database
    ↓
Response to Slack
```

### ポート設計

| Component | Address | Purpose |
|-----------|---------|---------|
| Tailscale Funnel | 100.88.235.122:10000 | 外部からのHTTPS受信 |
| uvicorn | 127.0.0.1:10000 | ローカルでFastAPI実行 |

**重要**: Funnelがリバースプロキシとして動作するため、uvicornは`127.0.0.1`でリッスン

---

## ✅ 実装チェックリスト

### Step 1: 依存関係の宣言的管理

#### pyproject.toml修正
```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "slack-bolt>=1.18.0",
    "slack-sdk>=3.37.0",        # 3.31.0 → 3.37.0に変更
    "claude-agent-sdk>=0.1.3",
    "anthropic>=0.37.0",
    "aiohttp>=3.13.0",          # ← 追加
    "psycopg[binary,pool]>=3.2.0",
    "sqlalchemy>=2.0.0",
    "pgvector>=0.3.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "python-dateutil>=2.8.0",
]
```

**理由**:
- `aiohttp`: AsyncWebClient (slack-sdk) が内部で使用
- `slack-sdk>=3.37.0`: slack-boltの依存関係要件

#### チェック項目
- [ ] `pyproject.toml`に`aiohttp>=3.13.0`追加
- [ ] `slack-sdk`を`>=3.37.0`に変更

---

### Step 2: NixOS設定修正

#### nakamura-misaki-api.nix修正

**変更前**:
```nix
.venv/bin/uvicorn src.adapters.primary.api:app \
  --host 0.0.0.0 \
  --port 10000 \
  --log-level info
```

**変更後**:
```nix
.venv/bin/uvicorn src.adapters.primary.api:app \
  --host 127.0.0.1 \
  --port 10000 \
  --log-level info
```

**理由**: Tailscale Funnelとのポート競合を回避

#### チェック項目
- [ ] `--host 127.0.0.1`に変更
- [ ] コミット・プッシュ

---

### Step 3: デプロイワークフロー改善

#### .github/workflows/deploy.yml修正

**追加するステップ** (Sync Dashboard code の後):

```yaml
- name: Install nakamura-misaki dependencies
  uses: appleboy/ssh-action@master
  with:
    host: home-lab-01
    username: ${{ secrets.NIXOS_USER }}
    key: ${{ secrets.NIXOS_SSH_KEY }}
    script: |
      cd /home/noguchilin/projects/lab-project/nakamura-misaki

      # 依存関係をインストール
      .venv/bin/pip install -e .

      echo "✅ Dependencies installed"
```

**理由**: コード同期後に依存関係も同期する必要がある

#### チェック項目
- [ ] 依存関係インストールステップ追加
- [ ] コミット・プッシュ

---

### Step 4: クリーンデプロイ

#### 本番環境のクリーンアップ

```bash
# 手動で実行（SSH経由）
ssh nixos "cd ~/projects/lab-project/nakamura-misaki && rm -rf .venv"
```

**理由**: 手動インストールした依存関係を削除し、宣言的設定のみで再構築

#### デプロイ実行

```bash
# ローカルで実行
git add .
git commit -m "fix: Configure nakamura-misaki for proper Tailscale Funnel integration

- Add aiohttp dependency to pyproject.toml
- Change uvicorn bind address to 127.0.0.1
- Add dependency installation step to deploy workflow"
git push origin main
```

#### モニタリング

```bash
# デプロイ監視
gh run watch --repo NOGUCHILin/lab-project

# サービス状態確認
ssh nixos "systemctl status nakamura-misaki-api.service"

# ログ確認
ssh nixos "journalctl -u nakamura-misaki-api.service -f"
```

#### チェック項目
- [ ] 本番`.venv`削除
- [ ] コミット・プッシュ
- [ ] デプロイ成功確認
- [ ] サービスが`active (running)`
- [ ] ポート10000がリッスン中（`ss -tlnp | grep :10000`）

---

### Step 5: 動作確認

#### ヘルスチェック

```bash
# ローカルから（Tailscale経由）
curl https://home-lab-01.tail4ed625.ts.net:10000/health

# 期待される応答
{"status":"ok","service":"nakamura-misaki","version":"4.0.0"}
```

#### チェック項目
- [ ] `/health`エンドポイントが200 OK
- [ ] JSON応答が正しい

---

### Step 6: Slack App設定

#### Event Subscriptions設定

1. Slack App管理画面にアクセス
2. **Event Subscriptions** → Enable Events
3. **Request URL**: `https://home-lab-01.tail4ed625.ts.net:10000/slack/events`
4. Slackが自動でURL Verification Challengeを送信
5. ✅マークが表示されることを確認

#### Subscribe to bot events設定

以下のイベントを購読:
- `message.channels`
- `message.groups`
- `message.im`
- `message.mpim`

**Save Changes**をクリック

#### チェック項目
- [ ] Request URL検証成功（✅マーク）
- [ ] Botイベント購読設定完了
- [ ] 変更保存完了

---

### Step 7: 統合テスト

#### テストケース1: URL Verification

```bash
# Slackが自動で送信（Step 6で実行済み）
# ログで確認
ssh nixos "journalctl -u nakamura-misaki-api.service -n 50 | grep 'url_verification'"
```

**期待される動作**: `{"challenge": "..."}`を返す

#### テストケース2: メッセージ受信

1. Slackワークスペースで任意のチャンネルに投稿
2. ログでイベント受信を確認

```bash
ssh nixos "journalctl -u nakamura-misaki-api.service -f"
```

**期待されるログ**:
```
INFO: Started server process [PID]
INFO: Waiting for application startup.
✅ nakamura-misaki API server started
INFO: POST /slack/events 200 OK
```

#### テストケース3: 署名検証

不正な署名でリクエスト送信（手動テスト）

**期待される動作**: `401 Invalid signature`

#### テストケース4: Taskコマンド

Slackで以下を投稿:
```
今日のタスク確認して
```

**期待される動作**: nakamura-misakiからタスクリストの返信

#### チェック項目
- [ ] URL Verification成功
- [ ] メッセージイベント受信確認
- [ ] 署名検証動作確認
- [ ] Taskコマンド動作確認

---

## 🚨 トラブルシューティング

### 問題1: サービスが起動しない

**症状**: `systemctl status`で`activating (auto-restart)`

**確認事項**:
```bash
journalctl -u nakamura-misaki-api.service -n 50
```

**よくある原因**:
1. ポート競合 → `ss -tlnp | grep :10000`で確認
2. モジュール不足 → `.venv/bin/pip list | grep <module>`で確認
3. シークレット未設定 → `ls -la /run/secrets/`で確認

### 問題2: Slack URL Verification失敗

**症状**: Request URLに❌マーク

**確認事項**:
1. `/health`エンドポイントにアクセス可能か
2. Tailscale Funnelが正しく設定されているか
3. `api.py`に`url_verification`処理があるか

### 問題3: 署名検証エラー

**症状**: 全リクエストが`401 Invalid signature`

**確認事項**:
1. Signing Secretが正しいか → `cat /run/secrets/slack_signing_secret`
2. タイムスタンプ検証（5分以内）が正しいか

### 問題4: メッセージに反応しない

**症状**: イベントは受信するが、応答がない

**確認事項**:
1. `SlackEventHandler`が正しく呼ばれているか
2. データベース接続が確立されているか
3. Use casesが正しく動作しているか

---

## 📊 成功基準

### Phase 5完了条件

- [x] FastAPI server実装
- [x] Slack Event Handler実装
- [ ] 依存関係の宣言的管理
- [ ] サービスが`active (running)`で安定動作
- [ ] `/health`エンドポイントが正常
- [ ] Slack URL Verification成功
- [ ] メッセージイベント受信・処理確認
- [ ] 署名検証が正常動作
- [ ] Taskコマンドが動作

### Phase 5+α（将来）

- [ ] Handoffコマンド動作
- [ ] 自然言語パーサー改善
- [ ] エラーハンドリング強化
- [ ] パフォーマンス計測

---

## 📝 関連ドキュメント

- [RECOVERY_PLAN_2025-10-14.md](./RECOVERY_PLAN_2025-10-14.md) - リカバリー計画
- [CURRENT_STATE_2025-10-14.md](./CURRENT_STATE_2025-10-14.md) - 現状スナップショット
- [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - 全体進捗
- [/lab-project/claudedocs/service-registry.md](../../../claudedocs/service-registry.md) - Service Registry

---

Generated with [Claude Code](https://claude.com/claude-code)
