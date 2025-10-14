# Phase 2: Task API - Requirements

## Overview

タスク管理APIを実装し、Slack経由でタスクの登録・更新・削除・一覧表示ができるようにする。`{task_context}` 動的変数を実装し、システムプロンプトに今日のタスクを自動注入する。

## User Stories

### Story 1: タスク登録

**As a** チームメンバー
**I want** Slackでタスクを登録できる
**So that** やるべきことを管理できる

**Acceptance Criteria**:
- [ ] `@中村美咲 タスク登録: [タスク名] 期限: [日時]` で登録できる
- [ ] 担当者を指定できる（デフォルトは自分）
- [ ] 期限を指定できる（デフォルトは期限なし）
- [ ] 登録完了メッセージが返る

**Example**:
```
User: @中村美咲 タスク登録: API統合テスト 期限: 明日15時
nakamura-misaki:
  ✅ タスク登録完了

  - タスク: API統合テスト
  - 担当: @野口凜
  - 期限: 2025-10-15 15:00
  - ID: abc12345
```

### Story 2: タスク一覧表示

**As a** チームメンバー
**I want** 自分のタスク一覧を確認できる
**So that** 今日やるべきことが分かる

**Acceptance Criteria**:
- [ ] `@中村美咲 今日のタスクは？` で今日が期限のタスクを表示
- [ ] `@中村美咲 タスク一覧` で全タスクを表示
- [ ] 期限順に並ぶ
- [ ] ステータスが表示される（未着手・進行中・完了）

**Example**:
```
User: @中村美咲 今日のタスクは？
nakamura-misaki:
  今日のタスク（3件）:
  - [abc12345] API統合テスト (15:00期限)
  - [def67890] ドキュメント更新 (18:00期限)
  - [ghi11111] レビュー対応 (期限なし)
```

### Story 3: タスク更新

**As a** チームメンバー
**I want** タスクのステータスを更新できる
**So that** 進捗を管理できる

**Acceptance Criteria**:
- [ ] `@中村美咲 タスク [ID] を進行中に` でステータス変更
- [ ] `@中村美咲 タスク [ID] を完了` で完了にできる
- [ ] 期限変更ができる
- [ ] 担当者変更ができる

**Example**:
```
User: @中村美咲 タスク abc12345 を完了
nakamura-misaki:
  ✅ タスク完了

  タスク: API統合テスト
  完了時刻: 2025-10-15 14:30
  所要時間: 3時間
```

### Story 4: タスク削除

**As a** チームメンバー
**I want** 不要なタスクを削除できる
**So that** タスク一覧がクリーンになる

**Acceptance Criteria**:
- [ ] `@中村美咲 タスク [ID] を削除` で削除できる
- [ ] 削除前に確認がある
- [ ] 削除後、復元不可

**Example**:
```
User: @中村美咲 タスク abc12345 を削除
nakamura-misaki:
  ⚠️ 本当に削除しますか？

  タスク: API統合テスト
  担当: @野口凜

  削除する場合は「削除確認」と返信してください。

User: 削除確認
nakamura-misaki:
  ✅ タスク削除完了
```

### Story 5: システムプロンプトへのタスク注入

**As a** nakamura-misaki
**I want** システムプロンプトに今日のタスクが自動注入される
**So that** ユーザーの質問に対してタスクを考慮した応答ができる

**Acceptance Criteria**:
- [ ] `{task_context}` 変数に今日のタスク一覧が注入される
- [ ] 保留中のハンドオフも注入される
- [ ] 動的変数置換が正常動作する

**Example System Prompt**:
```xml
<context>
現在のタスク状況:
今日のタスク:
- [abc12345] API統合テスト (期限: 15:00)
- [def67890] ドキュメント更新 (期限: 18:00)

保留中のハンドオフ:
- [ghi11111] API統合 → 田中太郎（明日 9:00）
</context>
```

## Functional Requirements

### FR-1: Task Use Cases

- `RegisterTaskUseCase`: タスク登録
- `UpdateTaskUseCase`: タスク更新
- `CompleteTaskUseCase`: タスク完了
- `DeleteTaskUseCase`: タスク削除
- `QueryTodayTasksUseCase`: 今日のタスク一覧
- `QueryAllTasksUseCase`: 全タスク一覧

### FR-2: Slack Command Parser

自然言語でのタスク操作を解析：

- `タスク登録: [タスク名] 期限: [日時]` → RegisterTaskUseCase
- `今日のタスクは？` → QueryTodayTasksUseCase
- `タスク一覧` → QueryAllTasksUseCase
- `タスク [ID] を完了` → CompleteTaskUseCase
- `タスク [ID] を削除` → DeleteTaskUseCase

### FR-3: Task Context Generation

```python
async def _generate_task_context(self, user_id: str) -> str:
    """Generate task context for system prompt"""
    tasks = await self.task_repository.list_due_today(user_id)
    handoffs = await self.handoff_repository.list_by_to_user(user_id)

    context = "今日のタスク:\n"
    for task in tasks:
        context += f"- [{task.id}] {task.title} (期限: {task.due_at.strftime('%H:%M')})\n"

    if handoffs:
        context += "\n保留中のハンドオフ:\n"
        for handoff in handoffs:
            context += f"- [{handoff.task_id}] {handoff.from_user_id} → {handoff.to_user_id} ({handoff.handoff_at.strftime('%m/%d %H:%M')})\n"

    return context
```

### FR-4: Date/Time Parsing

自然言語の日時表現を解析：

- `明日15時` → `2025-10-15 15:00:00`
- `来週月曜` → `2025-10-21 09:00:00`
- `今日中` → `2025-10-14 23:59:59`
- `3日後` → `2025-10-17 23:59:59`

## Non-Functional Requirements

### NFR-1: Performance
- タスク登録: 200ms以内
- タスク一覧取得: 100ms以内
- システムプロンプト生成: 50ms以内

### NFR-2: Usability
- 自然言語でタスク操作できる
- エラーメッセージは分かりやすい
- 確認が必要な操作は確認ダイアログ

### NFR-3: Reliability
- タスク操作はトランザクション管理
- エラー時はロールバック
- 削除操作は論理削除（オプション）

## Success Metrics

### Phase 2完了基準

1. **Task CRUD**:
   - [ ] タスク登録・更新・削除・一覧が正常動作
   - [ ] Slack経由で全操作可能

2. **Task Context Injection**:
   - [ ] `{task_context}` が正しく注入される
   - [ ] システムプロンプトにタスク情報が反映される

3. **User Experience**:
   - [ ] 自然言語でタスク操作できる
   - [ ] エラーメッセージが分かりやすい

4. **Performance**:
   - [ ] タスク登録: 200ms以内
   - [ ] タスク一覧: 100ms以内

## Out of Scope (Phase 2では実装しない)

- ❌ ハンドオフ管理（Phase 3）
- ❌ チーム全体のタスク一覧（Phase 4）
- ❌ リマインダー自動送信（Phase 4）
- ❌ Admin UI（Phase 4）

**Phase 2のスコープ**: タスクCRUD + `{task_context}` 変数実装のみ
