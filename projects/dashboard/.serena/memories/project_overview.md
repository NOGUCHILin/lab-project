# Unified Dashboard - プロジェクト概要

## プロジェクトの目的
NixOS上で動作する複数のバックエンドサービスを一元管理するための統合ダッシュボード。
OpenAI Realtime API、Code Server、Syncthing、NATS、MediaMTXなどのサービスを
スケーラブルなサービスレジストリアーキテクチャで管理する。

## 主要機能
- サービスレジストリパターンによる動的サービス管理
- リアルタイムヘルスチェック機能（30秒間隔）
- 自動サービス検出とステータス監視
- Tailscale Serve経由のHTTPSアクセス対応
- レスポンシブデザイン（モバイル対応）
- TypeScriptによる型安全性保証

## 技術スタック
- **フロントエンド**: Next.js 15 (App Router)
- **言語**: TypeScript (strict mode)
- **UI**: React 19 + Tailwind CSS 4
- **状態管理**: React Context + Hooks
- **テスト**: Playwright E2E
- **リンター**: ESLint (next/typescript)
- **ランタイム**: Node.js + Turbopack

## アーキテクチャ
- **サービスレジストリ型**: 設定ファイルによる宣言的サービス管理
- **ヘルスチェック**: 30秒TTLキャッシュ付き自動監視
- **React Context**: アプリケーション全体でのサービス状態共有
- **コンポーネント駆動**: ServiceCard/ServiceGrid による再利用可能UI

## デプロイメント環境
- **OS**: NixOS (宣言的システム管理)
- **ネットワーク**: Tailscale VPN + Serve (HTTPS)
- **開発環境**: Turbopack による高速ビルド
- **CI/CD**: Husky + lint-staged による品質管理