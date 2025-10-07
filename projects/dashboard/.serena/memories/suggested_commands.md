# Suggested Commands - 推奨コマンド集

## 開発用コマンド
```bash
# 開発サーバー起動 (Turbopack使用)
npm run dev

# プロダクションビルド (Turbopack使用)
npm run build

# プロダクションビルド (Nix環境用)
npm run build:nix

# プロダクションサーバー起動
npm run start
```

## 品質管理コマンド
```bash
# ESLint実行
npm run lint

# E2Eテスト実行
npm run test

# E2EテストUI実行
npm run test:ui

# テストレポート表示
npm run test:report
```

## デプロイメント
```bash
# NixOS デプロイ (E2Eテスト込み)
npm run deploy

# または直接スクリプト実行
./scripts/deploy.sh
```

## Git & 品質管理
```bash
# Husky準備 (初回のみ)
npm run prepare

# コミット前自動実行 (lint-staged設定済み)
# - ESLint自動修正
# - E2Eテスト実行
```

## システム固有コマンド (NixOS)
```bash
# システム設定更新
sudo nixos-rebuild switch --flake /home/noguchilin/nixos-config#nixos

# サービス状態確認
systemctl status [service-name]

# ログ確認
journalctl -u [service-name] -f
```

## 開発ツール
```bash
# 依存関係インストール
npm install

# パッケージ追加
npm install [package-name]

# 開発依存関係追加
npm install --save-dev [package-name]
```

## Playwright特有
```bash
# ブラウザインストール (必要時)
npx playwright install

# 特定テストファイル実行
npx playwright test tests/e2e/dashboard.spec.ts

# デバッグモード
npx playwright test --debug
```

## Tailscale (ネットワーク)
```bash
# Tailscale状態確認
tailscale status

# Tailscale Serve設定確認
tailscale serve status
```