# CI/CD技術的負債と対策

**作成日**: 2025-10-23
**状態**: 🔴 Critical - 高頻度でCI/CDが失敗している

---

## 📊 エラー頻度分析

### 過去20回のWorkflow実行結果

| Workflow | 成功 | 失敗 | 成功率 |
|----------|------|------|--------|
| **deploy.yml** | 17回 | 3回 | 85% ✅ |
| **test.yml (Dashboard)** | **0回** | **20回** | **0% 🔴** |
| **test-nakamura-misaki.yml** | 20回 | 0回 | 100% ✅ |

**結論**: Dashboardのテストワークフローが**完全に機能していない**。

---

## 🔥 致命的な問題（優先度: 最高）

### 1. Dashboard E2Eテストの不正なURL生成

**問題箇所**: `projects/dashboard/tests/e2e/api-health.spec.ts:20`

```typescript
// ❌ 不正なURL構築
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || baseURL || 'http://localhost';
const CODE_SERVER_PORT = process.env.NEXT_PUBLIC_CODE_SERVER_PORT || '8889';
const codeServerResponse = await request.get(`${BASE_URL}:${CODE_SERVER_PORT}`, {
```

**結果**:
```
// BASE_URL = "http://localhost:3005" の場合
// ポート番号が二重に追加される
http://localhost:3005:8889 ← Invalid URL
```

**エラーログ**:
```
TypeError: apiRequestContext.get: Invalid URL
url: 'http://localhost:3005:8889'
```

**影響**: 全E2Eテストが失敗

**根本原因**:
- `baseURL`は完全なURL（プロトコル+ホスト+ポート）を含む
- それに対してさらにポート番号を追加している

**修正方法**:
```typescript
// ✅ 正しい実装
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://home-lab-01.tail4ed625.ts.net';
const CODE_SERVER_PORT = process.env.NEXT_PUBLIC_CODE_SERVER_PORT || '8889';

// URLオブジェクトを使用してホスト名だけ取得
const url = new URL(BASE_URL);
const codeServerUrl = `${url.protocol}//${url.hostname}:${CODE_SERVER_PORT}`;
const codeServerResponse = await request.get(codeServerUrl, {
```

---

### 2. Dashboardビルド時の`services.json`依存

**問題**: ビルド時に `/etc/unified-dashboard/services.json` の読み込みが失敗

**エラーログ** (test.yml run 18740071005):
```
Error loading services: Error: ENOENT: no such file or directory,
open '/etc/unified-dashboard/services.json'
```

**影響**: CI環境でビルドは完了するが警告が出る（実運用では問題）

**根本原因**:
- Next.jsのビルド時にSSG（Static Site Generation）で`services.json`を読み込もうとしている
- CI環境には本番環境のファイルが存在しない

**対策**:
1. **短期**: ビルド時は動的レンダリング（SSR）に切り替え
2. **中期**: `services.json`のモックをCI環境に用意
3. **長期**: Service Registryから直接データ取得（API化）

---

### 3. Next.js + Nix統合の不安定さ

**10/21の14回連続失敗の内訳**:

| 失敗原因 | 回数 | 詳細 |
|---------|------|------|
| npmDepsHash不一致 | 6回 | package-lock.json変更後、ハッシュ更新忘れ |
| TypeScript設定エラー | 4回 | tsconfig.json未含まれ、パス解決失敗 |
| ESLintエラー | 2回 | 本番ビルドで初めて検出されるエラー |
| devDependencies不足 | 2回 | TailwindCSSなどのビルド依存が欠落 |

**根本原因**: Next.js + Nix の組み合わせは**ドキュメント不足で試行錯誤が必要**

**ユーザーの仮説は正しい**: 「NixOSのドキュメントが少なくて間違えが多くて安定しない」

---

## ⚠️ その他の問題

### 4. ポート設定の混乱

**問題**: test.ymlとplaywright.configでポート番号が一致しない可能性

- `test.yml:106`: `PORT=3000`でサーバー起動
- `playwright.config.js:15`: `baseURL: 'http://localhost:3000'`
- しかし、実際のテスト失敗ログでは`localhost:3005`への接続エラー

**原因不明**: 環境変数が上書きされている？

---

### 5. 統合テストの無効化（nakamura-misaki）

`test-nakamura-misaki.yml:75`:
```yaml
- name: Run integration tests
  if: false  # 新しいDDDコンテキスト用の統合テストは未作成のため一時的にスキップ
```

**影響**: データベース連携、Slack API連携のバグが本番で発覚するリスク

---

## 📋 技術的負債リスト

### 優先度: 🔴 Critical（即時対応）

- [ ] **Dashboard E2EテストのURL構築修正** (api-health.spec.ts:20)
  - 推定工数: 1時間
  - 影響範囲: 全E2Eテスト
  - 担当者: TBD

- [ ] **Dashboardのservices.json依存解消**
  - 推定工数: 4時間
  - 影響範囲: ビルドプロセス
  - 担当者: TBD

### 優先度: 🟡 High（今週中）

- [ ] **Nix buildNpmPackageの安定化**
  - npmDepsHash自動更新スクリプト作成
  - 推定工数: 2時間
  - 担当者: TBD

- [ ] **pre-commit hookにnpm run lintを追加**
  - ESLintエラーをコミット前に検出
  - 推定工数: 30分
  - 担当者: TBD

- [ ] **Dashboard E2Eテストのポート設定統一**
  - 環境変数の整理
  - 推定工数: 1時間
  - 担当者: TBD

### 優先度: 🟢 Medium（今月中）

- [ ] **nakamura-misaki統合テスト再有効化**
  - DDD再設計後に対応
  - 推定工数: 8時間
  - 担当者: TBD

- [ ] **Dashboardのエラーハンドリング追加**
  - try/catchの追加
  - Error Boundary実装
  - 推定工数: 6時間
  - 担当者: TBD

- [ ] **Dashboardの構造化ログ導入**
  - Winston/Pino導入
  - 推定工数: 4時間
  - 担当者: TBD

### 優先度: 🔵 Low（必要時）

- [ ] **AppleBuyers PreviewのFlake化**
  - rsync→宣言的デプロイに移行
  - 推定工数: 6時間
  - 担当者: TBD

- [ ] **DEBUG環境変数の本番環境確認**
  - 推定工数: 10分
  - 担当者: TBD

---

## 💡 根本対策

### 1. Next.js + Nix ベストプラクティスの確立

**問題**: Next.jsとNixの組み合わせはドキュメント不足で試行錯誤が多い

**対策**:
- ✅ **既に作成済み**: `claudedocs/nextjs-nix-best-practices.md`
- 📝 **今後追加**: CI/CD特有のトラブルシューティング

**参考ドキュメント**:
- `claudedocs/nextjs-nix-best-practices.md`
- Nix公式: https://nixos.org/manual/nixpkgs/stable/#javascript
- Next.js + Nix community examples

---

### 2. CI/CDパイプラインの段階的改善

**現状**: テスト失敗→手動修正→再push→また失敗→...の繰り返し

**改善案**:

#### Phase 1: 即時修正（今日）
```bash
# 1. Dashboard E2EテストのURL修正
# 2. playwright.config.jsのポート確認
```

#### Phase 2: 自動化（今週）
```bash
# 1. npmDepsHash自動更新
nix run nixpkgs#nix-update -- --flake --version=skip dashboard

# 2. pre-commit hook強化
cat <<EOF >> .pre-commit-config.yaml
  - repo: local
    hooks:
      - id: npm-lint
        name: npm lint (Dashboard)
        entry: bash -c 'cd projects/dashboard && npm run lint'
        language: system
        files: ^projects/dashboard/
EOF
```

#### Phase 3: 監視強化（今月）
```yaml
# .github/workflows/test.yml に追加
- name: Save build logs
  if: failure()
  run: |
    mkdir -p build-logs
    npm run build > build-logs/build.log 2>&1 || true

- name: Upload build logs
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: build-logs
    path: build-logs/
```

---

### 3. ローカルテスト戦略

**問題**: CI環境でしか検出されないエラーが多い

**対策**:

```bash
# ローカルで本番ビルドを必ずテスト
cd projects/dashboard

# 1. Nixビルドテスト（CI環境に近い）
nix build .#dashboard --no-link --print-build-logs

# 2. 通常ビルドテスト
npm run build

# 3. E2Eテスト
npm start &
npm run test
```

**pre-push フック** (既に存在、強化版):
```bash
# projects/dashboard/.git/hooks/pre-push
#!/bin/bash
cd projects/dashboard
npm run lint && npm run build && nix build .#dashboard --no-link
```

---

## 📈 成功指標

### 短期目標（1週間）
- [ ] Dashboard test.yml 成功率 **0% → 80%以上**
- [ ] E2Eテスト全pass
- [ ] npmDepsHash更新の自動化

### 中期目標（1ヶ月）
- [ ] Dashboard test.yml 成功率 **95%以上**
- [ ] 統合テスト再有効化
- [ ] CI実行時間 **5分以内**

### 長期目標（3ヶ月）
- [ ] 全Workflow 成功率 **98%以上**
- [ ] ゼロダウンタイムデプロイ
- [ ] 自動ロールバックの実績

---

## 🔗 関連ドキュメント

- `claudedocs/nextjs-nix-best-practices.md` - Next.js+Nixベストプラクティス
- `claudedocs/service-registry.md` - Service Registryパターン
- `CLAUDE.md` - プロジェクト全体の制約とルール
- `.github/workflows/deploy.yml` - 本番デプロイワークフロー
- `.github/workflows/test.yml` - Dashboardテストワークフロー

---

## ✅ 次のアクション

### 今日やること:
1. ✅ この技術的負債ドキュメント作成（完了）
2. 🔲 Dashboard E2EテストのURL修正（api-health.spec.ts）
3. 🔲 playwright.config.jsのポート設定確認

### 今週やること:
1. npmDepsHash自動更新スクリプト作成
2. pre-commit hookにnpm run lint追加
3. services.json依存解消の設計

### ユーザーへの確認事項:
- この分析は正しいか？
- 最優先で修正すべき項目は何か？
- すぐに修正作業を開始するか、それとも他の作業優先か？
