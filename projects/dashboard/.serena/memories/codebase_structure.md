# Codebase Structure - コードベース構造

## ディレクトリ階層
```
unified-dashboard/
├── .husky/                    # Git フック設定
├── .serena/                   # Serena MCP 設定
├── public/                    # 静的アセット
├── scripts/                   # デプロイ・ユーティリティスクリプト
│   └── deploy.sh             # NixOS デプロイスクリプト
├── src/                      # メインソースコード
│   ├── app/                  # Next.js App Router
│   │   ├── api/             # APIルート
│   │   │   └── health/      # ヘルスチェックAPI
│   │   ├── code/            # Code Server統合ページ
│   │   ├── files/           # File Manager統合ページ  
│   │   ├── voice/           # GPT Realtime統合ページ
│   │   ├── layout.tsx       # ルートレイアウト
│   │   ├── page.tsx         # メインダッシュボード
│   │   └── globals.css      # グローバルスタイル
│   ├── components/          # 再利用可能コンポーネント
│   │   └── services/        # サービス関連コンポーネント
│   │       ├── ServiceCard.tsx    # 個別サービスカード
│   │       └── ServiceGrid.tsx    # サービス一覧グリッド
│   └── lib/                 # 共有ライブラリ・ユーティリティ
│       ├── config/          # 設定ファイル
│       │   └── services.config.ts # サービス定義設定
│       └── services/        # サービスレジストリシステム
│           ├── types.ts     # 型定義
│           ├── registry.ts  # レジストリ管理クラス
│           └── hooks.tsx    # React Hooks
├── tests/                    # テストファイル
│   └── e2e/                 # Playwright E2Eテスト
│       ├── dashboard.spec.ts      # ダッシュボード機能
│       ├── api-health.spec.ts     # API健全性
│       ├── error-handling.spec.ts # エラーハンドリング
│       └── performance.spec.ts    # パフォーマンス
└── 設定ファイル
    ├── package.json          # 依存関係・スクリプト
    ├── tsconfig.json         # TypeScript設定
    ├── eslint.config.mjs     # ESLint設定
    ├── next.config.ts        # Next.js設定
    ├── playwright.config.ts  # Playwright設定
    └── postcss.config.mjs    # PostCSS/Tailwind設定
```

## コアファイルの役割
- **services.config.ts**: 新サービス追加時のメイン設定ファイル
- **registry.ts**: サービス管理・ヘルスチェックのシングルトンクラス
- **hooks.tsx**: React Contextとカスタムフック群
- **types.ts**: TypeScript型定義の中央管理
- **ServiceCard/Grid**: UI表示コンポーネント
- **deploy.sh**: E2Eテスト付きNixOSデプロイ自動化

## 拡張ポイント
1. **新サービス追加**: services.config.ts のSERVICES配列
2. **UI カスタマイズ**: components/services/ のコンポーネント
3. **ヘルスチェック拡張**: registry.ts のcheckServiceHealth
4. **テスト追加**: tests/e2e/ に新スペックファイル
5. **API追加**: src/app/api/ に新ルートフォルダ