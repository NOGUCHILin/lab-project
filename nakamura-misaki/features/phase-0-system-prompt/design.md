# Phase 0: System Prompt - Design

## System Architecture

### Current Architecture (v3.0.0)

```
Slack Event → SlackEventAdapter → ClaudeAdapter.send_message()
                                        ↓
                                   PromptRepository.get_for_user()
                                        ↓
                                   default.json (v3.0.0)
                                        ↓
                                   Variable Replacement ({user_id}, {workspace_path}, {saved_notes})
                                        ↓
                                   Claude API
```

### Target Architecture (v4.0.0)

変更なし（プロンプト内容のみ更新）

## System Prompt Structure (v4.0.0)

### JSON Schema

```json
{
  "name": "default",
  "description": "nakamura-misaki v4.0.0 - 草薙素子風タスク管理特化プロンプト",
  "version": "4.0.0",
  "system_prompt": "...",
  "metadata": {
    "created_at": "2025-10-14",
    "updated_at": "2025-10-14",
    "author": "noguchilin",
    "use_case": "タスク管理・ハンドオフ・内部情報管理（草薙素子風）",
    "personality": "kusanagi_motoko_rookie",
    "version_notes": "v4.0.0: 草薙素子風性格、タスク管理特化、コードレビュー除外"
  }
}
```

### System Prompt XML Structure

```xml
<role>
あなたは中村美咲（Nakamura-Misaki）、Slackワークスペース内で活動する仮想チームメンバーです。

## 性格（草薙素子少佐 - 新人バージョン）
- 冷静、論理的、無駄がない
- 間違いを発見したら指摘し、代替案を提示
- 的確に応答（不要な前置き・後置きなし）
- 謙虚だが確実

## 役割
- タスク管理（登録・更新・削除・リマインダー）
- ハンドオフ管理（作業引き継ぎ・進捗共有）
- 内部情報管理（決定事項・ノート検索）

## できないこと
- コードレビュー・バグ修正
- コード実行
- 外部ツール連携（Slack/Claude以外）
</role>

<context>
セッション情報:
- ユーザーID: {user_id}
- ワークスペース: {workspace_path}
- チャネルタイプ: {channel_type}

過去のノート（セッション間記憶）:
{saved_notes}
</context>

<tone>
- 簡潔（1-3文で完結）
- 直接的（質問には直接答える）
- 的確（間違いは指摘、代替案を提示）
- 論理的（感情表現は最小限）
- 絵文字は控えめ（✅📝📖程度）
</tone>

<rules>
## 基本動作
1. 質問には直接答える（不要な前置きなし）
2. 不足情報があれば的確に質問する
3. 間違いを発見したら指摘し、代替案を提示
4. できないことは明確に断り、代替案を提示

## 内部情報管理（Phase 0で実装済み）
1. 決定事項は自動記録（Anthropic Structured Note-Taking）
2. 過去のノートから検索可能
3. セッション間で記憶保持

## できないこと
1. ❌ コードレビュー → 技術リードに依頼を提案
2. ❌ バグ修正 → GitHub Issueを提案
3. ❌ コード実行 → 実行環境がないことを明示
4. ❌ 外部API連携 → Slack/Claude以外は非対応
</rules>

<examples>
<example>
<scenario>間違いの指摘と代替案</scenario>
<user>このコード見てくれる？</user>
<assistant>
コードレビューは対応していません。

代替案：
- @技術リードに依頼
- GitHub Pull Requestでレビュー依頼
</assistant>
</example>

<example>
<scenario>過去のノート検索</scenario>
<user>先週のDB移行の決定事項は？</user>
<assistant>
📖 2025-10-07の決定事項

- DB: PostgreSQL 16
- Vector DB: Supabase pgvector
- 移行日: 2025-10-15（月）
- 担当: 野口凜

詳細が必要な場合はお知らせください。
</assistant>
</example>

<example>
<scenario>簡潔な応答</scenario>
<user>nakamura-misakiって何ができるの？</user>
<assistant>
Phase 0では以下が可能です：
- 過去の決定事項・ノートの検索
- セッション間での記憶保持
- 簡潔で的確な応答

タスク管理・ハンドオフはPhase 2以降で実装予定です。
</assistant>
</example>
</examples>

<immediate_task>
ユーザーからのメッセージに応答してください。
上記のルールと例に従い、簡潔かつ的確に答えてください。
</immediate_task>
```

## Dynamic Variables

### Variable Replacement Logic

実装場所: [src/adapters/secondary/claude_adapter.py:50-82](src/adapters/secondary/claude_adapter.py#L50-L82)

```python
async def send_message(
    self,
    user_id: str,
    message: str,
    workspace_path: str,
    session_id: str | None = None,
    continue_conversation: bool = False,
    is_dm: bool = False,
    saved_notes: str = "",
) -> str:
    """Send message to Claude Code"""
    prompt_config = await self.prompt_repository.get_for_user(user_id)
    task_context = await self._generate_task_context(user_id)

    # Variable replacement
    system_prompt = prompt_config.system_prompt
    system_prompt = system_prompt.replace("{user_id}", user_id)
    system_prompt = system_prompt.replace("{workspace_path}", workspace_path)
    system_prompt = system_prompt.replace("{channel_type}", "DM" if is_dm else "Channel Mention")
    system_prompt = system_prompt.replace("{task_context}", task_context)
    system_prompt = system_prompt.replace("{saved_notes}", saved_notes)

    # Send to Claude...
```

### Variables Definition

| Variable | Type | Source | Example | Phase |
|----------|------|--------|---------|-------|
| `{user_id}` | string | Slack Event | `U01ABC123` | 0 |
| `{workspace_path}` | string | Config | `/path/to/workspace` | 0 |
| `{channel_type}` | string | Derived | `DM` or `Channel Mention` | 0 |
| `{saved_notes}` | string | Note Repository | `- 2025-10-07: DB移行決定\n...` | 0 (既存) |
| `{task_context}` | string | Task Repository | `今日のタスク:\n- API統合...` | 2 (Phase 2で実装) |

### Phase 0 Implementation

**Phase 0での変更**:
- `{task_context}` は空文字列 `""` を返す（Phase 2で実装）
- その他の変数は既存実装を維持

```python
async def _generate_task_context(self, user_id: str) -> str:
    """Generate task context for user

    Phase 0: Returns empty string (not yet implemented)
    Phase 2: Returns today's tasks and pending handoffs
    """
    # TODO: Phase 2でタスク取得ロジック実装
    return ""
```

## File Structure

### Affected Files

```
nakamura-misaki/
├── config/prompts/
│   ├── default.json          # ✏️ 更新（v3.0.0 → v4.0.0）
│   ├── technical.json         # ⚠️ 非推奨マーク追加
│   └── schedule.json          # ⚠️ 非推奨マーク追加
├── src/adapters/secondary/
│   ├── claude_adapter.py      # ✏️ 更新（_generate_task_context実装）
│   └── prompt_repository_adapter.py  # 変更なし
└── tests/
    ├── unit/test_claude_adapter.py           # ✅ 新規作成
    ├── integration/test_prompt_loading.py    # ✅ 新規作成
    └── e2e/test_kusanagi_personality.py      # ✅ 新規作成
```

## API Design

### No API Changes

Phase 0ではAPIエンドポイントの変更なし。既存の `ClaudeAdapter.send_message()` を使用。

### Internal Method: `_generate_task_context()`

```python
async def _generate_task_context(self, user_id: str) -> str:
    """Generate task context for system prompt

    Args:
        user_id: Slack User ID

    Returns:
        Task context string (empty in Phase 0)

    Phase 0: Returns ""
    Phase 2: Returns formatted task list like:
        今日のタスク:
        - [abc12345] API統合テスト (期限: 15:00)
        - [def67890] ドキュメント更新 (期限: 18:00)

        保留中のハンドオフ:
        - [ghi11111] API統合 → 田中太郎（明日 9:00）
    """
    # Phase 0: Not implemented yet
    return ""
```

## Data Model

### PromptConfig (No Changes)

既存の `src/domain/models/prompt_config.py` を使用（変更なし）

```python
@dataclass
class PromptConfig:
    name: str
    system_prompt: str
    description: str
    version: str
    metadata: dict[str, Any] = field(default_factory=dict)
```

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_claude_adapter.py`

```python
class TestClaudeAdapter:
    async def test_variable_replacement_phase0(self):
        """Phase 0: 変数置換が正しく動作する"""
        adapter = ClaudeAdapter(...)

        result = await adapter.send_message(
            user_id="U01ABC123",
            message="今日のタスクは？",
            workspace_path="/test/workspace",
            is_dm=True,
            saved_notes="- 2025-10-07: DB移行決定",
        )

        # System promptに変数が置換されていることを確認
        assert "U01ABC123" in adapter._last_system_prompt
        assert "/test/workspace" in adapter._last_system_prompt
        assert "DM" in adapter._last_system_prompt
        assert "2025-10-07: DB移行決定" in adapter._last_system_prompt

    async def test_task_context_empty_in_phase0(self):
        """Phase 0: task_contextは空文字列"""
        adapter = ClaudeAdapter(...)

        context = await adapter._generate_task_context("U01ABC123")
        assert context == ""
```

### Integration Tests

**File**: `tests/integration/test_prompt_loading.py`

```python
class TestPromptLoading:
    async def test_load_v4_default_prompt(self):
        """default.json v4.0.0が正しく読み込める"""
        repo = JsonPromptRepository(Path("config/prompts"))

        prompt = await repo.get_by_name("default")

        assert prompt.name == "default"
        assert prompt.version == "4.0.0"
        assert "草薙素子" in prompt.metadata.get("personality", "")
        assert "<role>" in prompt.system_prompt
        assert "{task_context}" in prompt.system_prompt
```

### E2E Tests

**File**: `tests/e2e/test_kusanagi_personality.py`

```python
class TestKusanagiPersonality:
    async def test_concise_response(self):
        """簡潔な応答（1-3文）"""
        response = await send_slack_message("今日のタスクは？")

        # 1-3文で完結しているか確認（改行で分割）
        lines = [l for l in response.split("\n") if l.strip()]
        assert len(lines) <= 5  # タスク一覧 + 余白

    async def test_refuse_code_review_with_alternative(self):
        """コードレビューは断り、代替案を提示"""
        response = await send_slack_message("このコード見てくれる？")

        assert "対応していません" in response
        assert "代替案" in response or "提案" in response

    async def test_point_out_mistake(self):
        """間違いを指摘し、代替案を提示"""
        # テストシナリオ: 存在しないタスクIDを指定
        response = await send_slack_message("タスクXYZ123の進捗は？")

        assert "見つかりません" in response or "存在しません" in response
        # 代替案提示を確認（タスク一覧表示など）
```

## Deployment

### Rollout Plan

#### Step 1: Backup Current Prompt
```bash
cd /Users/noguchilin/dev/lab-project/nakamura-misaki
cp config/prompts/default.json config/prompts/default.json.v3.0.0.backup
```

#### Step 2: Update Prompt
- `config/prompts/default.json` をv4.0.0に更新
- `technical.json`, `schedule.json` に非推奨マークを追加（`"deprecated": true` in metadata）

#### Step 3: Deploy to NixOS
```bash
# mainブランチにpush → 自動デプロイ
git add config/prompts/default.json
git commit -m "feat: Update system prompt to v4.0.0 (Kusanagi personality)"
git push origin main

# デプロイ確認
gh run watch
```

#### Step 4: Verify
```bash
# NixOSで確認
ssh home-lab-01
systemctl restart nakamura-misaki-api.service
journalctl -u nakamura-misaki-api.service -f

# Slackで動作確認
# 1. 「今日のタスクは？」と質問
# 2. 「このコード見てくれる？」と質問（断る応答を確認）
# 3. 応答スタイルが草薙素子風か確認
```

### Rollback Plan

問題が発生した場合:

```bash
# Backup promptに戻す
cd /Users/noguchilin/dev/lab-project/nakamura-misaki
cp config/prompts/default.json.v3.0.0.backup config/prompts/default.json

# デプロイ
git add config/prompts/default.json
git commit -m "fix: Rollback to v3.0.0"
git push origin main
```

## Performance Considerations

### Token Count

- **v3.0.0**: 約1800 tokens
- **v4.0.0 Target**: 約2000 tokens（+10%許容）
- **測定方法**: Claude API tokenizer使用

### Cache Hit Rate

既存のキャッシュ機構（`st_mtime`）により、ファイル変更がない限りキャッシュから読み込む。

- **Expected Cache Hit Rate**: 95%以上
- **Cache Invalidation**: ファイル変更検知（`st_mtime`）

## Security Considerations

### No Security Impact

Phase 0ではセキュリティ関連の変更なし。

- 機密情報（API Key等）はシステムプロンプトに含まない
- ユーザー入力はそのまま変数置換（サニタイズ不要：Claude API側で処理）

## Error Handling

### Prompt Loading Failure

既存の実装を維持（[src/adapters/secondary/prompt_repository_adapter.py:96-106](src/adapters/secondary/prompt_repository_adapter.py#L96-L106)）:

```python
def _get_fallback_prompt(self) -> PromptConfig:
    """デフォルトプロンプトが見つからない場合のフォールバック"""
    return PromptConfig(
        name="fallback",
        system_prompt="""あなたは中村美咲、親切なアシスタントです。

ユーザーの質問に丁寧に答え、タスク管理をサポートします。
""",
        description="フォールバックプロンプト",
        version="1.0.0",
    )
```

### Variable Replacement Failure

変数が存在しない場合、そのまま置換しない（`{task_context}` がシステムプロンプトに残る）。Claude APIはこれを無視するため問題なし。

## Monitoring

### Metrics to Track

- **Prompt Loading Time**: 10ms以内
- **Variable Replacement Time**: 5ms以内
- **Claude API Response Time**: 5秒以内
- **Error Rate**: 1%以下

### Logging

```python
logger.info("Loaded prompt", extra={
    "prompt_name": prompt_config.name,
    "version": prompt_config.version,
    "user_id": user_id,
    "loading_time_ms": loading_time,
})
```
