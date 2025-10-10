# lab-project

NixOS統合環境 - 全プロジェクト・NixOS設定を統合管理する統合リポジトリ

## 📋 概要

**目的**: 全プロジェクト・NixOS設定を統合管理する統合リポジトリ
**構成**: 複数プロジェクト（frontend, backend, dashboard, nakamura-misaki等）+ NixOS設定
**デプロイ**: GitHub Actions経由で完全自動化

## 🗂️ ディレクトリ構成

```
lab-project/
├── projects/                  # 全サービス統一管理
│   ├── dashboard/             # Next.js 22 統合ダッシュボード
│   ├── nakamura-misaki/       # Claude Agent (FastAPI + Next.js)
│   ├── code-server/           # ブラウザ版VSCode
│   ├── filebrowser/           # Webファイル管理
│   └── nats/                  # NATS messaging
│
├── nixos-config/              # NixOS設定
│   ├── flake.nix              # 各projects/*/service.nixをimport
│   ├── hosts/home-lab-01/
│   ├── modules/
│   │   ├── core/
│   │   ├── development/
│   │   ├── networking/
│   │   └── security/
│   └── users/
│
├── scripts/                   # デプロイ・管理スクリプト
├── .github/workflows/         # 自動デプロイ
└── docs/                      # ドキュメント
```

## 🚀 デプロイフロー

```
ローカル開発 → git push → GitHub Actions → deploy-rs → NixOS本番
     ↓             ↓            ↓              ↓           ↓
  コード編集       main      ワークフロー   自動デプロイ  宣言的更新
```

## 🛠️ 技術スタック

- **NixOS**: Flakes有効、宣言的設定管理
- **deploy-rs**: 自動ロールバック対応の宣言的デプロイ
- **systemd**: サービス管理
- **Tailscale**: VPN・アクセス管理
- **GitHub Actions**: CI/CD
- **sops-nix**: シークレット管理

## 📚 ドキュメント

詳細は `/Users/noguchilin/dev/nixos-deploy-plan.md` を参照

## 🔄 デプロイ方法

mainブランチへのpushで自動的にdeploy-rsが実行され、NixOS本番環境に反映されます。
