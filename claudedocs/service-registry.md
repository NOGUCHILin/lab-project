# Service Registry Pattern 詳細ガイド

lab-projectにおけるService Registryパターンの完全実装ガイド

## 📋 目次

1. [概要](#概要)
2. [アーキテクチャ](#アーキテクチャ)
3. [サービス追加の完全フロー](#サービス追加の完全フロー)
4. [Tailscale公開設定](#tailscale公開設定)
5. [トラブルシューティング](#トラブルシューティング)
6. [ベストプラクティス](#ベストプラクティス)

---

## 概要

### Service Registryとは

lab-projectでは、すべてのサービス（dashboard, nakamura-misaki, code-server等）を`modules/services/registry/default.nix`で一元管理しています。これにより：

- **中央集約**: 全サービスのポート・URL・ヘルスチェックを一箇所で管理
- **自動生成**: `/etc/unified-dashboard/services.json`としてエクスポート、ダッシュボードから参照可能
- **宣言的**: NixOS設定として宣言的に管理、冪等性保証

### Service定義の構造

```nix
{
  port = 3000;                    # リスニングポート
  path = "/";                     # URLパス
  name = "Unified Dashboard";     # サービス名
  description = "統合ダッシュボード"; # 説明
  healthCheck = "/api/health";    # ヘルスチェックエンドポイント
  icon = "📊";                    # アイコン（絵文字）
}
```

---

## アーキテクチャ

### ファイル構成

```
nixos-config/
├── modules/
│   ├── core/
│   │   └── port-management.nix        # ポート一元管理
│   ├── services/
│   │   ├── registry/
│   │   │   ├── default.nix            # レジストリ統合
│   │   │   ├── dashboard.nix          # 各サービス定義
│   │   │   ├── nakamura-misaki.nix
│   │   │   ├── code-server.nix
│   │   │   └── [新サービス].nix       # 追加サービス
│   │   └── tailscale-direct.nix       # Tailscale公開設定
│   └── networking/
│       └── tailscale.nix              # Tailscale基本設定
└── hosts/
    └── home-lab-01/
        └── configuration.nix          # ホスト設定
```

### データフロー

```
1. サービス定義 (registry/*.nix)
   ↓
2. レジストリ統合 (default.nix)
   ↓
3. JSON出力 (/etc/unified-dashboard/services.json)
   ↓
4. ダッシュボード読み込み (Next.jsアプリ)
   ↓
5. ユーザー表示 (ブラウザ)
```

---

## サービス追加の完全フロー

### 1. ポート番号の決定

**手順**:
1. `modules/core/port-management.nix` を確認
2. 未使用ポートを選択（例: 3006）
3. port-management.nixに新ポートを追加

**例**:
```nix
# modules/core/port-management.nix
{
  ports = {
    dashboard = 3000;
    nakamura-misaki-admin = 3002;
    new-service = 3006;  # 追加
  };
}
```

### 2. サービス定義ファイル作成

**ファイル名**: `modules/services/registry/[サービス名].nix`

**テンプレート**:
```nix
# modules/services/registry/my-service.nix
{
  port = 3006;
  path = "/my-service";
  name = "My Service";
  description = "新しいサービスの説明";
  healthCheck = "/health";
  icon = "🚀";
}
```

**アイコン選択ガイド**:
- API: 🔌
- Dashboard: 📊
- Editor: ✏️
- Database: 🗄️
- Worker: ⚙️
- Monitor: 👁️

### 3. Registryへの登録

**ファイル**: `modules/services/registry/default.nix`

```nix
{ config, lib, pkgs, ... }:

let
  services = [
    (import ./dashboard.nix)
    (import ./nakamura-misaki.nix)
    (import ./code-server.nix)
    (import ./my-service.nix)  # 追加
  ];
in
{
  # ... 既存の設定 ...
}
```

### 4. Tailscale公開設定

#### パターンA: Tailscale Serve（内部公開）

**ファイル**: `modules/services/tailscale-direct.nix`

```nix
serveConfig = {
  "https:443" = "http://localhost:3000";  # Dashboard
  "https:443/my-service" = "http://localhost:3006";  # 追加
};
```

**アクセスURL**: `https://[tailscale-hostname]/my-service`

#### パターンB: Tailscale Funnel（外部公開）

**制約**: ポート443/8443/10000のみサポート

```nix
serveConfig = {
  "https:10001" = "https://localhost:10001";  # Funnel公開
};
```

**アクセスURL**: `https://[tailscale-hostname]:10001`

### 5. Configuration.nixへのimport

**ファイル**: `nixos-config/hosts/home-lab-01/configuration.nix`

```nix
imports = [
  ../../modules/core
  ../../modules/networking
  ../../modules/services/registry  # レジストリモジュール
  ../../modules/services/tailscale-direct.nix
];
```

### 6. ビルド・デプロイ

```bash
# ローカルテスト（構文チェック）
cd nixos-config
nix flake check

# mainブランチにpush（自動デプロイ）
git add .
git commit -m "feat: Add my-service to service registry"
git push origin main

# デプロイ状況確認
gh run watch
```

### 7. 動作確認

```bash
# SSH接続
ssh home-lab-01

# サービス状態確認
systemctl status my-service.service

# Tailscale公開状態確認
tailscale serve status
# または
tailscale funnel status

# ヘルスチェック
curl http://localhost:3006/health
```

---

## Tailscale公開設定

### Serve vs Funnel の選択基準

| 要件 | 推奨方式 | ポート制限 | 用途例 |
|------|----------|------------|--------|
| Tailscaleネットワーク内のみ | Serve | なし | 管理画面、内部API |
| インターネット公開 | Funnel | 443/8443/10000のみ | Webhook受信、公開API |

### Serve設定例

```nix
# modules/services/tailscale-direct.nix
{
  services.tailscale-direct = {
    enable = true;
    enforceDeclarative = true;
    serveConfig = {
      # ルートドメイン
      "https:443" = "http://localhost:3000";

      # サブパス
      "https:443/admin" = "http://localhost:3002";
      "https:443/api" = "http://localhost:10000";

      # 異なるポート（Tailscaleネットワーク内のみ）
      "https:8443" = "http://localhost:5678";
    };
  };
}
```

### Funnel設定例

```nix
{
  services.tailscale-direct = {
    enable = true;
    enforceDeclarative = true;
    serveConfig = {
      # Funnel公開（インターネットからアクセス可能）
      "https:443" = "https://localhost:3000";
      "https:10000" = "https://localhost:10000";  # Webhook用
    };
  };
}
```

**重要**: Funnelで公開する場合、バックエンドサービスもHTTPS化が必要

---

## トラブルシューティング

### 問題1: ポート競合エラー

**症状**:
```
error: Port 3000 is already in use by dashboard
```

**原因**: 既存サービスと同じポートを指定

**解決策**:
1. `modules/core/port-management.nix` で空きポートを確認
2. 別のポート番号を選択（例: 3006）
3. port-management.nixに新ポートを追加

### 問題2: サービスがダッシュボードに表示されない

**原因チェックリスト**:
- [ ] `registry/default.nix` に登録済みか？
- [ ] NixOS再ビルドは成功したか？
- [ ] `/etc/unified-dashboard/services.json` に含まれているか？

**確認コマンド**:
```bash
ssh home-lab-01
cat /etc/unified-dashboard/services.json | jq
```

### 問題3: Tailscale公開が動作しない

**確認ポイント**:
```bash
# Tailscale状態確認
tailscale status

# Serve/Funnel設定確認
tailscale serve status
tailscale funnel status

# Tailscaleログ確認
journalctl -u tailscaled -f
```

**よくあるエラー**:
- Funnel非対応ポート（443/8443/10000以外）を使用
- HTTPSバックエンドが必要なのにHTTPを指定
- `enforceDeclarative = true` なのに手動変更を試みた

### 問題4: NixOS再ビルド失敗

**診断**:
```bash
# 構文チェック
cd nixos-config
nix flake check

# 詳細ログ確認
sudo nixos-rebuild switch --flake .#home-lab-01 --show-trace
```

**よくある原因**:
- Nixファイルの構文エラー
- Import漏れ
- 未定義変数の参照

---

## ベストプラクティス

### 1. サービス命名規則

- **ファイル名**: ケバブケース（例: `my-service.nix`）
- **サービス名**: タイトルケース（例: "My Service"）
- **ポート変数**: スネークケース（例: `my_service_port`）

### 2. ポート番号の割り当て

| 範囲 | 用途 |
|------|------|
| 3000-3999 | Webアプリケーション |
| 5000-5999 | ワークフローエンジン（n8n等） |
| 8000-8999 | 開発ツール（code-server等） |
| 9000-9999 | ファイル管理・監視 |
| 10000-10999 | 外部公開API（Funnel用） |

### 3. ヘルスチェックエンドポイント

**推奨実装**:
```typescript
// Next.js API Route例
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.APP_VERSION
  });
}
```

### 4. Git Commit Message

```bash
# 新サービス追加
feat: Add webhook-api to service registry

# ポート変更
fix: Change my-service port to avoid conflict

# Tailscale設定更新
config: Enable Funnel for webhook-api on port 10001
```

### 5. テスト戦略

**デプロイ前**:
```bash
# 1. ローカル構文チェック
nix flake check

# 2. 手動デプロイ確認（本番前にテスト環境で）
sudo nixos-rebuild switch --flake .#home-lab-01

# 3. サービス起動確認
systemctl status my-service.service

# 4. ヘルスチェック
curl http://localhost:3006/health
```

**デプロイ後**:
```bash
# 1. GitHub Actions成功確認
gh run watch

# 2. 本番環境SSH接続
ssh home-lab-01

# 3. サービス一覧確認
check-services

# 4. Tailscale公開確認
tailscale serve status
```

---

## 参考リンク

- [NixOS Manual - Services](https://nixos.org/manual/nixos/stable/#ch-configuration)
- [Tailscale Serve Documentation](https://tailscale.com/kb/1242/tailscale-serve/)
- [Tailscale Funnel Documentation](https://tailscale.com/kb/1223/tailscale-funnel/)
- [lab-project CLAUDE.md](../CLAUDE.md)

---

最終更新: 2025-10-12
