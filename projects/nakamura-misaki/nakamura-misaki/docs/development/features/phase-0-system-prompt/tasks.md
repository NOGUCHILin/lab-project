# Phase 0: System Prompt - Tasks

## Implementation Checklist

### 1. System Prompt Creation

- [ ] **1.1** `config/prompts/default.json.v3.0.0.backup` を作成（バックアップ）
- [ ] **1.2** `config/prompts/default.json` をv4.0.0に更新
  - [ ] `version`: `"4.0.0"`
  - [ ] `description`: "nakamura-misaki v4.0.0 - 草薙素子風タスク管理特化プロンプト"
  - [ ] `metadata.personality`: `"kusanagi_motoko_rookie"`
  - [ ] `metadata.version_notes`: v4.0.0の変更内容を記述
  - [ ] `system_prompt`: XML構造で草薙素子風プロンプトを記述
    - [ ] `<role>`: 性格・役割・できないこと
    - [ ] `<context>`: 動的変数（`{user_id}`, `{workspace_path}`, `{channel_type}`, `{task_context}`, `{saved_notes}`）
    - [ ] `<tone>`: 応答スタイル（簡潔・直接的・的確・論理的）
    - [ ] `<rules>`: 基本動作・タスク管理・ハンドオフ・内部情報管理・できないこと
    - [ ] `<examples>`: 5つの例（タスク確認・間違い指摘・ハンドオフ・ノート検索・不足情報確認）
- [ ] **1.3** `config/prompts/technical.json` に非推奨マークを追加
  - [ ] `metadata.deprecated`: `true`
  - [ ] `metadata.deprecation_reason`: "v4.0.0からタスク管理に特化（技術サポートは非対応）"
- [ ] **1.4** `config/prompts/schedule.json` に非推奨マークを追加
  - [ ] `metadata.deprecated`: `true`
  - [ ] `metadata.deprecation_reason`: "v4.0.0でdefault.jsonに統合"

### 2. Code Implementation

- [ ] **2.1** `src/adapters/secondary/claude_adapter.py` を更新
  - [ ] `_generate_task_context()` メソッドを追加
    ```python
    async def _generate_task_context(self, user_id: str) -> str:
        """Generate task context for system prompt

        Phase 0: Returns empty string (not yet implemented)
        Phase 2: Returns today's tasks and pending handoffs
        """
        # TODO: Phase 2でタスク取得ロジック実装
        return ""
    ```
  - [ ] `send_message()` で `_generate_task_context()` を呼び出し
    ```python
    task_context = await self._generate_task_context(user_id)
    system_prompt = system_prompt.replace("{task_context}", task_context)
    ```
- [ ] **2.2** 既存の変数置換ロジックが正しく動作するか確認（`{user_id}`, `{workspace_path}`, `{channel_type}`, `{saved_notes}`）

### 3. Testing

#### 3.1 Unit Tests
- [ ] **3.1.1** `tests/unit/test_claude_adapter.py` を作成
  - [ ] `test_variable_replacement_phase0`: 変数置換が正しく動作
  - [ ] `test_task_context_empty_in_phase0`: `{task_context}` が空文字列
  - [ ] `test_kusanagi_personality_prompt_structure`: XML構造が正しい
  - [ ] `test_fallback_prompt_loading`: フォールバックプロンプトが動作

#### 3.2 Integration Tests
- [ ] **3.2.1** `tests/integration/test_prompt_loading.py` を作成
  - [ ] `test_load_v4_default_prompt`: default.json v4.0.0が読み込める
  - [ ] `test_prompt_cache_hit`: キャッシュが正しく動作
  - [ ] `test_prompt_file_change_detection`: ファイル変更検知（`st_mtime`）が動作
  - [ ] `test_deprecated_prompts_loading`: 非推奨プロンプトも読み込める（警告あり）

#### 3.3 E2E Tests
- [ ] **3.3.1** `tests/e2e/test_kusanagi_personality.py` を作成
  - [ ] `test_concise_response`: 簡潔な応答（1-3文）
  - [ ] `test_direct_answer_to_question`: 質問には直接答える
  - [ ] `test_refuse_code_review_with_alternative`: コードレビューは断り、代替案を提示
  - [ ] `test_point_out_mistake_with_alternative`: 間違いを指摘し、代替案を提示
  - [ ] `test_ask_for_missing_information`: 不足情報を的確に質問
  - [ ] `test_emoji_usage_minimal`: 絵文字は控えめ（✅📝📖程度）
  - [ ] `test_no_unnecessary_preamble`: 不要な前置き・後置きがない

### 4. Documentation

- [ ] **4.1** `docs/IMPLEMENTATION_PLAN.md` を更新
  - [ ] Phase 0の実装状況を記録（完了日・変更内容）
- [ ] **4.2** `claudedocs/prompt-guide.md` を作成（オプション）
  - [ ] システムプロンプトの構造解説
  - [ ] 動的変数の使い方
  - [ ] プロンプトカスタマイズ方法

### 5. Deployment

- [ ] **5.1** ローカルテスト
  ```bash
  cd /Users/noguchilin/dev/lab-project/nakamura-misaki
  uv run pytest tests/unit/test_claude_adapter.py -v
  uv run pytest tests/integration/test_prompt_loading.py -v
  ```
- [ ] **5.2** Git Commit
  ```bash
  git add config/prompts/default.json src/adapters/secondary/claude_adapter.py tests/
  git commit -m "feat: Implement Phase 0 - System Prompt v4.0.0 (Kusanagi personality)"
  ```
- [ ] **5.3** GitHub Push（自動デプロイ）
  ```bash
  git push origin main
  ```
- [ ] **5.4** デプロイ確認
  ```bash
  gh run watch
  ```
- [ ] **5.5** NixOSで動作確認
  ```bash
  ssh home-lab-01
  systemctl status nakamura-misaki-api.service
  journalctl -u nakamura-misaki-api.service -f
  ```

### 6. Validation (Slack E2E Tests)

- [ ] **6.1** Slackで動作確認（基本応答）
  - [ ] 質問: "今日のタスクは？" → 簡潔な応答を確認
  - [ ] 質問: "先週の決定事項は？" → 過去のノートから検索を確認
  - [ ] 質問: "タスク登録して" → 不足情報を的確に質問を確認

- [ ] **6.2** Slackで動作確認（草薙素子風性格）
  - [ ] 質問: "このコード見てくれる？" → 断り + 代替案を確認
  - [ ] 質問: "XYZ123のタスクは？" → 間違いを指摘 + 代替案を確認
  - [ ] 応答スタイル: 1-3文で完結、不要な前置きなし、絵文字控えめ

- [ ] **6.3** Slackで動作確認（できないことの明示）
  - [ ] 質問: "バグ修正して" → できないことを明示 + 代替案
  - [ ] 質問: "コード実行して" → できないことを明示 + 代替案
  - [ ] 質問: "GitHub Issues見て" → できないことを明示 + 代替案

### 7. Post-Deployment

- [ ] **7.1** メトリクス確認
  - [ ] Prompt Loading Time: 10ms以内
  - [ ] Variable Replacement Time: 5ms以内
  - [ ] Claude API Response Time: 5秒以内
  - [ ] Error Rate: 1%以下

- [ ] **7.2** ユーザーフィードバック収集
  - [ ] 草薙素子風スコア: 5段階評価で4以上
  - [ ] ユーザー満足度: "性格は適切か？" に対してYes

- [ ] **7.3** トークンカウント確認
  - [ ] システムプロンプト長: 2000 tokens以内
  - [ ] Claude API tokenizer で測定

### 8. Rollback Plan (問題発生時のみ)

- [ ] **8.1** Backup promptに戻す
  ```bash
  cd /Users/noguchilin/dev/lab-project/nakamura-misaki
  cp config/prompts/default.json.v3.0.0.backup config/prompts/default.json
  ```
- [ ] **8.2** 再デプロイ
  ```bash
  git add config/prompts/default.json
  git commit -m "fix: Rollback to v3.0.0"
  git push origin main
  ```

## Estimated Timeline

| Task | Estimated Time | Dependencies |
|------|----------------|--------------|
| 1. System Prompt Creation | 2 hours | - |
| 2. Code Implementation | 1 hour | 1 |
| 3. Testing | 3 hours | 2 |
| 4. Documentation | 1 hour | 1, 2 |
| 5. Deployment | 30 minutes | 3 |
| 6. Validation | 1 hour | 5 |
| 7. Post-Deployment | 30 minutes | 6 |
| **Total** | **9 hours** | - |

## Dependencies

- ✅ Anthropic Structured Note-Taking (v3.0.0で実装済み)
- ✅ `JsonPromptRepository` (既存実装)
- ✅ `ClaudeAdapter` (既存実装)
- ✅ 変数置換機構（`{user_id}`, `{workspace_path}`, `{saved_notes}`）
- ⏳ `{task_context}` 変数の実装（Phase 2）
- ⏳ PostgreSQL連携（Phase 1）

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| 草薙素子風の性格が実現できない | High | Low | E2Eテストで人間評価、必要に応じてプロンプト調整 |
| トークン数が2000を超える | Medium | Medium | プロンプトを簡潔化、不要なセクションを削除 |
| 既存の動作が壊れる | High | Low | 単体テスト・統合テストでカバー、rollback planあり |
| Claude APIのレスポンスが遅い | Medium | Low | タイムアウト設定（5秒）、非同期処理で対応 |

## Success Criteria

Phase 0は以下を満たせば完了とする：

1. **システムプロンプト実装**:
   - [ ] default.json v4.0.0が正しく読み込める
   - [ ] 動的変数（`{user_id}`, `{workspace_path}`, `{channel_type}`, `{saved_notes}`, `{task_context}`）が正しく置換される
   - [ ] トークン数が2000以内

2. **草薙素子風性格の実現**:
   - [ ] 簡潔な応答（1-3文）
   - [ ] 質問には直接答える
   - [ ] 間違いを指摘し、代替案を提示
   - [ ] コードレビュー等は断り、代替案を提示
   - [ ] 絵文字は控えめ

3. **テストカバレッジ**:
   - [ ] 単体テスト: 80%以上
   - [ ] 統合テスト: 主要パスをカバー
   - [ ] E2Eテスト: 主要ユーザーストーリーをカバー

4. **デプロイ成功**:
   - [ ] NixOSで正常動作
   - [ ] Slackで動作確認完了
   - [ ] エラーなし

## Notes

- Phase 0では `{task_context}` は空文字列を返す（Phase 2で実装）
- `technical.json`, `schedule.json` は非推奨だが削除しない（後方互換性）
- プロンプトの調整は人間評価を元に継続的に改善
