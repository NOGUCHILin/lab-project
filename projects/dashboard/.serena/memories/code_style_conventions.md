# Code Style & Conventions - コーディング規約

## TypeScript設定
- **Strict Mode**: 厳格な型チェック有効
- **Target**: ES2017
- **Module Resolution**: bundler (Next.js最適化)
- **JSX**: preserve (Next.js処理)

## ファイル命名規則
- **Components**: PascalCase (ServiceCard.tsx)
- **Hooks**: camelCase with 'use' prefix (useServiceHealth)
- **Types**: PascalCase interfaces (Service, ServiceHealth)
- **Config**: camelCase with descriptive suffix (services.config.ts)

## ディレクトリ構造
```
src/
├── app/                 # Next.js App Router
├── components/          # 再利用可能コンポーネント
│   └── services/        # サービス関連コンポーネント
├── lib/                 # 共有ライブラリ
│   ├── services/        # サービスレジストリシステム
│   └── config/          # 設定ファイル
```

## コーディング規約
- **インポート順序**: 外部ライブラリ → 内部モジュール → 型インポート
- **コメント**: 日本語 JSDoc形式
- **型定義**: 完全な型安全性（unknown型使用、any禁止）
- **関数**: アロー関数優先
- **状態管理**: React Context + Hooks パターン

## コンポーネント設計
- **'use client'**: クライアントコンポーネントに明示的指定
- **Props型定義**: 明示的なinterface定義
- **デフォルト値**: パラメータレベルで設定
- **エラーハンドリング**: loading/error状態の明示的処理

## 型システム
- **厳格な型定義**: Record<string, unknown> 使用
- **Enum**: ServiceStatus等の定数値管理
- **Optional Properties**: ?演算子による明示的オプション
- **Generic Types**: ServiceApiResponse<T = unknown>

## ESLint設定
- **next/core-web-vitals**: Web Vitals最適化
- **next/typescript**: TypeScript統合
- **Ignore Patterns**: .next/, node_modules/, build/