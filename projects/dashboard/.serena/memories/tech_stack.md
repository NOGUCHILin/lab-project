# Tech Stack - 技術スタック詳細

## フロントエンド
- **Next.js 15.5.2** - App Router使用
- **React 19.1.0** - 最新の React Server Components
- **TypeScript 5** - 厳格な型チェック有効

## スタイリング
- **Tailwind CSS 4** - PostCSS統合
- **レスポンシブデザイン** - モバイルファースト
- **カスタムコンポーネント** - ServiceCard/ServiceGrid

## 開発ツール
- **ESLint 9** - next/typescript設定
- **Playwright 1.55.0** - E2Eテスト
- **Husky 9.1.7** - Gitフック管理
- **lint-staged 16.1.6** - ステージングファイル処理
- **Turbopack** - 高速バンドラー

## サービス管理
- **Service Registry Pattern** - 動的サービス管理
- **Health Check System** - 30秒TTLキャッシュ
- **React Context** - 状態管理とProviderパターン
- **TypeScript Interfaces** - 完全な型安全性

## ビルド・デプロイ
- **Node.js** - サーバーランタイム
- **NixOS** - システムレベルパッケージ管理
- **Tailscale Serve** - HTTPS プロキシ
- **Chromium (NixOS)** - E2Eテスト用ブラウザ

## 依存関係
### Production Dependencies
- next: 15.5.2
- react: 19.1.0
- react-dom: 19.1.0

### Development Dependencies
- @playwright/test: ^1.55.0
- @tailwindcss/postcss: ^4
- @types/node: ^20
- @types/react: ^19
- @types/react-dom: ^19
- eslint: ^9
- eslint-config-next: 15.5.2
- husky: ^9.1.7
- lint-staged: ^16.1.6
- tailwindcss: ^4
- typescript: ^5