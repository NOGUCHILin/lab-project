# Phase 3: Handoff Management - Requirements

## Overview

作業引き継ぎ（ハンドオフ）機能を実装し、タスクを次の担当者にスムーズに引き継げるようにする。引き継ぎ予定時刻に自動リマインダーを送信する。

## User Stories

### Story 1: ハンドオフ登録

**As a** 開発者
**I want** 作業途中でタスクを次の人に引き継げる
**So that** 多日にわたるプロジェクトでスムーズに作業が進む

**Acceptance Criteria**:
- [ ] `@中村美咲 「タスク名」を [ユーザー] に引き継ぎ` で登録できる
- [ ] 進捗状況を記録できる
- [ ] 次のステップを記録できる
- [ ] 引き継ぎ予定日時を指定できる

**Example**:
```
User: @中村美咲 「API統合」を @田中太郎 に明日9時から引き継ぎ
nakamura-misaki:
  📝 ハンドオフ登録

  タスク: API統合テスト
  引き継ぎ: 野口凜 → 田中太郎
  開始予定: 明日 9:00

  進捗状況を教えてください。

User: 認証部分は完了、決済APIは未実装
nakamura-misaki:
  ✅ ハンドオフ完了

  引き継ぎ内容:
  - 進捗: 認証部分完了、決済API未実装
  - 次のステップ: 決済API実装

  明日朝8:50に @田中太郎 にリマインド送信します。
```

### Story 2: ハンドオフ一覧

**As a** チームメンバー
**I want** 自分宛のハンドオフを確認できる
**So that** 引き継ぎ予定の作業を事前に把握できる

**Acceptance Criteria**:
- [ ] `@中村美咲 引き継ぎ一覧` で自分宛のハンドオフを表示
- [ ] 引き継ぎ予定日時順に並ぶ
- [ ] 進捗状況・次のステップが表示される

**Example**:
```
User: @中村美咲 引き継ぎ一覧
nakamura-misaki:
  📋 あなた宛の引き継ぎ（2件）:

  1. API統合テスト
     - 引き継ぎ元: @野口凜
     - 開始予定: 明日 9:00
     - 進捗: 認証部分完了、決済API未実装
     - 次のステップ: 決済API実装

  2. DB移行作業
     - 引き継ぎ元: @佐藤花子
     - 開始予定: 3日後 10:00
     - 進捗: スキーマ作成完了
     - 次のステップ: データ移行スクリプト作成
```

### Story 3: 自動リマインダー

**As a** チームメンバー
**I want** 引き継ぎ予定時刻の少し前にリマインダーを受け取る
**So that** 引き継ぎを忘れずに対応できる

**Acceptance Criteria**:
- [ ] 引き継ぎ予定時刻の10分前にDM送信
- [ ] リマインダーには進捗状況・次のステップが記載される
- [ ] リマインダー送信後、再送信しない

**Example**:
```
nakamura-misaki (DM):
  🔔 引き継ぎリマインダー

  10分後（9:00）に以下の引き継ぎがあります：

  タスク: API統合テスト
  引き継ぎ元: @野口凜

  現在の進捗:
  - 認証部分完了
  - 決済API未実装

  次のステップ:
  - 決済API実装（Stripe連携）

  不明点があれば @野口凜 に確認してください。
```

### Story 4: ハンドオフ完了

**As a** チームメンバー
**I want** 引き継ぎ作業が完了したことを記録できる
**So that** ハンドオフ一覧から消える

**Acceptance Criteria**:
- [ ] `@中村美咲 ハンドオフ [ID] 完了` で完了できる
- [ ] 完了後、一覧から消える
- [ ] 元の担当者に通知される

**Example**:
```
User: @中村美咲 ハンドオフ abc12345 完了
nakamura-misaki:
  ✅ ハンドオフ完了

  タスク: API統合テスト
  引き継ぎ元: @野口凜 → あなた
  開始: 今日 9:00
  完了: 今日 17:00

  @野口凜 に完了通知を送信しました。
```

## Functional Requirements

### FR-1: Handoff Use Cases

- `RegisterHandoffUseCase`: ハンドオフ登録
- `QueryHandoffsByUserUseCase`: ユーザー宛ハンドオフ一覧
- `CompleteHandoffUseCase`: ハンドオフ完了
- `SendHandoffReminderUseCase`: リマインダー送信

### FR-2: Reminder Scheduler

```python
async def send_pending_reminders():
    """保留中のリマインダーを送信

    引き継ぎ予定時刻の10分前にDM送信
    """
    now = datetime.utcnow()
    reminder_time = now + timedelta(minutes=10)

    handoffs = await handoff_repository.list_pending_reminders(reminder_time)

    for handoff in handoffs:
        await slack_client.chat_postMessage(
            channel=handoff.to_user_id,  # DM
            text=format_handoff_reminder(handoff),
        )

        await handoff_repository.mark_reminded(handoff.id)
```

### FR-3: Task Context Update

`{task_context}` にハンドオフ情報を追加：

```python
async def _generate_task_context(self, user_id: str) -> str:
    tasks = await self.task_repository.list_due_today(user_id)
    handoffs = await self.handoff_repository.list_by_to_user(user_id)

    context = "今日のタスク:\n..."

    if handoffs:
        context += "\n保留中のハンドオフ:\n"
        for handoff in handoffs:
            context += f"- [{handoff.task_id}] {handoff.from_user_id} → あなた ({handoff.handoff_at.strftime('%m/%d %H:%M')})\n"

    return context
```

## Non-Functional Requirements

### NFR-1: Performance
- ハンドオフ登録: 200ms以内
- ハンドオフ一覧取得: 100ms以内
- リマインダー送信: 1秒以内

### NFR-2: Reliability
- リマインダーは必ず送信される（失敗時はリトライ）
- リマインダーは重複送信しない
- スケジューラーはクラッシュしても復旧可能

### NFR-3: Scalability
- 1000件のハンドオフまで対応
- 同時100件のリマインダー送信

## Success Metrics

### Phase 3完了基準

1. **Handoff CRUD**:
   - [ ] ハンドオフ登録・一覧・完了が正常動作
   - [ ] Slack経由で操作可能

2. **Reminder Scheduler**:
   - [ ] 引き継ぎ予定時刻の10分前にDM送信
   - [ ] 重複送信なし

3. **Task Context Update**:
   - [ ] `{task_context}` にハンドオフ情報が注入される

4. **Performance**:
   - [ ] ハンドオフ登録: 200ms以内
   - [ ] リマインダー送信: 1秒以内

## Out of Scope (Phase 3では実装しない)

- ❌ チーム全体のハンドオフ一覧（Phase 4）
- ❌ ハンドオフ統計・分析（Phase 4）
- ❌ カスタムリマインダー時刻（固定10分前）
- ❌ ハンドオフキャンセル機能

**Phase 3のスコープ**: ハンドオフCRUD + 自動リマインダーのみ
