# Phase 2: Task API - Tasks

## Implementation Checklist

### 1. Domain Model

- [ ] **1.1** `src/domain/models/task.py` 作成
  - [ ] `Task` Entity定義
  - [ ] Status enum (`pending`, `in_progress`, `completed`, `cancelled`)
  - [ ] `complete()` メソッド（ビジネスロジック）
  - [ ] `cancel()` メソッド
- [ ] **1.2** `src/domain/repositories/task_repository.py` インターフェース定義
  - [ ] `create(task: Task) -> Task`
  - [ ] `get(task_id: UUID) -> Task | None`
  - [ ] `update(task: Task) -> Task`
  - [ ] `delete(task_id: UUID) -> None`
  - [ ] `list_by_user(user_id: str, status: str | None) -> list[Task]`
  - [ ] `list_due_today(user_id: str) -> list[Task]`

### 2. Application Layer (Use Cases)

- [ ] **2.1** `src/application/dto/task_dto.py` 作成
  - [ ] `CreateTaskDTO`
  - [ ] `UpdateTaskDTO`
  - [ ] `TaskDTO` (出力用)
- [ ] **2.2** `src/application/use_cases/register_task.py` 作成
- [ ] **2.3** `src/application/use_cases/update_task.py` 作成
- [ ] **2.4** `src/application/use_cases/complete_task.py` 作成
- [ ] **2.5** `src/application/use_cases/delete_task.py` 作成
- [ ] **2.6** `src/application/use_cases/query_today_tasks.py` 作成
- [ ] **2.7** `src/application/use_cases/query_all_tasks.py` 作成

### 3. Command Parser

- [ ] **3.1** `src/adapters/primary/task_command_parser.py` 作成
  - [ ] `parse(text: str, user_id: str) -> ParsedCommand`
  - [ ] `_parse_register()`: タスク登録コマンド解析
  - [ ] `_parse_complete()`: タスク完了コマンド解析
  - [ ] `_parse_delete()`: タスク削除コマンド解析
  - [ ] `_parse_datetime()`: 自然言語日時解析
    - [ ] "明日15時" → `datetime`
    - [ ] "今日中" → `datetime`
    - [ ] "N日後" → `datetime`
    - [ ] "来週月曜" → `datetime`

### 4. Response Formatter

- [ ] **4.1** `src/adapters/primary/task_response_formatter.py` 作成
  - [ ] `format_task_created(task: Task) -> str`
  - [ ] `format_today_tasks(tasks: list[Task]) -> str`
  - [ ] `format_all_tasks(tasks: list[Task]) -> str`
  - [ ] `format_task_completed(task: Task) -> str`
  - [ ] `format_task_deleted(task: Task) -> str`
  - [ ] `format_error(error: str) -> str`

### 5. Task Context Generation

- [ ] **5.1** `src/adapters/secondary/claude_adapter.py` 更新
  - [ ] `_generate_task_context()` 実装（Phase 0では空文字列）
    ```python
    async def _generate_task_context(self, user_id: str) -> str:
        tasks = await self.task_repository.list_due_today(user_id)
        if not tasks:
            return "今日のタスク: なし"

        context = "今日のタスク:\n"
        for task in tasks:
            due_time = task.due_at.strftime("%H:%M") if task.due_at else "期限なし"
            status_icon = {"pending": "⏸️", "in_progress": "▶️", "completed": "✅"}.get(task.status, "")
            context += f"- [{task.id}] {task.title} ({due_time}) {status_icon}\n"

        return context
    ```

### 6. Slack Integration

- [ ] **6.1** `src/adapters/primary/slack_event_adapter.py` 更新
  - [ ] `_is_task_command(text: str) -> bool` 追加
  - [ ] `_handle_task_command()` 追加
    - [ ] コマンド解析（TaskCommandParser）
    - [ ] Use Case実行
    - [ ] 応答生成（TaskResponseFormatter）
    - [ ] Slack返信
  - [ ] エラーハンドリング追加

### 7. Dependency Injection

- [ ] **7.1** `src/infrastructure/di.py` 更新
  - [ ] `build_register_task_use_case()` 追加
  - [ ] `build_query_today_tasks_use_case()` 追加
  - [ ] `build_complete_task_use_case()` 追加
  - [ ] `build_delete_task_use_case()` 追加
  - [ ] `build_task_command_parser()` 追加

### 8. Testing

#### 8.1 Unit Tests
- [ ] **8.1.1** `tests/unit/test_task_command_parser.py`
  - [ ] `test_parse_register_with_due_date`
  - [ ] `test_parse_register_without_due_date`
  - [ ] `test_parse_register_with_assignee`
  - [ ] `test_parse_list_today`
  - [ ] `test_parse_complete`
  - [ ] `test_parse_delete`
  - [ ] `test_parse_datetime_tomorrow`
  - [ ] `test_parse_datetime_today`
  - [ ] `test_parse_datetime_next_week`
- [ ] **8.1.2** `tests/unit/test_register_task_use_case.py`
  - [ ] `test_register_task_success`
  - [ ] `test_register_task_validation_error`
  - [ ] `test_register_task_with_due_date`
- [ ] **8.1.3** `tests/unit/test_task_response_formatter.py`
  - [ ] `test_format_task_created`
  - [ ] `test_format_today_tasks_empty`
  - [ ] `test_format_today_tasks_multiple`

#### 8.2 Integration Tests
- [ ] **8.2.1** `tests/integration/test_task_workflow.py`
  - [ ] `test_task_crud_workflow`: 登録→一覧→完了→削除
  - [ ] `test_task_context_generation`: `{task_context}` 変数生成
  - [ ] `test_multiple_users_tasks`: 複数ユーザーのタスク分離

#### 8.3 E2E Tests
- [ ] **8.3.1** `tests/e2e/test_task_slack_commands.py`
  - [ ] `test_register_task_via_slack`
  - [ ] `test_list_today_tasks_via_slack`
  - [ ] `test_complete_task_via_slack`
  - [ ] `test_task_context_injection`: システムプロンプトにタスク反映

### 9. Documentation

- [ ] **9.1** `docs/IMPLEMENTATION_PLAN.md` 更新
  - [ ] Phase 2の実装状況記録
- [ ] **9.2** `claudedocs/task-management.md` 作成
  - [ ] タスクコマンド一覧
  - [ ] 日時解析の例
  - [ ] エラーメッセージ一覧

### 10. Deployment

- [ ] **10.1** ローカルテスト
  ```bash
  uv run pytest tests/unit/test_task_*.py -v
  uv run pytest tests/integration/test_task_*.py -v
  ```
- [ ] **10.2** Git Commit
  ```bash
  git add src/domain/models/task.py src/application/use_cases/ src/adapters/primary/task_*.py
  git commit -m "feat: Implement Phase 2 - Task API"
  ```
- [ ] **10.3** GitHub Push（自動デプロイ）
  ```bash
  git push origin main
  ```
- [ ] **10.4** デプロイ確認
  ```bash
  gh run watch
  ssh home-lab-01
  journalctl -u nakamura-misaki-api.service -f
  ```

### 11. Validation (Slack E2E Tests)

- [ ] **11.1** タスク登録
  - [ ] `@中村美咲 タスク登録: API統合 期限: 明日15時`
  - [ ] `@中村美咲 タスク登録: ドキュメント更新` （期限なし）
- [ ] **11.2** タスク一覧
  - [ ] `@中村美咲 今日のタスクは？`
  - [ ] `@中村美咲 タスク一覧`
- [ ] **11.3** タスク完了
  - [ ] `@中村美咲 タスク [ID] を完了`
- [ ] **11.4** Task Context注入
  - [ ] 質問: "今何をすべき？"
  - [ ] システムプロンプトにタスクが反映されていることを確認

### 12. Post-Deployment

- [ ] **12.1** メトリクス確認
  - [ ] タスク登録時間: 200ms以内
  - [ ] タスク一覧取得: 100ms以内
  - [ ] `{task_context}` 生成: 50ms以内
- [ ] **12.2** エラーレート確認
  - [ ] タスクコマンドエラー率: 5%以下
- [ ] **12.3** ユーザーフィードバック収集
  - [ ] 自然言語コマンドの使いやすさ
  - [ ] エラーメッセージの分かりやすさ

### 13. Rollback Plan (問題発生時のみ)

- [ ] **13.1** Task Context注入を無効化
  ```python
  # claude_adapter.py
  async def _generate_task_context(self, user_id: str) -> str:
      return ""  # 一時的に空文字列を返す
  ```
- [ ] **13.2** 再デプロイ
  ```bash
  git add src/adapters/secondary/claude_adapter.py
  git commit -m "fix: Temporarily disable task context injection"
  git push origin main
  ```

## Estimated Timeline

| Task | Estimated Time | Dependencies |
|------|----------------|--------------|
| 1. Domain Model | 2 hours | Phase 1 |
| 2. Application Layer | 4 hours | 1 |
| 3. Command Parser | 4 hours | - |
| 4. Response Formatter | 2 hours | - |
| 5. Task Context Generation | 2 hours | 1, 2 |
| 6. Slack Integration | 3 hours | 2, 3, 4 |
| 7. Dependency Injection | 1 hour | 2 |
| 8. Testing | 5 hours | 2, 3, 4, 5, 6 |
| 9. Documentation | 1 hour | - |
| 10. Deployment | 1 hour | 8 |
| 11. Validation | 1 hour | 10 |
| 12. Post-Deployment | 1 hour | 11 |
| **Total** | **27 hours** | - |

## Dependencies

- ✅ Phase 1 (Database + Task Repository)
- ✅ Phase 0 (System Prompt with `{task_context}` variable)
- ⏳ dateutil library（日時解析用）

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| 自然言語解析の精度低い | Medium | Medium | パターンマッチング強化、エラーメッセージで例を提示 |
| 日時解析の精度低い | Medium | Medium | dateutil使用、よくあるパターンを優先処理 |
| Task Context注入でトークン増加 | Low | Low | 最大10件に制限、簡潔なフォーマット |
| コマンド解析エラー多発 | Medium | Medium | ユーザーフィードバックで改善、Claudeにフォールバック |

## Success Criteria

Phase 2は以下を満たせば完了：

1. **Task CRUD**:
   - [ ] タスク登録・更新・削除・一覧が正常動作
   - [ ] 自然言語コマンドでタスク操作可能

2. **Task Context Injection**:
   - [ ] `{task_context}` が正しく生成される
   - [ ] システムプロンプトにタスク情報が反映される

3. **Performance**:
   - [ ] タスク登録: 200ms以内
   - [ ] タスク一覧: 100ms以内
   - [ ] Task Context生成: 50ms以内

4. **User Experience**:
   - [ ] エラーメッセージが分かりやすい
   - [ ] 日時解析が正確（よくあるパターン）
