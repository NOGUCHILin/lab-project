# Phase 3: Handoff Management - Tasks

## Implementation Checklist

### 1. Domain Model

- [ ] **1.1** `src/domain/models/handoff.py` 作成
  - [ ] `Handoff` Entity定義
  - [ ] `is_pending() -> bool` メソッド
  - [ ] `is_reminder_needed(current_time: datetime) -> bool` メソッド
- [ ] **1.2** `src/domain/repositories/handoff_repository.py` インターフェース定義
  - [ ] `create(handoff: Handoff) -> Handoff`
  - [ ] `get(handoff_id: UUID) -> Handoff | None`
  - [ ] `list_by_to_user(user_id: str) -> list[Handoff]`
  - [ ] `list_pending_reminders(before: datetime) -> list[Handoff]`
  - [ ] `mark_reminded(handoff_id: UUID) -> None`
  - [ ] `complete(handoff_id: UUID) -> Handoff`

### 2. Application Layer (Use Cases)

- [ ] **2.1** `src/application/dto/handoff_dto.py` 作成
  - [ ] `CreateHandoffDTO`
  - [ ] `HandoffDTO` (出力用)
- [ ] **2.2** `src/application/use_cases/register_handoff.py` 作成
- [ ] **2.3** `src/application/use_cases/query_handoffs_by_user.py` 作成
- [ ] **2.4** `src/application/use_cases/complete_handoff.py` 作成
- [ ] **2.5** `src/application/use_cases/send_handoff_reminder.py` 作成

### 3. Command Parser

- [ ] **3.1** `src/adapters/primary/handoff_command_parser.py` 作成
  - [ ] `parse(text: str, user_id: str) -> ParsedHandoffCommand`
  - [ ] `_parse_register()`: ハンドオフ登録コマンド解析
  - [ ] `_parse_list()`: ハンドオフ一覧コマンド解析
  - [ ] `_parse_complete()`: ハンドオフ完了コマンド解析

### 4. Response Formatter

- [ ] **4.1** `src/adapters/primary/handoff_response_formatter.py` 作成
  - [ ] `format_handoff_created(handoff: Handoff) -> str`
  - [ ] `format_handoff_list(handoffs: list[Handoff]) -> str`
  - [ ] `format_handoff_completed(handoff: Handoff) -> str`
  - [ ] `format_handoff_reminder(handoff: Handoff) -> str`

### 5. Task Context Update

- [ ] **5.1** `src/adapters/secondary/claude_adapter.py` 更新
  - [ ] `_generate_task_context()` にハンドオフ情報追加
    ```python
    handoffs = await self.handoff_repository.list_by_to_user(user_id)
    if handoffs:
        context += "\n保留中のハンドオフ:\n"
        for handoff in handoffs:
            context += f"- [{handoff.task_id}] <@{handoff.from_user_id}> → あなた ({handoff.handoff_at.strftime('%m/%d %H:%M')})\n"
    ```

### 6. Reminder Scheduler

- [ ] **6.1** `scripts/send_reminders.py` 作成
  - [ ] `main()`: リマインダー送信ロジック
  - [ ] エラーハンドリング（失敗時はmark_remindedしない）
- [ ] **6.2** NixOS設定追加: `modules/services/registry/nakamura-misaki-reminder.nix`
  - [ ] systemd timer設定（毎分実行）
  - [ ] systemd service設定
  - [ ] 環境変数読み込み
- [ ] **6.3** NixOS再ビルド・デプロイ

### 7. Slack Integration

- [ ] **7.1** `src/adapters/primary/slack_event_adapter.py` 更新
  - [ ] `_is_handoff_command(text: str) -> bool` 追加
  - [ ] `_handle_handoff_command()` 追加
    - [ ] コマンド解析（HandoffCommandParser）
    - [ ] Use Case実行
    - [ ] 応答生成（HandoffResponseFormatter）
    - [ ] Slack返信

### 8. Dependency Injection

- [ ] **8.1** `src/infrastructure/di.py` 更新
  - [ ] `build_register_handoff_use_case()` 追加
  - [ ] `build_query_handoffs_by_user_use_case()` 追加
  - [ ] `build_complete_handoff_use_case()` 追加
  - [ ] `build_send_handoff_reminder_use_case()` 追加

### 9. Testing

#### 9.1 Unit Tests
- [ ] **9.1.1** `tests/unit/test_handoff_command_parser.py`
  - [ ] `test_parse_register_handoff`
  - [ ] `test_parse_list_handoffs`
  - [ ] `test_parse_complete_handoff`
- [ ] **9.1.2** `tests/unit/test_register_handoff_use_case.py`
  - [ ] `test_register_handoff_success`
  - [ ] `test_register_handoff_past_date_error`
- [ ] **9.1.3** `tests/unit/test_send_handoff_reminder_use_case.py`
  - [ ] `test_send_reminders`
  - [ ] `test_no_reminders_needed`
  - [ ] `test_reminder_failure_no_mark`

#### 9.2 Integration Tests
- [ ] **9.2.1** `tests/integration/test_handoff_workflow.py`
  - [ ] `test_handoff_crud_workflow`: 登録→一覧→完了
  - [ ] `test_handoff_reminder_workflow`: 登録→リマインダー送信→mark_reminded
- [ ] **9.2.2** `tests/integration/test_task_context_with_handoffs.py`
  - [ ] `test_task_context_includes_handoffs`: `{task_context}` にハンドオフ反映

#### 9.3 E2E Tests
- [ ] **9.3.1** `tests/e2e/test_handoff_slack_commands.py`
  - [ ] `test_register_handoff_via_slack`
  - [ ] `test_list_handoffs_via_slack`
  - [ ] `test_complete_handoff_via_slack`
  - [ ] `test_handoff_reminder_dm`: リマインダーDM受信

### 10. Documentation

- [ ] **10.1** `docs/IMPLEMENTATION_PLAN.md` 更新
  - [ ] Phase 3の実装状況記録
- [ ] **10.2** `claudedocs/handoff-management.md` 作成
  - [ ] ハンドオフコマンド一覧
  - [ ] リマインダースケジューラー仕組み
  - [ ] トラブルシューティング

### 11. Deployment

- [ ] **11.1** ローカルテスト
  ```bash
  uv run pytest tests/unit/test_handoff_*.py -v
  uv run pytest tests/integration/test_handoff_*.py -v
  ```
- [ ] **11.2** Git Commit
  ```bash
  git add src/domain/models/handoff.py src/application/use_cases/ scripts/send_reminders.py
  git commit -m "feat: Implement Phase 3 - Handoff Management"
  ```
- [ ] **11.3** GitHub Push（自動デプロイ）
  ```bash
  git push origin main
  ```
- [ ] **11.4** NixOS確認
  ```bash
  ssh home-lab-01
  systemctl status nakamura-misaki-reminder.timer
  journalctl -u nakamura-misaki-reminder.service -f
  ```

### 12. Validation (Slack E2E Tests)

- [ ] **12.1** ハンドオフ登録
  - [ ] `@中村美咲 「API統合」を @田中太郎 に 明日9時 から引き継ぎ`
  - [ ] 進捗状況を入力
- [ ] **12.2** ハンドオフ一覧
  - [ ] `@中村美咲 引き継ぎ一覧`
- [ ] **12.3** リマインダー受信
  - [ ] 引き継ぎ予定時刻の10分前にDM確認
- [ ] **12.4** ハンドオフ完了
  - [ ] `@中村美咲 ハンドオフ [ID] 完了`

### 13. Post-Deployment

- [ ] **13.1** メトリクス確認
  - [ ] ハンドオフ登録時間: 200ms以内
  - [ ] リマインダー送信成功率: 99%以上
  - [ ] リマインダー送信遅延: 10秒以内
- [ ] **13.2** Scheduler動作確認
  ```bash
  ssh home-lab-01
  systemctl list-timers nakamura-misaki-reminder.timer
  ```

### 14. Rollback Plan (問題発生時のみ)

- [ ] **14.1** Reminder Timer停止
  ```bash
  ssh home-lab-01
  sudo systemctl stop nakamura-misaki-reminder.timer
  sudo systemctl disable nakamura-misaki-reminder.timer
  ```
- [ ] **14.2** Handoff機能を無効化（DI設定変更）

## Estimated Timeline

| Task | Estimated Time | Dependencies |
|------|----------------|--------------|
| 1. Domain Model | 2 hours | Phase 1 |
| 2. Application Layer | 4 hours | 1 |
| 3. Command Parser | 3 hours | - |
| 4. Response Formatter | 2 hours | - |
| 5. Task Context Update | 1 hour | 1, 2 |
| 6. Reminder Scheduler | 4 hours | 2 |
| 7. Slack Integration | 3 hours | 2, 3, 4 |
| 8. Dependency Injection | 1 hour | 2 |
| 9. Testing | 5 hours | 2, 3, 4, 5, 6, 7 |
| 10. Documentation | 1 hour | - |
| 11. Deployment | 2 hours | 9 |
| 12. Validation | 1 hour | 11 |
| 13. Post-Deployment | 1 hour | 12 |
| **Total** | **30 hours** | - |

## Dependencies

- ✅ Phase 1 (Database + Handoff Repository)
- ✅ Phase 2 (Task Context Generation)
- ⏳ NixOS systemd timer

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| リマインダー送信失敗 | High | Low | リトライ機構、失敗時はmark_remindedしない |
| リマインダー重複送信 | Medium | Low | `reminded_at IS NULL` でフィルタリング |
| Scheduler停止 | High | Low | systemd自動再起動、監視アラート |
| タイムゾーン問題 | Medium | Medium | UTC統一、表示時のみローカル変換 |

## Success Criteria

Phase 3は以下を満たせば完了：

1. **Handoff CRUD**:
   - [ ] ハンドオフ登録・一覧・完了が正常動作
   - [ ] Slack経由で操作可能

2. **Reminder Scheduler**:
   - [ ] 引き継ぎ予定時刻の10分前にDM送信
   - [ ] 重複送信なし
   - [ ] 送信成功率99%以上

3. **Task Context Update**:
   - [ ] `{task_context}` にハンドオフ情報が注入される

4. **Performance**:
   - [ ] ハンドオフ登録: 200ms以内
   - [ ] リマインダー送信: 1秒以内
