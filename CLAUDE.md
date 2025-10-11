# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**NixOS統合環境** - 全プロジェクト・NixOS設定を統合管理する統合リポジトリ

このリポジトリは、複数のWebサービス（dashboard, nakamura-misaki, code-server等）とそれらを動かすNixOS設定を一元管理しています。mainブランチへのpushで自動的にGitHub Actions経由でNixOS本番環境にデプロイされます。

## Architecture

### Flake-based NixOS Configuration

- **flake.nix**: NixOS設定のエントリーポイント。deploy-rs, home-manager, sops-nixを統合
- **ホスト定義**: `nixos-config/hosts/home-lab-01/configuration.nix`が本番環境のホスト設定
- **モジュール構成**:
  - `modules/core/`: 基盤設定（ポート管理、SSH、ファイアウォール、シークレット）
  - `modules/networking/`: Tailscale VPN設定
  - `modules/services/registry/`: サービス定義（各サービス毎にnixファイル）

### Service Registry Pattern

**重要**: すべてのサービスは `modules/services/registry/default.nix` で一元管理されています。

- 各サービスは `{ port, path, name, description, healthCheck, icon }` で定義
- ポート番号、URL、ヘルスチェックエンドポイントが一箇所に集約
- `/etc/unified-dashboard/services.json` として出力され、ダッシュボードから参照可能
- 新しいサービス追加時は:
  1. `modules/services/registry/` に `.nix` ファイル作成
  2. `default.nix` の `services` に登録
  3. `configuration.nix` の `imports` に追加

### Tailscale Exposure

- **Tailscale Funnel**: インターネット公開（例: Slack Webhook用のポート10000）
- **Tailscale Serve**: Tailscaleネットワーク内のみ公開（他の全サービス）
- 設定は `modules/services/tailscale-direct.nix` で宣言的に管理
- Funnelは443, 8443, 10000のみサポート

### Secrets Management (sops-nix)

- 暗号化された秘密情報は `secrets/` ディレクトリに格納
- `.sops.yaml` でage公開鍵を指定
- サービスから `config.sops.secrets.<name>.path` でアクセス
- **重要**: 秘密情報は絶対にプレーンテキストでコミットしない

## Common Development Commands

### NixOS Configuration

```bash
# ローカルでビルドテスト（構文チェック）
cd nixos-config
nix flake check

# フォーマット
nix fmt

# 開発シェル起動
nix develop          # 軽量デフォルトシェル
nix develop .#node   # Node.js開発環境
nix develop .#py     # Python開発環境
```

### Deployment

```bash
# mainブランチにpushすると自動デプロイ
git push origin main

# デプロイワークフロー手動トリガー
gh workflow run deploy.yml

# デプロイ状況確認
gh run list --limit 5
gh run watch
```

### Service Management on NixOS

```bash
# SSH接続（Tailscale経由）
ssh home-lab-01

# サービス状態確認
systemctl status nakamura-misaki-api.service
journalctl -u nakamura-misaki-api.service -f

# Tailscale Funnel/Serve状態確認
tailscale funnel status
tailscale serve status

# サービス一覧とヘルスチェック
check-services  # NixOSに配置されたヘルパースクリプト
```

## Key Services

### nakamura-misaki (Multi-user Claude Agent)

- **API**: FastAPI（ポート10000、Slack Webhook受信用にFunnel公開）
- **Admin UI**: Next.js（ポート3002、Tailscaleネットワーク内のみ）
- **重要**: APIサービスには `path = [ nodejs_22 bash coreutils python3 ]` が必要
- プロジェクトディレクトリ: `/home/noguchilin/projects/nakamura-misaki`
- venv環境を使用（`.venv/bin/python`）

### unified-dashboard

- **Framework**: Next.js 22
- **Port**: 3000（Tailscale Serveでルートドメインに公開）
- プロジェクトディレクトリ: `/home/noguchilin/projects/dashboard`
- サービスレジストリを読み込んで全サービスの状態を表示

### code-server (Browser-based VSCode)

- 複数インスタンス:
  - 汎用: ポート8889
  - AppleBuyers Writer: ポート8890
  - AppleBuyers Dev: ポート8891
- 各インスタンスは異なるプロジェクトディレクトリをマウント

## Deployment Workflow

1. **Code Push**: mainブランチへpush
2. **GitHub Actions**:
   - Tailscale接続（OAuth経由）
   - Dashboardコード同期（rsync）
   - NixOS設定同期（sparse checkout）
   - `sudo nixos-rebuild switch --flake .#home-lab-01`
3. **Verification**: 主要サービスの稼働確認

**注意**: `enforceDeclarative = true` のサービスは手動再起動不可。NixOS再ビルドが必要。

## Port Management

中央集約: `modules/core/port-management.nix`

主要ポート:
- 3000: Dashboard（HTTPS 443経由）
- 3002: nakamura-misaki Admin UI
- 5678: n8n
- 8222: NATS
- 8384: Syncthing
- 8889-8891: code-server (汎用/Writer/Dev)
- 9000: File Manager
- 10000: nakamura-misaki API（Funnel公開）
- 13006: AppleBuyers Preview

## Testing

```bash
# NixOS設定のビルドテスト
cd nixos-config
nix flake check

# サービステスト用スクリプト
cd tests
./test-dashboard.sh
./test-services.sh
```

## Important Notes

- **宣言的設定を優先**: 手動での設定変更は避け、必ずNixOS設定ファイルに反映
- **Tailscale Funnel制限**: ポート443, 8443, 10000のみサポート
- **Service Registry**: 新サービス追加時は必ず `default.nix` に登録
- **秘密情報管理**: sops-nix経由で必ず暗号化
- **デプロイは自動**: mainへのpushで自動デプロイされるため、テストは慎重に
