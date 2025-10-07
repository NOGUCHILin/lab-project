# Task Completion Checklist - タスク完了チェックリスト

## 基本品質チェック
- [ ] **ESLint**: `npm run lint` で警告・エラーなし
- [ ] **TypeScript**: 型エラーなし (ビルド時確認)
- [ ] **ビルド**: `npm run build` で成功
- [ ] **E2Eテスト**: `npm run test` で全テスト通過

## コード品質
- [ ] **型安全性**: unknownタイプ使用、any禁止
- [ ] **命名規則**: ファイル・関数・変数の一貫性
- [ ] **コメント**: 日本語JSDocでの説明
- [ ] **エラーハンドリング**: 適切なtry-catch、loading/error状態

## サービスレジストリ特有
- [ ] **型定義**: src/lib/services/types.ts の更新
- [ ] **設定追加**: src/lib/config/services.config.ts への登録
- [ ] **ヘルスチェック**: 正常なhealth endpoint応答
- [ ] **コンポーネント**: ServiceCard/ServiceGrid での表示確認

## テスト要件
- [ ] **E2E Coverage**: 新機能のPlaywrightテスト追加
- [ ] **エラーケース**: 異常系のテストケース
- [ ] **レスポンシブ**: モバイル/デスクトップでの動作確認
- [ ] **パフォーマンス**: 基本性能要件クリア

## デプロイ前チェック
- [ ] **ローカル動作**: `npm run dev` で正常動作
- [ ] **プロダクションビルド**: `npm run build && npm run start`
- [ ] **lint-staged**: コミット時の自動チェック通過
- [ ] **スクリプト**: `./scripts/deploy.sh` での統合テスト

## NixOS環境固有
- [ ] **システム統合**: NixOS設定ファイルへの反映
- [ ] **Tailscale**: HTTPSアクセスの動作確認
- [ ] **サービス起動**: systemctl でのサービス状態確認
- [ ] **ログ確認**: journalctl でのエラーログチェック

## 追加確認項目
- [ ] **メモリリーク**: 長時間動作でのリソース使用量
- [ ] **セキュリティ**: 不要な露出エンドポイントなし
- [ ] **アクセシビリティ**: 基本的なa11y要件
- [ ] **ドキュメント**: README・設定ファイルの更新