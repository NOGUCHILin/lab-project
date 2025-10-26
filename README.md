# lab-project

NixOS統合環境 - 全プロジェクト・NixOS設定を統合管理する統合リポジトリ

## 📋 概要

**目的**: 全プロジェクト・NixOS設定を統合管理する統合リポジトリ
**構成**: 複数プロジェクト（frontend, backend, dashboard, nakamura-misaki等）+ NixOS設定
**デプロイ**: GitHub Actions経由で完全自動化

## 🗂️ ディレクトリ構成

```
lab-project/                     # リポジトリルート
├── nixos-config/                # NixOS設定（flake.nixはここ）
│   ├── flake.nix               # NixOS設定のエントリーポイント
│   ├── hosts/home-lab-01/      # ホスト固有設定
│   │   └── configuration.nix
│   ├── modules/                # 再利用可能なモジュール
│   │   ├── core/               # 基盤設定（ポート管理、SSH等）
│   │   ├── networking/         # Tailscale VPN
│   │   └── services/           # サービス定義
│   │       ├── registry/       # Service Registry（各サービス定義）
│   │       └── tailscale-direct.nix
│   ├── packages/               # カスタムパッケージ
│   ├── secrets/                # sops-nix暗号化シークレット
│   ├── users/                  # ユーザー設定
│   └── docs/                   # NixOS固有ドキュメント
│
├── projects/                    # 各Webサービスのソースコード
│   ├── dashboard/              # Next.js 統合ダッシュボード
│   ├── nakamura-misaki/        # Slack Bot API (FastAPI)
│   ├── code-server/            # ブラウザ版VS Code
│   ├── filebrowser/            # Webファイル管理
│   └── nats/                   # NATS messaging
│
├── claudedocs/                  # Claude Code用詳細ドキュメント
│   ├── service-registry.md     # Service Registry実装ガイド
│   ├── nextjs-nix-best-practices.md  # Next.js+Nix統合ベストプラクティス
│   ├── technical-debt-cicd.md  # CI/CD改善ガイド
│   └── webui-real-data-implementation.md  # Web UI実装ガイド
│
├── .github/workflows/           # CI/CD（自動デプロイ）
├── .serena/                     # Serena MCP設定
├── CLAUDE.md                    # Claude Code用プロジェクト設定
└── README.md                    # このファイル
```

**重要**: NixOSコマンド（`nix flake check`等）は`nixos-config/`ディレクトリで実行してください。

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
