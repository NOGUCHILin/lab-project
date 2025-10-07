# Public Site NixOS自動デプロイ設定ガイド

**作成日**: 2025-10-07
**対象**: applebuyers_application/public-site
**目的**: NixOSサーバーへの自動デプロイ環境構築

---

## 📋 背景・目的

### 現状
- **public-site**: Next.js 15で構築された買取サイト（このリポジトリ内）
- **デプロイ先**:
  - 本番環境: Vercel
  - 開発/ライター環境: NixOSサーバー（Tailscale経由）

### 実現したいこと
1. **自動デプロイ**: `main`ブランチへのpush → NixOSに自動反映
2. **ライター環境**: Code Serverで記事（Markdown）編集 → リアルタイムプレビュー
3. **開発者環境**: ローカルで開発 → push → NixOSで確認可能

### NixOSサーバー情報
- **ホスト**: `home-lab-01`（Tailscale MagicDNS）
- **Tailscale IP**: `100.88.235.122`
- **ユーザー**: `noguchilin`
- **配置先**: `~/projects/applebuyers_application/public-site/`
- **ポート**: `13005`（開発サーバー）

---

## 🏗️ アーキテクチャ

### デプロイフロー
```
[開発者/ライター]
  ↓ git push origin main
[GitHub: applebuyers_application]
  ↓ GitHub Actions (.github/workflows/deploy-public-site.yml)
  ↓ Tailscale接続
[NixOS Server]
  ↓ git pull
  ↓ pnpm install && pnpm build
  ↓ systemctl restart
[public-site running on port 13005]
```

### NixOS側のディレクトリ構成
```
[NixOS] ~/projects/applebuyers_application/
└── public-site/              # Git Sparse Checkout
    ├── src/
    ├── content/articles/     # ライター編集領域
    ├── package.json
    └── ...

[NixOS] ~/nixos-config/       # 別リポジトリ (lab-project)
└── projects/
    └── applebuyers-public-site/
        └── service.nix       # systemdサービス定義
```

---

## ⚙️ 実装手順

### Phase 1: GitHub Actions設定

#### 1-1. ワークフローファイル作成
**ファイル**: `.github/workflows/deploy-public-site.yml`

```yaml
name: Deploy Public Site to NixOS

on:
  push:
    branches: [main]
    paths:
      - 'public-site/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # Tailscale接続
      - name: Connect to Tailscale
        uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci

      # NixOSにデプロイ
      - name: Deploy to NixOS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.NIXOS_HOST }}
          username: ${{ secrets.NIXOS_USER }}
          key: ${{ secrets.NIXOS_SSH_KEY }}
          script: |
            cd ~/projects/applebuyers_application
            git stash
            git pull origin main
            cd public-site
            pnpm install
            pnpm build
            sudo systemctl restart applebuyers-public-site.service

      # デプロイ確認
      - name: Verify deployment
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.NIXOS_HOST }}
          username: ${{ secrets.NIXOS_USER }}
          key: ${{ secrets.NIXOS_SSH_KEY }}
          script: |
            systemctl is-active applebuyers-public-site.service
            echo "✅ Public site deployed successfully"
```

#### 1-2. GitHub Secrets設定
**必要なSecrets** (リポジトリ設定 → Secrets and variables → Actions):

```bash
# Tailscale OAuth認証情報
TS_OAUTH_CLIENT_ID=kUxKjniuWt11CNTRL
TS_OAUTH_SECRET=tskey-client-kUxKjniuWt11CNTRL-2hTcY6K7RwKh6GQsR76XwKaoKX9VskUd

# NixOS SSH接続情報
NIXOS_HOST=100.88.235.122
NIXOS_USER=noguchilin
NIXOS_SSH_KEY=<SSH秘密鍵の内容>
```

**SSH鍵取得方法**:
```bash
# ローカルMacで実行
cat ~/.ssh/github-actions-deploy
```
鍵の内容全体をコピーして`NIXOS_SSH_KEY`に設定

---

### Phase 2: NixOS初期セットアップ

#### 2-1. Sparse Checkout初期化
**NixOSサーバーで実行**:
```bash
# プロジェクトディレクトリ作成
cd ~/projects
git clone --filter=blob:none --no-checkout \
  https://github.com/NOGUCHILin/applebuyers_application.git
cd applebuyers_application

# public-siteのみをチェックアウト
git sparse-checkout init --cone
git sparse-checkout set public-site
git checkout main

# 依存関係インストール
cd public-site
pnpm install
pnpm build
```

#### 2-2. systemdサービス定義作成
**lab-projectリポジトリで作成**:

**ファイル**: `nixos-config/projects/applebuyers-public-site/service.nix`

```nix
{ config, pkgs, ... }:

{
  systemd.services.applebuyers-public-site = {
    description = "AppleBuyers Public Site (Next.js)";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "simple";
      User = "noguchilin";
      WorkingDirectory = "/home/noguchilin/projects/applebuyers_application/public-site";
      ExecStart = "${pkgs.nodejs_22}/bin/node node_modules/.bin/next start -p 13005";
      Restart = "always";
      RestartSec = "10s";

      # Environment
      Environment = [
        "NODE_ENV=production"
        "PORT=13005"
      ];

      # Security
      ProtectSystem = "strict";
      ProtectHome = "read-only";
      PrivateTmp = true;
      NoNewPrivileges = true;
    };
  };

  # ファイアウォール設定
  networking.firewall.allowedTCPPorts = [ 13005 ];
}
```

#### 2-3. flake.nixに追加
**ファイル**: `nixos-config/flake.nix`

```nix
nixosConfigurations.home-lab-01 = nixpkgs.lib.nixosSystem {
  modules = [
    # ... 既存のモジュール ...

    # AppleBuyers Public Site
    ../projects/applebuyers-public-site/service.nix
  ];
};
```

#### 2-4. NixOS設定適用
```bash
# lab-projectリポジトリで実行
cd ~/dev/lab-project
git add nixos-config/projects/applebuyers-public-site/service.nix
git add nixos-config/flake.nix
git commit -m "feat: AppleBuyers Public Site自動デプロイ設定"
git push origin main
```

GitHub Actionsが自動実行され、NixOSに反映されます。

---

### Phase 3: Nginx設定（オプション）

**サブドメインでアクセスしたい場合**:

**ファイル**: `nixos-config/modules/nginx.nix`に追加

```nix
virtualHosts."applebuyers.home-lab-01.tail4ed625.ts.net" = {
  locations."/" = {
    proxyPass = "http://localhost:13005";
    proxyWebsockets = true;
    extraConfig = ''
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    '';
  };
};
```

---

## 🧪 動作確認

### 1. GitHub Actionsの確認
```bash
# ローカルでpublic-siteを変更してpush
cd ~/dev/applebuyers_application/public-site
echo "test" >> README.md
git add README.md
git commit -m "test: GitHub Actions動作確認"
git push origin main
```

GitHub Actionsタブで実行状況を確認:
- https://github.com/NOGUCHILin/applebuyers_application/actions

### 2. サービス状態確認
```bash
# NixOSで確認
ssh nixos "systemctl status applebuyers-public-site.service"
```

### 3. アクセス確認
- **直接アクセス**: `http://100.88.235.122:13005/`
- **Tailscale DNS**: `http://home-lab-01.tail4ed625.ts.net:13005/`
- **Nginxサブドメイン**: `https://applebuyers.home-lab-01.tail4ed625.ts.net/`

---

## 📝 ライター向け作業フロー

### Code Serverで記事編集
1. Code Serverにアクセス: `https://code.home-lab-01.tail4ed625.ts.net/`
2. `~/projects/applebuyers_application/public-site/content/articles/` を開く
3. Markdown記事を編集
4. ターミナルで：
   ```bash
   cd ~/projects/applebuyers_application/public-site
   pnpm dev:network  # プレビューサーバー起動（ポート13005）
   ```
5. ブラウザで `http://home-lab-01.tail4ed625.ts.net:13005/` を開いてプレビュー
6. 編集完了後、Git操作：
   ```bash
   git add content/articles/
   git commit -m "記事追加: ○○について"
   git push origin main
   ```
7. GitHub Actionsが自動実行 → 本番反映

---

## 🔧 トラブルシューティング

### サービスが起動しない
```bash
# ログ確認
ssh nixos "journalctl -u applebuyers-public-site.service -n 50"

# 手動起動テスト
ssh nixos "cd ~/projects/applebuyers_application/public-site && pnpm dev"
```

### ビルドエラー
```bash
# 依存関係を再インストール
ssh nixos "cd ~/projects/applebuyers_application/public-site && rm -rf node_modules .next && pnpm install && pnpm build"
```

### Git pull失敗
```bash
# 未コミット変更を退避
ssh nixos "cd ~/projects/applebuyers_application && git stash && git pull origin main"
```

---

## 🎯 次のステップ

### 完了チェックリスト
- [ ] GitHub Actions作成（`.github/workflows/deploy-public-site.yml`）
- [ ] GitHub Secrets設定（6つのSecret）
- [ ] NixOS Sparse Checkout初期化
- [ ] service.nix作成
- [ ] flake.nix更新
- [ ] 動作確認（push → 自動デプロイ）
- [ ] ライター向けガイド作成

### オプション機能
- [ ] Nginxサブドメイン設定
- [ ] Slackデプロイ通知
- [ ] エラー時の自動ロールバック

---

## 📚 参考リンク

- **lab-project**: https://github.com/NOGUCHILin/lab-project
- **Tailscale管理画面**: https://login.tailscale.com/admin
- **GitHub Actions**: https://github.com/NOGUCHILin/applebuyers_application/actions

---

**質問・問題があれば**: このドキュメントを共有してClaude Codeに相談してください。
