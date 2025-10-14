# nakamura-misaki v4.0.0 - Current State Snapshot

**作成日**: 2025-10-14 18:48 JST
**目的**: 本番環境の正確な状態を記録

---

## 🖥️ 本番環境 (home-lab-01)

### システム情報
- **ホスト名**: home-lab-01
- **OS**: NixOS
- **Tailscale IP**: 100.88.235.122
- **ユーザー**: noguchilin

### サービス状態

#### nakamura-misaki-api.service
```
Status: activating (auto-restart) - FAILED
Error: [Errno 98] error while attempting to bind on address ('0.0.0.0', 10000): address already in use
Restart counter: 継続的に再起動試行中
```

#### その他のnakamura-misakiサービス
```
nakamura-misaki-init-db.service: inactive (oneshot完了)
nakamura-misaki-enable-vector.service: inactive (oneshot完了)
nakamura-misaki-reminder.timer: active (running)
```

### ポート使用状況

#### ポート10000
```
LISTEN 0  4096  100.88.235.122:10000  0.0.0.0:*     (Tailscale Funnel)
LISTEN 0  4096  [fd7a:115c:a1e0::4801:eb86]:10000  [::]:*  (Tailscale Funnel IPv6)
```

**問題**: uvicornが`0.0.0.0:10000`でバインドしようとして競合

### Python環境

#### venv location
`/home/noguchilin/projects/lab-project/nakamura-misaki/.venv`

#### インストール済みパッケージ
```
anthropic==0.40.0       ← 手動インストール
aiohttp==3.13.0         ← 手動インストール
aiohappyeyeballs==2.6.1 ← aiohttp依存
aiosignal==1.4.0        ← aiohttp依存
fastapi==0.119.0
frozenlist==1.8.0       ← aiohttp依存
multidict==6.7.0        ← aiohttp依存
propcache==0.4.1        ← aiohttp依存
slack-bolt==1.26.0
slack-sdk==3.37.0       ← 手動アップグレード（元々3.31.0が必要だったが、slack-bolt要件で3.37.0に）
uvicorn==0.37.0
yarl==1.22.0            ← aiohttp依存
psycopg[binary,pool]>=3.2.0
sqlalchemy>=2.0.0
pgvector>=0.3.0
pydantic>=2.9.0
pydantic-settings>=2.5.0
python-dateutil>=2.8.0
```

**⚠️ 注意**: `anthropic`, `aiohttp`, および関連依存関係は手動インストールのため揮発的

### データベース状態

#### PostgreSQL
```
Service: postgresql.service - active (running)
Version: PostgreSQL 16
Extension: pgvector - enabled
```

#### テーブル
```sql
-- 存在確認済み
tasks
handoffs
notes
sessions
```

### NixOS設定ファイル

#### nakamura-misaki-api.nix
```nix
ExecStart: .venv/bin/uvicorn src.adapters.primary.api:app \
  --host 0.0.0.0 \        ← 問題: Tailscale Funnelと競合
  --port 10000 \
  --log-level info
```

**修正必要**: `--host 127.0.0.1`に変更

### シークレット設定

#### 設定済みシークレット
```
/run/secrets/slack_bot_token         - OK (xoxp-...)
/run/secrets/anthropic_api_key       - OK (sk-ant-...)
/run/secrets/slack_signing_secret    - OK (5d3d6ff8...)
/run/secrets/database_url            - OK (postgresql+asyncpg://...)
```

**確認済み**: すべてのシークレットファイルが存在し、サービス起動スクリプトで読み込まれている

### ファイルシステム

#### コード同期状態
```bash
~/projects/lab-project/nakamura-misaki/
├── src/
│   ├── adapters/
│   │   └── primary/
│   │       ├── api.py              ← 最新（FastAPI app定義）
│   │       └── api/                ← 削除済み ✅
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── .venv/                           ← 手動で依存関係追加済み
├── pyproject.toml                   ← 最新
└── ...
```

**最終同期**: 2025-10-14 18:41 JST (GitHub Actions Deploy)

---

## 💻 ローカル環境

### pyproject.toml

#### 依存関係リスト
```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "slack-bolt>=1.18.0",
    "slack-sdk>=3.31.0",          ← バージョン競合あり（slack-boltが3.37.0を要求）
    "claude-agent-sdk>=0.1.3",
    "anthropic>=0.37.0",
    "psycopg[binary,pool]>=3.2.0",
    "sqlalchemy>=2.0.0",
    "pgvector>=0.3.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "python-dateutil>=2.8.0",
    # ❌ aiohttp が含まれていない
]
```

**問題点**:
1. `aiohttp`が依存関係に含まれていない
2. `slack-sdk>=3.31.0`だが、`slack-bolt==1.26.0`は`slack-sdk>=3.37.0`を要求

### NixOS設定 (nixos-config/)

#### modules/services/registry/nakamura-misaki-api.nix
```nix
ExecStart = pkgs.writeShellScript "start-nakamura-api" ''
  # ... 環境変数設定 ...

  .venv/bin/uvicorn src.adapters.primary.api:app \
    --host 0.0.0.0 \    ← 修正必要
    --port 10000 \
    --log-level info
'';
```

#### .github/workflows/deploy.yml
```yaml
- name: Sync Dashboard code
  # nakamura-misakiコードをrsyncで同期
  # ❌ 依存関係のインストールステップがない
```

**問題点**: 依存関係同期ステップが存在しない

---

## 🔍 差分分析

### 本番 vs ローカル

| 項目 | 本番環境 | ローカル | 差分 |
|------|---------|---------|------|
| `anthropic` | 0.40.0（手動） | pyproject.toml定義 | 手動インストールで一致 |
| `aiohttp` | 3.13.0（手動） | **記載なし** | ❌ pyproject.tomlに追加必要 |
| `slack-sdk` | 3.37.0（手動） | >=3.31.0定義 | バージョン要件緩和必要 |
| api/ ディレクトリ | 削除済み | 削除済み | ✅ 一致 |
| uvicorn bind | 0.0.0.0 | 0.0.0.0 | ❌ 両方127.0.0.1に修正必要 |

### 手動操作リスト

以下は手動で実行したため、宣言的設定に含まれていない：

1. `ssh nixos "cd ~/projects/lab-project/nakamura-misaki && .venv/bin/pip install anthropic==0.40.0 slack-sdk==3.31.0"`
2. `ssh nixos "cd ~/projects/lab-project/nakamura-misaki && .venv/bin/pip install slack-sdk==3.37.0"` (アップグレード)
3. `ssh nixos "cd ~/projects/lab-project/nakamura-misaki && .venv/bin/pip install aiohttp"`
4. `rm -rf nakamura-misaki/src/adapters/primary/api` (ローカル)

**影響**: 1-3は次回`.venv`再構築時に消失するリスク

---

## 🚨 問題リスト

### 即座に解決必要

1. **ポート競合** (Critical)
   - 現象: uvicornが起動できない
   - 原因: `0.0.0.0:10000`がTailscale Funnelと競合
   - 対策: uvicornを`127.0.0.1:10000`にバインド

2. **依存関係不足** (Critical)
   - 現象: 手動インストールに依存
   - 原因: `pyproject.toml`に`aiohttp`がない
   - 対策: `aiohttp`を依存関係に追加

3. **デプロイワークフロー不備** (High)
   - 現象: 依存関係が同期されない
   - 原因: `deploy.yml`に同期ステップがない
   - 対策: `uv sync`または`pip install -e .`ステップ追加

### 次回改善

4. **slack-sdkバージョン競合** (Medium)
   - 現象: `slack-bolt`が`slack-sdk>=3.37.0`を要求
   - 対策: `slack-sdk>=3.37.0`に緩和

5. **uvコマンド不在** (Low)
   - 現象: 本番環境に`uv`がインストールされていない
   - 対策: NixOS設定で`uv`をインストール、またはpip経由で依存関係管理

---

## 📊 完了済み作業

### Phase 0-4
- ✅ PostgreSQL 16 + pgvector extension
- ✅ データベーステーブル (tasks, handoffs, notes, sessions)
- ✅ systemd services (init-db, enable-vector, reminder timer)
- ✅ Slack Event Handler実装
- ✅ FastAPI server実装 (api.py)

### Phase 5 (進行中)
- ✅ `api.py`作成
- ✅ `slack_event_handler.py`作成
- ✅ シークレット暗号化 (sops-nix)
- ✅ `nakamura-misaki-api.nix`作成
- ✅ 古い`api/`ディレクトリ削除
- ✅ 重複サービス定義削除
- 🚧 依存関係の宣言的管理（未完了）
- 🚧 サービス起動（ポート競合により失敗中）

---

## ✅ 次のアクション

1. [RECOVERY_PLAN_2025-10-14.md](./RECOVERY_PLAN_2025-10-14.md) Phase Bの実行
2. `pyproject.toml`修正
3. `nakamura-misaki-api.nix`修正
4. `deploy.yml`修正
5. クリーンデプロイ

---

Generated with [Claude Code](https://claude.com/claude-code)
