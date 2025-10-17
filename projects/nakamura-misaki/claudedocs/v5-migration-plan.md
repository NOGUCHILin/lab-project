# nakamura-misaki v5.0.0 Migration Plan
**Claude Agent SDK統合による自然言語タスク管理システム**

**作成日**: 2025-10-15
**ステータス**: 📋 Planning
**対象バージョン**: v4.0.0 → v5.0.0

---

## 🎯 移行の目的

**現状（v4.0.0）**: 正規表現パターンマッチングによるコマンド駆動型タスク管理

**目標（v5.0.0）**: Claude Agent SDKを活用した自然言語理解によるタスク管理

### 主要な変更点

1. **コマンドパーサー廃止**: `TaskCommandParser`, `HandoffCommandParser`を削除
2. **Claude Tool Use導入**: 自然言語→Tool呼び出し→Use Case実行
3. **会話履歴管理**: ユーザーごとのセッション保持（24時間TTL）
4. **雑談対応**: タスク関連以外のメッセージにも自然に応答

---

## 1. アーキテクチャ設計

### 1.1 システム構成

```
Slack Message
    ↓
SlackEventHandler
    ↓
ConversationManager (NEW)
    - セッション管理
    - 会話履歴取得/保存
    ↓
ClaudeAgentService (NEW)
    - Tool定義
    - Claude API呼び出し
    - Tool呼び出し実行
    ↓
TaskTools / HandoffTools (NEW)
    - Use Caseへのブリッジ
    - Tool実装
    ↓
Existing Use Cases
    - RegisterTaskUseCase
    - CompleteTaskUseCase
    - etc.
    ↓
Response
    ↓
Slack
```

### 1.2 新規コンポーネント

| コンポーネント | 責務 | 配置 |
|-------------|------|------|
| `ConversationManager` | ユーザーごとの会話履歴管理 | `src/domain/services/` |
| `ConversationRepository` | 会話履歴の永続化 | `src/adapters/secondary/repositories/` |
| `ClaudeAgentService` | Claude API統合、Tool Use制御 | `src/domain/services/` |
| `TaskTools` | タスク関連Tool実装 | `src/adapters/primary/tools/` |
| `HandoffTools` | ハンドオフ関連Tool実装 | `src/adapters/primary/tools/` |
| `TeamTools` | チーム関連Tool実装 | `src/adapters/primary/tools/` |

### 1.3 削除対象

- `TaskCommandParser` (正規表現パーサー)
- `HandoffCommandParser` (正規表現パーサー)
- `TaskResponseFormatter` (Claude生成に置き換え)
- `HandoffResponseFormatter` (Claude生成に置き換え)

---

## 2. データモデル設計

### 2.1 会話履歴テーブル

```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255) NOT NULL,
    messages JSONB NOT NULL,  -- Claude Messages API形式
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_message_at TIMESTAMP NOT NULL,
    INDEX idx_user_channel (user_id, channel_id),
    INDEX idx_last_message (last_message_at)
);
```

**会話履歴の保持期間**: 24時間（設定可能）

### 2.2 Messagesフォーマット

```json
[
  {"role": "user", "content": "明日までにレポート書く"},
  {"role": "assistant", "content": "...", "tool_calls": [...]},
  {"role": "user", "content": "今日のタスクは？"}
]
```

---

## 3. Tool定義設計

### 3.1 Task Management Tools

```python
tools = [
    {
        "name": "register_task",
        "description": "ユーザーの新しいタスクを登録する",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "タスクのタイトル"},
                "description": {"type": "string", "description": "タスクの詳細説明（任意）"},
                "due_date": {"type": "string", "format": "date-time", "description": "期限（ISO 8601形式）"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_tasks",
        "description": "ユーザーのタスク一覧を取得する",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "フィルタするステータス（任意）"},
                "date_filter": {"type": "string", "enum": ["today", "week", "all"], "description": "日付フィルタ（任意）"}
            }
        }
    },
    {
        "name": "complete_task",
        "description": "タスクを完了済みにする",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_identifier": {"type": "string", "description": "タスクID（UUID）またはタスクタイトルの一部"}
            },
            "required": ["task_identifier"]
        }
    },
    {
        "name": "update_task",
        "description": "タスク情報を更新する",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_identifier": {"type": "string", "description": "タスクID（UUID）またはタスクタイトルの一部"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "due_date": {"type": "string", "format": "date-time"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}
            },
            "required": ["task_identifier"]
        }
    }
]
```

### 3.2 Handoff Management Tools

```python
handoff_tools = [
    {
        "name": "create_handoff",
        "description": "タスクを別のメンバーに引き継ぐ",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_identifier": {"type": "string", "description": "引き継ぐタスクのID"},
                "to_user": {"type": "string", "description": "引き継ぎ先のSlack User ID（<@U123456>形式）"},
                "progress_note": {"type": "string", "description": "進捗メモ"},
                "handoff_time": {"type": "string", "format": "date-time", "description": "引き継ぎ予定時刻"}
            },
            "required": ["task_identifier", "to_user"]
        }
    },
    {
        "name": "list_handoffs",
        "description": "自分宛のハンドオフ一覧を取得する",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "complete_handoff",
        "description": "ハンドオフを完了済みにする",
        "input_schema": {
            "type": "object",
            "properties": {
                "handoff_id": {"type": "string", "description": "ハンドオフID（UUID）"}
            },
            "required": ["handoff_id"]
        }
    }
]
```

### 3.3 Context Tools

```python
context_tools = [
    {
        "name": "get_current_context",
        "description": "現在の日時、ユーザー情報、チーム情報を取得する",
        "input_schema": {"type": "object", "properties": {}}
    }
]
```

---

## 4. System Prompt設計

```python
SYSTEM_PROMPT = """
あなたは中村美咲というタスク管理AIアシスタントです。草薙素子のような冷静で効率的な性格で、ユーザーのタスク管理をサポートします。

# あなたの役割

- ユーザーの自然な日本語メッセージからタスク操作の意図を理解する
- 適切なToolを呼び出してタスク・ハンドオフを管理する
- 簡潔で的確な応答を返す

# Tool使用ガイドライン

1. **タスク登録**: 「〜をやる」「〜を作る」「〜までに〜」等の表現からタスク登録意図を検出
2. **タスク確認**: 「今日のタスク」「タスク一覧」等でlist_tasksを呼び出し
3. **タスク完了**: 「〜終わった」「〜完了」等でcomplete_taskを呼び出し
4. **曖昧な識別子**: ユーザーがタスクを「あのレポート」等と表現した場合、list_tasksで候補を確認してから操作
5. **日時解釈**: 「明日」「来週」「3日後」等を適切にISO 8601形式に変換
6. **雑談対応**: タスク関連でない雑談にも自然に応答（Toolは呼ばない）

# 応答スタイル

- 簡潔（1-2文）
- 草薙素子風の口調（「了解した」「把握した」「確認する」等）
- タスク操作結果を明確に伝える

# 現在時刻

{current_time}
"""
```

---

## 5. 実装ステップ

### Phase 1: 基盤構築（データモデル・リポジトリ）

**タスク**:
1. `conversations`テーブル作成（マイグレーション）
2. `Conversation`エンティティ作成
3. `ConversationRepository`実装（SQLAlchemy）
4. `ConversationManager`ドメインサービス実装

**成果物**:
- `alembic/versions/xxx_add_conversations_table.py`
- `src/domain/entities/conversation.py`
- `src/adapters/secondary/repositories/conversation_repository.py`
- `src/domain/services/conversation_manager.py`

---

### Phase 2: Tool実装（Use Caseブリッジ）

**タスク**:
1. `BaseTool`抽象クラス作成
2. `TaskTools`実装（register, list, complete, update）
3. `HandoffTools`実装（create, list, complete）
4. `ContextTools`実装（get_current_context）

**成果物**:
- `src/adapters/primary/tools/base_tool.py`
- `src/adapters/primary/tools/task_tools.py`
- `src/adapters/primary/tools/handoff_tools.py`
- `src/adapters/primary/tools/context_tools.py`

**設計ポイント**:
- `task_identifier`が曖昧な場合の解決ロジック（タイトル部分一致）
- Tool実行時のエラーハンドリング（存在しないタスクID等）

---

### Phase 3: Claude Agent Service実装

**タスク**:
1. `ClaudeAgentService`作成
2. Tool Use APIラッパー実装
3. System Prompt管理
4. Tool呼び出しディスパッチャー実装

**成果物**:
- `src/domain/services/claude_agent_service.py`

**主要メソッド**:
```python
class ClaudeAgentService:
    async def process_message(
        self,
        user_id: str,
        channel_id: str,
        message: str,
        conversation_history: list[dict]
    ) -> tuple[str, list[dict]]:
        """
        Returns:
            (response_text, updated_conversation_history)
        """
```

---

### Phase 4: SlackEventHandler統合

**タスク**:
1. 既存`SlackEventHandler`をリファクタリング
2. `ConversationManager`統合
3. `ClaudeAgentService`統合
4. パーサー・フォーマッター削除

**成果物**:
- `src/adapters/primary/slack_event_handler.py`（大幅リファクタ）

**新しいフロー**:
```python
async def handle_message(self, user_id: str, text: str, channel: str) -> str:
    # 1. 会話履歴取得
    conversation = await self.conversation_manager.get_or_create(user_id, channel)

    # 2. Claude Agent呼び出し
    response, updated_history = await self.claude_agent.process_message(
        user_id, channel, text, conversation.messages
    )

    # 3. 会話履歴更新
    await self.conversation_manager.update(conversation.id, updated_history)

    # 4. 応答返却
    return response
```

---

### Phase 5: REST API見直し

**判断基準**:
- Slack経由でのみ使用される場合 → 削除
- 外部統合・管理UI等で必要 → 維持

**暫定判断**:
- `/api/tasks` → **維持**（Admin UIで使用中）
- `/api/handoffs` → **維持**（Admin UIで使用中）
- `/api/team` → **維持**

---

### Phase 6: 環境変数・設定更新

**タスク**:
1. `ANTHROPIC_API_KEY`確認（既存）
2. `CONVERSATION_TTL_HOURS`追加（デフォルト24時間）
3. NixOS設定更新

**成果物**:
- `nixos-config/modules/services/registry/nakamura-misaki-api.nix`更新

---

### Phase 7: ログ・モニタリング強化

**タスク**:
1. Claude API呼び出しログ追加
2. Tool実行ログ追加
3. 会話履歴管理ログ追加

**ログレベル**:
- INFO: Tool呼び出し、会話開始/終了
- DEBUG: Claude API request/response、Tool実行詳細

---

### Phase 8: テスト・検証

**テストシナリオ**:
1. **基本タスク操作**:
   - 「明日までにレポート書く」→ タスク登録
   - 「今日のタスクは？」→ タスク一覧表示
   - 「レポート終わった」→ タスク完了

2. **曖昧な表現**:
   - 「あのレポートのタスク完了」→ タイトル部分一致で特定

3. **雑談混在**:
   - 「おはよう」→ 通常応答
   - 「疲れた」→ 励まし応答
   - 「そういえば会議資料作らなきゃ」→ タスク登録提案

4. **ハンドオフ**:
   - 「このタスクを<@U123456>に引き継ぎ」→ ハンドオフ作成

5. **会話履歴**:
   - 連続した会話でコンテキスト保持確認

---

## 6. マイグレーション戦略

### 6.1 コード削除

```bash
# 削除対象ファイル
rm src/adapters/primary/task_command_parser.py
rm src/adapters/primary/handoff_command_parser.py
rm src/adapters/primary/task_response_formatter.py
rm src/adapters/primary/handoff_response_formatter.py
```

### 6.2 段階的ロールアウト

**方針**: フィーチャーフラグによる段階移行は行わず、一気に置き換え

---

## 7. リスク・考慮事項

### 7.1 Claude API レート制限

- **対策**: Exponential backoff実装、レート制限エラーハンドリング

### 7.2 会話履歴の肥大化

- **対策**:
  - 24時間でTTL
  - メッセージ数上限（例: 直近20件のみ保持）
  - 古い履歴の要約機能（オプション）

### 7.3 Tool呼び出しの信頼性

- **考慮**: Claudeの誤判断リスク
- **対策**:
  - 詳細なTool description
  - 実行ログで異常検知
  - 必要に応じて確認UIを後から追加可能な設計

### 7.4 コスト

- **試算**: メッセージあたり約2,000トークン（会話履歴込み）
  - Claude 3.5 Sonnet: $3/MTok (input), $15/MTok (output)
  - 1,000メッセージ/月 → 約$50-100/月

---

## 8. ドキュメント更新計画

### 8.1 更新対象

| ファイル | 更新内容 | 優先度 |
|---------|---------|--------|
| `README.md` | v5.0.0概要、技術スタック、アーキテクチャ全面書き換え | 🔴 必須 |
| `CLAUDE.md` | v5.0.0方針、Claude Agent SDK統合、Tool定義 | 🔴 必須 |
| `docs/ARCHITECTURE_V5.md` (NEW) | v5.0.0詳細設計ドキュメント | 🔴 必須 |
| `docs/ARCHITECTURE_V4.md` | アーカイブ扱い（参照のみ） | 🟡 任意 |
| `docs/PHASE5_IMPLEMENTATION_PLAN.md` | Phase 5はv4.0.0のSlack統合として完了扱い | 🟡 任意 |

### 8.2 README.md 新構成

```markdown
# nakamura-misaki v5.0.0

**自然言語タスク管理AIアシスタント**

## 概要

nakamura-misakiは、Claudeを活用した自然言語タスク管理システムです。
Slackでの会話を通じて、タスクやハンドオフを管理します。

## 主要機能

- 🤖 **自然言語理解**: Claude Agent SDKによる柔軟なタスク操作
- 💬 **Slack統合**: Slackワークスペースでシームレスに利用
- 📊 **チーム管理**: タスク・ハンドオフの可視化
- 🧠 **会話履歴保持**: コンテキストを保った対話

## 技術スタック

- **Python 3.12**: メイン言語
- **FastAPI**: REST API/Webhook
- **Claude 3.5 Sonnet**: 自然言語理解（Tool Use）
- **PostgreSQL 16 + pgvector**: データ永続化
- **Slack Events API**: メッセージ受信
- **NixOS**: 宣言的デプロイ

## アーキテクチャ

詳細は [docs/ARCHITECTURE_V5.md](docs/ARCHITECTURE_V5.md) を参照

...
```

### 8.3 CLAUDE.md 新構成

```markdown
# nakamura-misaki v5.0.0

**Claude Agent SDK統合タスク管理システム**

## プロジェクト概要

- **目的**: 自然言語によるタスク・ハンドオフ管理
- **コア技術**: Claude Tool Use, Hexagonal Architecture
- **バージョン**: v5.0.0

## 開発ガイドライン

### アーキテクチャ原則

- **Hexagonal Architecture**: ドメイン層を中心とした設計
- **Tool-Driven Design**: Claude Toolとして機能を定義
- **Conversation-Aware**: 会話履歴を保持した自然な対話

### v4.0.0からの主要変更

❌ **削除**:
- TaskCommandParser（正規表現パーサー）
- HandoffCommandParser
- TaskResponseFormatter
- HandoffResponseFormatter

✅ **追加**:
- ConversationManager（会話履歴管理）
- ClaudeAgentService（Tool Use統合）
- TaskTools/HandoffTools（Tool実装）

...
```

---

## 9. 移行完了の定義

以下をすべて満たした時点でv5.0.0リリース：

- ✅ 会話履歴管理機能の実装・テスト完了
- ✅ Claude Tool Use統合の実装・テスト完了
- ✅ 既存パーサーの削除
- ✅ 自然言語タスク操作の動作確認（5つのシナリオ）
- ✅ ドキュメント更新（README, CLAUDE.md, ARCHITECTURE_V5.md）
- ✅ 本番環境デプロイ・動作確認

---

Generated with [Claude Code](https://claude.com/claude-code)
