# nakamura-misaki v4.0.0 - Recovery Plan

**作成日**: 2025-10-14
**状況**: Phase 5 (Slack Bot統合) デプロイ中に問題発生、リカバリー中

---

## 📋 現状の問題サマリー

### 発生した問題

1. **ポート競合**
   - Tailscale Funnel (100.88.235.122:10000) とuvicorn (0.0.0.0:10000) が競合
   - uvicornが起動失敗 `[Errno 98] address already in use`

2. **依存関係不足**
   - `pyproject.toml`に`aiohttp`が記載されていなかった
   - `slack-sdk`がAsyncWebClientを使用するために`aiohttp`が必要

3. **手動操作による技術的負債**
   - 本番環境で`pip install anthropic aiohttp slack-sdk`を手動実行
   - これらは`.venv`内で揮発的（次回再構築時に消える）
   - **NixOSの宣言的管理を破った**

4. **古いディレクトリ構造の残存**
   - `src/adapters/primary/api/`ディレクトリが残っていた
   - `api.py`モジュールとの競合を引き起こした（修正済み）

---

## 🎯 リカバリー戦略

### 原則

1. **すべての変更を宣言的設定に反映する**
2. **手動操作は一切行わない**
3. **ドキュメントを先に書いて、実装との乖離を防ぐ**
4. **クリーンな状態から再デプロイする**

### フェーズ分け

#### Phase A: ドキュメント整理（このフェーズ）

**目的**: 現状を正確に記録し、今後の計画を明確化

**成果物**:
- ✅ `RECOVERY_PLAN_2025-10-14.md`（本ドキュメント）
- 🔄 `CURRENT_STATE_2025-10-14.md`（次に作成）
- 🔄 `PHASE5_IMPLEMENTATION_PLAN.md`（次に作成）
- 🔄 `IMPLEMENTATION_STATUS.md`（更新）

#### Phase B: 宣言的設定の修正

**目的**: すべての変更をNixOS設定とpyproject.tomlに反映

**作業項目**:
1. `pyproject.toml`に`aiohttp`を追加
2. `nakamura-misaki-api.nix`のuvicornバインドアドレスを`127.0.0.1`に変更
3. `.github/workflows/deploy.yml`に依存関係同期ステップを追加

#### Phase C: クリーンデプロイ

**目的**: 手動操作の痕跡を消し、宣言的設定のみでデプロイ

**作業項目**:
1. 本番環境の`.venv`を削除
2. GitHubにpush → 自動デプロイ
3. デプロイ完了確認
4. サービス起動確認

#### Phase D: Slack統合検証

**目的**: Slack Events APIとの統合動作確認

**作業項目**:
1. `/health`エンドポイント確認
2. Slack App設定（Request URL）
3. テストメッセージ送信
4. 署名検証動作確認

---

## 📊 現在の環境状態

### 本番環境 (home-lab-01)

#### サービス状態
- **nakamura-misaki-api.service**: `activating (auto-restart)` (起動失敗中)
- **エラー**: `[Errno 98] address already in use`

#### インストール済みパッケージ（手動操作）
```
anthropic==0.40.0  ← 手動インストール
aiohttp==3.13.0    ← 手動インストール
slack-sdk==3.37.0  ← 手動インストール
fastapi==0.119.0
uvicorn==0.37.0
slack-bolt==1.26.0
```

#### ポート状態
```
100.88.235.122:10000  ← Tailscale Funnel (正常)
0.0.0.0:10000         ← uvicornが起動しようとして失敗
```

#### ファイルシステム
- `~/projects/lab-project/nakamura-misaki/` - 最新コード同期済み
- `.venv/` - 手動で依存関係追加済み（揮発的）
- `src/adapters/primary/api/` - 削除済み ✅

### ローカル環境

#### pyproject.toml
- ❌ `aiohttp`が依存関係に含まれていない
- ✅ その他の依存関係は正しい

#### NixOS設定
- ❌ `nakamura-misaki-api.nix`のバインドアドレスが`0.0.0.0`
- ❌ デプロイワークフローに依存関係同期ステップがない

---

## 🚨 技術的負債リスト

### 高優先度（即座に修正必要）

1. **手動インストールした依存関係**
   - 影響: 次回`.venv`再構築時に消える
   - 対策: `pyproject.toml`に追加

2. **ポート競合**
   - 影響: サービスが起動できない
   - 対策: uvicornを`127.0.0.1:10000`でバインド

3. **デプロイワークフローの不備**
   - 影響: 依存関係が同期されない
   - 対策: `uv sync`または`pip install -e .`を追加

### 中優先度（次回改善）

1. **依存関係管理の明確化**
   - NixOSと`.venv`の責任分離
   - `uv`の本番環境へのインストール検討

2. **ドキュメントの更新頻度**
   - 実装とドキュメントの乖離防止策

---

## 📝 次に作成するドキュメント

### 1. `CURRENT_STATE_2025-10-14.md`

**目的**: 本番環境の正確なスナップショット

**内容**:
- 全サービスの状態
- 全インストール済みパッケージ
- ポート使用状況
- シークレット設定状況
- NixOS設定の現状

### 2. `PHASE5_IMPLEMENTATION_PLAN.md`

**目的**: Phase 5の詳細実装手順

**内容**:
- Slack Events API統合の全ステップ
- チェックリスト形式
- トラブルシューティングガイド
- 成功基準の明確化

### 3. `IMPLEMENTATION_STATUS.md`（更新）

**更新内容**:
- Phase 4を完了に更新
- Phase 5の進捗状況を追加
- 既知の問題セクションを追加

---

## 🔍 ドキュメント戦略

### Anthropicのベストプラクティス適用

#### 1. 最小限の高シグナルトークン
- 冗長な説明を避ける
- 具体的な数値・コマンド・ファイルパスを記載
- 「やるべきこと」を明確に

#### 2. 構造化
- XMLタグ/Markdown見出しで明確に区分
- チェックリスト形式を活用
- 表形式で比較情報を提示

#### 3. タスク指向
- 「何をすべきか」を中心に記述
- 「なぜそうなったか」は簡潔に
- コマンド例を必ず含める

### ドキュメント配置ルール

#### `nakamura-misaki/docs/`
- **IMPLEMENTATION_STATUS.md** - 実装完了状況（常に最新）
- **IMPLEMENTATION_PLAN.md** - 元々の計画（変更しない）
- **DEPLOYMENT_GUIDE.md** - デプロイ手順（汎用）
- **RECOVERY_PLAN_YYYY-MM-DD.md** - リカバリー計画（履歴）
- **CURRENT_STATE_YYYY-MM-DD.md** - 環境スナップショット（履歴）
- **PHASE*_IMPLEMENTATION_PLAN.md** - フェーズ別詳細計画

#### `lab-project/claudedocs/`
- **deployment.md** - NixOS全体のデプロイ手順
- **service-registry.md** - Service Registryパターン
- **troubleshooting.md** - 一般的なトラブルシューティング

---

## ✅ 成功基準

### Phase A完了条件
- [x] `RECOVERY_PLAN_2025-10-14.md` 作成
- [ ] `CURRENT_STATE_2025-10-14.md` 作成
- [ ] `PHASE5_IMPLEMENTATION_PLAN.md` 作成
- [ ] `IMPLEMENTATION_STATUS.md` 更新

### Phase B完了条件
- [ ] `pyproject.toml`に`aiohttp`追加
- [ ] `nakamura-misaki-api.nix`修正
- [ ] `deploy.yml`修正
- [ ] コミット・プッシュ完了

### Phase C完了条件
- [ ] 本番`.venv`削除
- [ ] デプロイ成功
- [ ] `nakamura-misaki-api.service`が`active (running)`
- [ ] `/health`エンドポイントが200 OK

### Phase D完了条件
- [ ] Slack App設定完了
- [ ] URL Verification成功
- [ ] テストメッセージで応答確認
- [ ] 署名検証動作確認

---

Generated with [Claude Code](https://claude.com/claude-code)
