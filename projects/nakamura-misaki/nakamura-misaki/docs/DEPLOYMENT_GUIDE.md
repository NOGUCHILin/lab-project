# nakamura-misaki v4.0.0 - Deployment Guide

本番環境へのデプロイ手順

---

## 📋 前提条件

- NixOS 24.05以降
- PostgreSQL 16 + pgvector extension
- Slack Bot Token (Scopes: `chat:write`, `users:read`, `im:write`)
- Anthropic API Key
- sops-nixによる秘密情報管理

---

## 🚀 デプロイ手順

### 1. Secrets設定

#### テンプレートから作成
```bash
cd nixos-config/secrets
cp nakamura-misaki.yaml.template nakamura-misaki.yaml
```

#### 実際の値に編集
```yaml
nakamura-misaki:
  DATABASE_URL: "postgresql+asyncpg://nakamura_misaki:YOUR_PASSWORD@localhost:5432/nakamura_misaki"
  SLACK_BOT_TOKEN: "xoxb-YOUR-SLACK-BOT-TOKEN"
  ANTHROPIC_API_KEY: "sk-ant-YOUR-ANTHROPIC-API-KEY"
  PM_USER_ID: "U01ABC123"  # あなたのSlack User ID
```

#### sopsで暗号化
```bash
# age公開鍵が設定済みであることを確認
cat ~/.config/sops/age/keys.txt

# 暗号化
sops -e nakamura-misaki.yaml
```

### 2. NixOS設定確認

以下のファイルが正しくimportされているか確認:

#### `hosts/home-lab-01/configuration.nix`
```nix
imports = [
  # ...
  ../../modules/services/registry/nakamura-misaki.nix
  ../../modules/services/registry/nakamura-misaki-db.nix
  ../../modules/services/registry/nakamura-misaki-reminder.nix
];
```

### 3. プロジェクトファイル配置

```bash
# プロジェクトを /var/lib/nakamura-misaki/ にコピー
sudo mkdir -p /var/lib/nakamura-misaki
sudo cp -r /path/to/lab-project/nakamura-misaki /var/lib/nakamura-misaki/
sudo chown -R nakamura-misaki:nakamura-misaki /var/lib/nakamura-misaki
```

### 4. NixOS再ビルド

```bash
cd nixos-config

# 構文チェック
nix flake check

# フォーマット
nix fmt

# 再ビルド＆デプロイ（ローカル）
sudo nixos-rebuild switch --flake .#home-lab-01

# または GitHub Actions経由（推奨）
git add -A
git commit -m "feat: Deploy nakamura-misaki v4.0.0"
git push origin main
```

### 5. デプロイ確認

#### サービス状態確認
```bash
# PostgreSQL確認
systemctl status postgresql

# DB初期化確認
systemctl status nakamura-misaki-init-db
journalctl -u nakamura-misaki-init-db -n 50

# リマインダースケジューラー確認
systemctl status nakamura-misaki-reminder.timer
systemctl list-timers | grep nakamura
```

#### データベース確認
```bash
# PostgreSQL接続
sudo -u postgres psql

# データベース確認
\l nakamura_misaki

# pgvector extension確認
\dx

# テーブル確認
\c nakamura_misaki
\dt

# 終了
\q
```

#### テーブル構造確認
```sql
-- notes table (pgvector)
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'notes';

-- tasks table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tasks';

-- handoffs table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'handoffs';
```

---

## 🧪 動作確認

### Slackでテスト

#### タスク管理
```
# タスク登録
「デプロイテスト」を今日やる

# タスク一覧
今日のタスクは？

# タスク完了
タスク [UUID] 完了
```

#### ハンドオフ管理
```
# ハンドオフ登録
「テスト完了」を @username に [task_id] 2時間後に引き継ぎ

# ハンドオフ一覧
引き継ぎ一覧

# ハンドオフ完了
ハンドオフ [handoff_id] 完了
```

### ログ確認

```bash
# リマインダーログ確認
journalctl -u nakamura-misaki-reminder.service -f

# PostgreSQLログ確認
journalctl -u postgresql -f
```

---

## 🔧 トラブルシューティング

### DB初期化が失敗する

**症状**: `nakamura-misaki-init-db.service` が failed

**原因**:
- PostgreSQLが起動していない
- プロジェクトディレクトリが存在しない
- DATABASE_URLが間違っている

**解決策**:
```bash
# PostgreSQL起動確認
systemctl status postgresql

# プロジェクトディレクトリ確認
ls -la /var/lib/nakamura-misaki/nakamura-misaki

# Secrets確認
sudo cat /run/secrets/nakamura-misaki/env

# 手動で初期化実行
sudo -u nakamura-misaki bash
cd /var/lib/nakamura-misaki/nakamura-misaki
export DATABASE_URL="postgresql+asyncpg://..."
python scripts/init_db.py
```

### リマインダーが送信されない

**症状**: ハンドオフ登録したがリマインダーDMが届かない

**原因**:
- SLACK_BOT_TOKENが間違っている
- Slack Botのスコープ不足
- データベース接続エラー

**解決策**:
```bash
# タイマー確認
systemctl status nakamura-misaki-reminder.timer

# 手動実行してログ確認
sudo -u nakamura-misaki bash
cd /var/lib/nakamura-misaki/nakamura-misaki
export DATABASE_URL="..."
export SLACK_BOT_TOKEN="..."
export ANTHROPIC_API_KEY="..."
python scripts/send_reminders.py
```

### pgvector extensionが見つからない

**症状**: `CREATE EXTENSION IF NOT EXISTS vector` が失敗

**原因**: PostgreSQLにpgvectorがインストールされていない

**解決策**:
```bash
# NixOS設定確認
grep -r "pgvector" nixos-config/

# PostgreSQL再起動
sudo systemctl restart postgresql

# 手動でextension作成
sudo -u postgres psql -d nakamura_misaki -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## 📊 Monitoring

### サービス一覧確認

```bash
# 統合ダッシュボードで確認
check-services

# 手動確認
systemctl status postgresql
systemctl status nakamura-misaki-reminder.timer
systemctl list-timers | grep nakamura
```

### データベース統計

```sql
-- タスク数
SELECT status, COUNT(*) FROM tasks GROUP BY status;

-- ハンドオフ数
SELECT
  CASE
    WHEN completed_at IS NOT NULL THEN 'completed'
    ELSE 'pending'
  END as status,
  COUNT(*)
FROM handoffs
GROUP BY status;

-- ノート数
SELECT category, COUNT(*) FROM notes GROUP BY category;
```

---

## 🔄 アップデート手順

```bash
# プロジェクト更新
cd /path/to/lab-project
git pull origin main

# プロジェクトファイル再配置
sudo cp -r nakamura-misaki /var/lib/nakamura-misaki/
sudo chown -R nakamura-misaki:nakamura-misaki /var/lib/nakamura-misaki

# データベースマイグレーション（必要に応じて）
sudo -u nakamura-misaki bash
cd /var/lib/nakamura-misaki/nakamura-misaki
export DATABASE_URL="..."
python scripts/migrate_db.py  # 将来実装

# NixOS再ビルド
cd nixos-config
git pull origin main
sudo nixos-rebuild switch --flake .#home-lab-01
```

---

## 📝 参考情報

- [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - 実装完了状況
- [../CLAUDE.md](../CLAUDE.md) - プロジェクト概要
- [Service Registry Pattern](../../nixos-config/claudedocs/service-registry.md) - NixOSサービス管理
- [Kiro Specifications](../.kiro/) - AWS Kiro仕様書

---

Generated with [Claude Code](https://claude.com/claude-code)
