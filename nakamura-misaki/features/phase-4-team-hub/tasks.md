# Phase 4: Team Hub - Tasks

## Implementation Checklist

### 1. Domain Model

- [ ] **1.1** `src/domain/models/bottleneck.py` 作成
  - [ ] `Bottleneck` dataclass定義
  - [ ] Type enum (`task_concentration`, `overdue_tasks`, `stale_tasks`)
  - [ ] Severity enum (`high`, `medium`, `low`)
- [ ] **1.2** `src/domain/models/team_stats.py` 作成
  - [ ] `TeamStats` dataclass定義

### 2. Application Layer (Use Cases)

- [ ] **2.1** `src/application/use_cases/query_team_tasks.py` 作成
- [ ] **2.2** `src/application/use_cases/detect_bottleneck.py` 作成
- [ ] **2.3** `src/application/use_cases/query_team_stats.py` 作成

### 3. Admin UI (FastAPI)

- [ ] **3.1** `src/infrastructure/admin_ui.py` 作成
  - [ ] FastAPIアプリケーション作成
  - [ ] `/admin` ルート（Dashboard HTML）
  - [ ] `/api/team/tasks` ルート（タスク一覧API）
  - [ ] `/api/team/stats` ルート（統計API）
  - [ ] `/api/team/bottlenecks` ルート（ボトルネックAPI）
- [ ] **3.2** `templates/admin/dashboard.html` 作成
  - [ ] HTML/CSS/JavaScript実装
  - [ ] Chart.js統合
  - [ ] API呼び出し
- [ ] **3.3** FastAPIとnakamura-misaki APIを統合

### 4. Bottleneck Detection

- [ ] **4.1** `scripts/detect_bottlenecks.py` 作成
  - [ ] ボトルネック検出ロジック
  - [ ] PM宛DM送信
- [ ] **4.2** NixOS設定追加: `modules/services/registry/nakamura-misaki-bottleneck.nix`
  - [ ] systemd timer設定（daily）
  - [ ] systemd service設定
- [ ] **4.3** NixOS再ビルド・デプロイ

### 5. Slack Integration

- [ ] **5.1** `src/adapters/primary/slack_event_adapter.py` 更新
  - [ ] `_is_team_command(text: str) -> bool` 追加
  - [ ] `_handle_team_command()` 追加
    - [ ] `チームのタスク` → QueryTeamTasksUseCase
    - [ ] `今週の統計` → QueryTeamStatsUseCase
  - [ ] `_format_team_tasks()` 追加
  - [ ] `_format_team_stats()` 追加

### 6. Repository Extension

- [ ] **6.1** `src/adapters/secondary/postgresql_task_repository.py` 更新
  - [ ] `list_all(status: str | None) -> list[Task]` 追加
  - [ ] `list_overdue() -> list[Task]` 追加
  - [ ] `list_stale(days: int) -> list[Task]` 追加
  - [ ] `list_created_between(start: datetime, end: datetime) -> list[Task]` 追加
  - [ ] `count_by_user() -> dict[str, int]` 追加
- [ ] **6.2** `src/adapters/secondary/postgresql_handoff_repository.py` 更新
  - [ ] `list_created_between(start: datetime, end: datetime) -> list[Handoff]` 追加

### 7. Configuration

- [ ] **7.1** `.env.example` 更新
  ```bash
  # Admin UI
  ADMIN_UI_PORT=3002

  # Bottleneck Detection
  PM_USER_ID=U01ABC123
  ```
- [ ] **7.2** NixOS secrets設定
  ```bash
  sops secrets/nakamura-misaki.yaml
  # PM_USER_ID を追加
  ```

### 8. Dependency Injection

- [ ] **8.1** `src/infrastructure/di.py` 更新
  - [ ] `build_query_team_tasks_use_case()` 追加
  - [ ] `build_detect_bottleneck_use_case()` 追加
  - [ ] `build_query_team_stats_use_case()` 追加

### 9. Testing

#### 9.1 Unit Tests
- [ ] **9.1.1** `tests/unit/test_detect_bottleneck_use_case.py`
  - [ ] `test_detect_task_concentration`
  - [ ] `test_detect_overdue_tasks`
  - [ ] `test_detect_stale_tasks`
  - [ ] `test_no_bottlenecks`
- [ ] **9.1.2** `tests/unit/test_query_team_stats_use_case.py`
  - [ ] `test_query_team_stats`
  - [ ] `test_completion_rate_calculation`

#### 9.2 Integration Tests
- [ ] **9.2.1** `tests/integration/test_admin_ui.py`
  - [ ] `test_admin_ui_team_tasks`
  - [ ] `test_admin_ui_team_stats`
  - [ ] `test_admin_ui_bottlenecks`
- [ ] **9.2.2** `tests/integration/test_bottleneck_detection.py`
  - [ ] `test_detect_bottlenecks_workflow`
  - [ ] `test_send_bottleneck_notification`

#### 9.3 E2E Tests
- [ ] **9.3.1** `tests/e2e/test_team_slack_commands.py`
  - [ ] `test_team_tasks_via_slack`
  - [ ] `test_team_stats_via_slack`
- [ ] **9.3.2** `tests/e2e/test_admin_ui_browser.py`
  - [ ] `test_admin_ui_loads`: Admin UIが表示される
  - [ ] `test_admin_ui_charts`: グラフが表示される

### 10. Documentation

- [ ] **10.1** `docs/IMPLEMENTATION_PLAN.md` 更新
  - [ ] Phase 4の実装状況記録
- [ ] **10.2** `claudedocs/admin-ui.md` 作成
  - [ ] Admin UIの使い方
  - [ ] APIエンドポイント一覧
  - [ ] ボトルネック検出ロジック

### 11. Deployment

- [ ] **11.1** ローカルテスト
  ```bash
  uv run pytest tests/unit/test_*team*.py -v
  uv run pytest tests/integration/test_admin_ui.py -v
  ```
- [ ] **11.2** Admin UI起動確認
  ```bash
  uv run uvicorn src.infrastructure.admin_ui:app --reload --port 3002
  # http://localhost:3002/admin にアクセス
  ```
- [ ] **11.3** Git Commit
  ```bash
  git add src/application/use_cases/ src/infrastructure/admin_ui.py templates/
  git commit -m "feat: Implement Phase 4 - Team Hub & Admin UI"
  ```
- [ ] **11.4** GitHub Push（自動デプロイ）
  ```bash
  git push origin main
  ```
- [ ] **11.5** NixOS確認
  ```bash
  ssh home-lab-01
  systemctl status nakamura-misaki-admin.service
  systemctl status nakamura-misaki-bottleneck.timer
  ```

### 12. Validation

- [ ] **12.1** Admin UI動作確認
  - [ ] https://nakamura-misaki-admin.your-domain.ts.net/admin にアクセス
  - [ ] Dashboard表示確認
  - [ ] グラフ表示確認
  - [ ] ボトルネック表示確認
- [ ] **12.2** Slackコマンド確認
  - [ ] `@中村美咲 チームのタスク`
  - [ ] `@中村美咲 今週の統計`
- [ ] **12.3** ボトルネック検出確認
  - [ ] タスクを5件以上登録
  - [ ] ボトルネック検出スクリプト手動実行
  - [ ] PM宛にDM送信確認

### 13. Post-Deployment

- [ ] **13.1** メトリクス確認
  - [ ] Admin UIリクエスト数
  - [ ] Admin UIレスポンスタイム: 1秒以内
  - [ ] ボトルネック検出時間: 500ms以内
- [ ] **13.2** Scheduler動作確認
  ```bash
  ssh home-lab-01
  systemctl list-timers nakamura-misaki-bottleneck.timer
  ```

### 14. Rollback Plan (問題発生時のみ)

- [ ] **14.1** Admin UI停止
  ```bash
  ssh home-lab-01
  sudo systemctl stop nakamura-misaki-admin.service
  sudo systemctl disable nakamura-misaki-admin.service
  ```
- [ ] **14.2** Bottleneck Detection停止
  ```bash
  sudo systemctl stop nakamura-misaki-bottleneck.timer
  sudo systemctl disable nakamura-misaki-bottleneck.timer
  ```

## Estimated Timeline

| Task | Estimated Time | Dependencies |
|------|----------------|--------------|
| 1. Domain Model | 2 hours | - |
| 2. Application Layer | 4 hours | 1 |
| 3. Admin UI | 8 hours | 2 |
| 4. Bottleneck Detection | 3 hours | 2 |
| 5. Slack Integration | 3 hours | 2 |
| 6. Repository Extension | 3 hours | Phase 1 |
| 7. Configuration | 1 hour | - |
| 8. Dependency Injection | 1 hour | 2 |
| 9. Testing | 6 hours | 2, 3, 4, 5 |
| 10. Documentation | 2 hours | - |
| 11. Deployment | 2 hours | 9 |
| 12. Validation | 2 hours | 11 |
| 13. Post-Deployment | 1 hour | 12 |
| **Total** | **38 hours** | - |

## Dependencies

- ✅ Phase 1 (Database)
- ✅ Phase 2 (Task API)
- ✅ Phase 3 (Handoff Management)
- ⏳ Chart.js（グラフ表示用）
- ⏳ Jinja2（テンプレートエンジン）

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Admin UI実装が複雑 | High | Medium | シンプルなHTML/JS、Chart.js使用 |
| ボトルネック検出の精度低い | Medium | Medium | しきい値を調整可能にする、フィードバック収集 |
| パフォーマンス低下 | Medium | Low | キャッシュ機構、ページネーション |
| Admin UI認証不十分 | High | Low | Slack OAuth実装（Phase 4.5で検討）|

## Success Criteria

Phase 4は以下を満たせば完了：

1. **Team Hub**:
   - [ ] チーム全体のタスク一覧が表示される
   - [ ] ボトルネック検出が動作する
   - [ ] Slackコマンドで操作可能

2. **Admin UI**:
   - [ ] Web UIが表示される
   - [ ] タスク一覧・グラフが表示される
   - [ ] ボトルネックが表示される

3. **Statistics**:
   - [ ] 週次統計が表示される
   - [ ] メンバー別完了数が表示される

4. **Performance**:
   - [ ] チーム全体タスク取得: 500ms以内
   - [ ] Admin UI読み込み: 1秒以内
   - [ ] ボトルネック検出: 500ms以内

## Notes

- Admin UI認証はPhase 4では未実装（Tailscale Serveで保護）
- Phase 4.5でSlack OAuth実装を検討
- グラフライブラリはChart.js（CDN）を使用
