# Phase 4: Team Hub - Requirements

## Overview

チーム全体のタスク・ハンドオフを可視化するAdmin UIを実装する。nakamura-misakiがチームの状況を把握し、ボトルネックを検出できるようにする。

## User Stories

### Story 1: チーム全体のタスク一覧

**As a** プロジェクトマネージャー
**I want** チーム全体のタスクを確認できる
**So that** チームの状況を把握できる

**Acceptance Criteria**:
- [ ] `@中村美咲 チームのタスク` でチーム全体のタスクを表示
- [ ] メンバー別にグループ化される
- [ ] 期限順に並ぶ
- [ ] ステータスが表示される

**Example**:
```
User: @中村美咲 チームのタスク
nakamura-misaki:
  📊 チーム全体のタスク（8件）

  野口凜 (3件):
  - [abc12345] API統合テスト (今日15:00) ▶️
  - [def67890] ドキュメント更新 (今日18:00) ⏸️
  - [ghi11111] レビュー対応 (期限なし) ⏸️

  田中太郎 (2件):
  - [jkl22222] DB移行 (明日10:00) ▶️
  - [mno33333] UI改善 (明後日16:00) ⏸️

  佐藤花子 (3件):
  - [pqr44444] テスト実装 (今日17:00) ▶️
  - [stu55555] 設計レビュー (明日14:00) ⏸️
  - [vwx66666] パフォーマンス改善 (来週) ⏸️
```

### Story 2: ボトルネック検出

**As a** nakamura-misaki
**I want** タスクの偏りを検出できる
**So that** プロジェクトマネージャーにアラートできる

**Acceptance Criteria**:
- [ ] 1人に5件以上タスクが集中したら警告
- [ ] 期限切れタスクがあったら警告
- [ ] 進行中タスクが長期間更新されていなかったら警告

**Example**:
```
nakamura-misaki (自発的にDM):
  ⚠️ タスクボトルネック検出

  野口凜さんにタスクが集中しています（5件）。
  他のメンバーに分散を検討してください。

  期限切れタスク:
  - [abc12345] API統合テスト（期限: 昨日15:00）

  長期停滞タスク（3日以上更新なし）:
  - [ghi11111] レビュー対応（野口凜）
```

### Story 3: Admin UI

**As a** プロジェクトマネージャー
**I want** Web UIでチーム全体を確認できる
**So that** Slackを開かなくても状況を把握できる

**Acceptance Criteria**:
- [ ] `/admin` でWeb UI表示
- [ ] チーム全体のタスク一覧
- [ ] メンバー別タスク数グラフ
- [ ] 期限別タスク数グラフ
- [ ] ハンドオフ一覧

**UI Mockup**:
```
+-----------------------------------+
| nakamura-misaki Admin             |
+-----------------------------------+
| [Dashboard] [Tasks] [Handoffs]    |
+-----------------------------------+

Dashboard:
- チーム全体: 8タスク
- 今日期限: 3タスク
- 期限切れ: 1タスク
- ハンドオフ予定: 2件

[グラフ] メンバー別タスク数
野口凜: ████████ 3件
田中太郎: █████ 2件
佐藤花子: ████████ 3件

[グラフ] 期限別タスク数
今日: ███ 3件
明日: ██ 2件
今週: █████ 5件
```

### Story 4: チーム統計

**As a** プロジェクトマネージャー
**I want** チームのタスク完了率・ハンドオフ回数を確認できる
**So that** チームのパフォーマンスを評価できる

**Acceptance Criteria**:
- [ ] 週次タスク完了率
- [ ] メンバー別タスク完了数
- [ ] ハンドオフ回数（週次）
- [ ] 平均タスク所要時間

**Example**:
```
User: @中村美咲 今週の統計
nakamura-misaki:
  📈 今週の統計（10/7 - 10/13）

  タスク完了率: 85% (17/20件)

  メンバー別完了数:
  - 野口凜: 6件
  - 田中太郎: 5件
  - 佐藤花子: 6件

  ハンドオフ回数: 3件
  平均タスク所要時間: 4.2時間
```

## Functional Requirements

### FR-1: Team Hub Use Cases

- `QueryTeamTasksUseCase`: チーム全体のタスク一覧
- `DetectBottleneckUseCase`: ボトルネック検出
- `QueryTeamStatsUseCase`: チーム統計取得

### FR-2: Admin UI

- FastAPI + Jinja2テンプレート
- REST API: `/api/team/tasks`, `/api/team/handoffs`, `/api/team/stats`
- 認証: Slack OAuth

### FR-3: Bottleneck Detection Logic

```python
async def detect_bottlenecks() -> list[Bottleneck]:
    """ボトルネック検出

    Returns:
        検出されたボトルネック一覧
    """
    bottlenecks = []

    # 1. タスク集中検出（5件以上）
    user_task_counts = await task_repository.count_by_user()
    for user_id, count in user_task_counts.items():
        if count >= 5:
            bottlenecks.append(Bottleneck(
                type="task_concentration",
                user_id=user_id,
                severity="high",
                message=f"{user_id}にタスクが集中（{count}件）",
            ))

    # 2. 期限切れタスク検出
    overdue_tasks = await task_repository.list_overdue()
    if overdue_tasks:
        bottlenecks.append(Bottleneck(
            type="overdue_tasks",
            severity="high",
            message=f"期限切れタスク: {len(overdue_tasks)}件",
            tasks=overdue_tasks,
        ))

    # 3. 長期停滞タスク検出（3日以上更新なし）
    stale_tasks = await task_repository.list_stale(days=3)
    if stale_tasks:
        bottlenecks.append(Bottleneck(
            type="stale_tasks",
            severity="medium",
            message=f"長期停滞タスク: {len(stale_tasks)}件",
            tasks=stale_tasks,
        ))

    return bottlenecks
```

## Non-Functional Requirements

### NFR-1: Performance
- チーム全体タスク取得: 500ms以内
- Admin UI読み込み: 1秒以内
- ボトルネック検出: 500ms以内

### NFR-2: Scalability
- 10人のチームまで対応
- 100タスクまで対応

### NFR-3: Security
- Admin UIはSlack OAuthで認証
- APIエンドポイントはトークン認証

## Success Metrics

### Phase 4完了基準

1. **Team Hub**:
   - [ ] チーム全体のタスク一覧が表示される
   - [ ] ボトルネック検出が動作する

2. **Admin UI**:
   - [ ] Web UIが表示される
   - [ ] タスク一覧・グラフが表示される

3. **Statistics**:
   - [ ] 週次統計が表示される
   - [ ] メンバー別完了数が表示される

4. **Performance**:
   - [ ] チーム全体タスク取得: 500ms以内
   - [ ] Admin UI読み込み: 1秒以内

## Out of Scope (v4.0では実装しない)

- ❌ カスタムダッシュボード
- ❌ エクスポート機能（CSV/Excel）
- ❌ 通知設定カスタマイズ
- ❌ Multi-workspace対応

**Phase 4のスコープ**: Team Hub + Admin UI + 統計のみ
