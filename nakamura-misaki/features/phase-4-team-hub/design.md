# Phase 4: Team Hub - Design

## System Architecture

### Admin UI Architecture

```
Browser → FastAPI (Admin UI) → Use Cases → PostgreSQL
                              → Slack OAuth
```

### Bottleneck Detection Flow

```
Cron Job (daily) → DetectBottleneckUseCase → PostgreSQL
                                           ↓
                                      Slack DM (PM宛)
```

## Use Case Implementation

### QueryTeamTasksUseCase

```python
from src.domain.repositories.task_repository import TaskRepository

class QueryTeamTasksUseCase:
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self) -> dict[str, list[Task]]:
        """チーム全体のタスク一覧取得

        Returns:
            ユーザーID→タスク一覧のdict
        """
        all_tasks = await self._task_repository.list_all()

        # ユーザーごとにグループ化
        tasks_by_user: dict[str, list[Task]] = {}
        for task in all_tasks:
            if task.assignee_user_id not in tasks_by_user:
                tasks_by_user[task.assignee_user_id] = []
            tasks_by_user[task.assignee_user_id].append(task)

        # 各ユーザーのタスクを期限順にソート
        for user_id in tasks_by_user:
            tasks_by_user[user_id].sort(key=lambda t: t.due_at or datetime.max)

        return tasks_by_user
```

### DetectBottleneckUseCase

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Bottleneck:
    type: str  # "task_concentration", "overdue_tasks", "stale_tasks"
    severity: str  # "high", "medium", "low"
    message: str
    user_id: str | None = None
    tasks: list[Task] | None = None

class DetectBottleneckUseCase:
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    async def execute(self) -> list[Bottleneck]:
        """ボトルネック検出"""
        bottlenecks = []

        # 1. タスク集中検出（5件以上）
        user_task_counts = await self._count_tasks_by_user()
        for user_id, count in user_task_counts.items():
            if count >= 5:
                bottlenecks.append(Bottleneck(
                    type="task_concentration",
                    user_id=user_id,
                    severity="high",
                    message=f"<@{user_id}>にタスクが集中（{count}件）",
                ))

        # 2. 期限切れタスク検出
        overdue_tasks = await self._task_repository.list_overdue()
        if overdue_tasks:
            bottlenecks.append(Bottleneck(
                type="overdue_tasks",
                severity="high",
                message=f"期限切れタスク: {len(overdue_tasks)}件",
                tasks=overdue_tasks,
            ))

        # 3. 長期停滞タスク検出（3日以上更新なし）
        stale_tasks = await self._task_repository.list_stale(days=3)
        if stale_tasks:
            bottlenecks.append(Bottleneck(
                type="stale_tasks",
                severity="medium",
                message=f"長期停滞タスク（3日以上更新なし）: {len(stale_tasks)}件",
                tasks=stale_tasks,
            ))

        return bottlenecks

    async def _count_tasks_by_user(self) -> dict[str, int]:
        """ユーザーごとのタスク数集計"""
        all_tasks = await self._task_repository.list_all(status="pending")
        counts: dict[str, int] = {}
        for task in all_tasks:
            counts[task.assignee_user_id] = counts.get(task.assignee_user_id, 0) + 1
        return counts
```

### QueryTeamStatsUseCase

```python
from datetime import datetime, timedelta

@dataclass
class TeamStats:
    start_date: datetime
    end_date: datetime
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    completed_by_user: dict[str, int]
    handoff_count: int
    avg_task_duration_hours: float

class QueryTeamStatsUseCase:
    def __init__(
        self,
        task_repository: TaskRepository,
        handoff_repository: HandoffRepository,
    ):
        self._task_repository = task_repository
        self._handoff_repository = handoff_repository

    async def execute(self, start_date: datetime, end_date: datetime) -> TeamStats:
        """チーム統計取得

        Args:
            start_date: 集計開始日
            end_date: 集計終了日

        Returns:
            チーム統計
        """
        # 期間内に作成されたタスク
        all_tasks = await self._task_repository.list_created_between(start_date, end_date)
        completed_tasks = [t for t in all_tasks if t.status == "completed"]

        # 完了率
        total_tasks = len(all_tasks)
        completed_count = len(completed_tasks)
        completion_rate = completed_count / total_tasks if total_tasks > 0 else 0.0

        # メンバー別完了数
        completed_by_user: dict[str, int] = {}
        for task in completed_tasks:
            user = task.assignee_user_id
            completed_by_user[user] = completed_by_user.get(user, 0) + 1

        # ハンドオフ回数
        handoffs = await self._handoff_repository.list_created_between(start_date, end_date)
        handoff_count = len(handoffs)

        # 平均タスク所要時間
        durations = [
            (t.completed_at - t.created_at).total_seconds() / 3600
            for t in completed_tasks
            if t.completed_at
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        return TeamStats(
            start_date=start_date,
            end_date=end_date,
            total_tasks=total_tasks,
            completed_tasks=completed_count,
            completion_rate=completion_rate,
            completed_by_user=completed_by_user,
            handoff_count=handoff_count,
            avg_task_duration_hours=avg_duration,
        )
```

## Admin UI Implementation

### FastAPI Routes

```python
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin Dashboard"""
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
    })

@app.get("/api/team/tasks")
async def get_team_tasks():
    """チーム全体のタスク一覧API"""
    use_case = build_query_team_tasks_use_case()
    tasks_by_user = await use_case.execute()

    # JSON serializable形式に変換
    return {
        user_id: [task.to_dict() for task in tasks]
        for user_id, tasks in tasks_by_user.items()
    }

@app.get("/api/team/stats")
async def get_team_stats(days: int = 7):
    """チーム統計API"""
    use_case = build_query_team_stats_use_case()

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    stats = await use_case.execute(start_date, end_date)

    return {
        "start_date": stats.start_date.isoformat(),
        "end_date": stats.end_date.isoformat(),
        "total_tasks": stats.total_tasks,
        "completed_tasks": stats.completed_tasks,
        "completion_rate": stats.completion_rate,
        "completed_by_user": stats.completed_by_user,
        "handoff_count": stats.handoff_count,
        "avg_task_duration_hours": stats.avg_task_duration_hours,
    }

@app.get("/api/team/bottlenecks")
async def get_team_bottlenecks():
    """ボトルネック検出API"""
    use_case = build_detect_bottleneck_use_case()
    bottlenecks = await use_case.execute()

    return [
        {
            "type": b.type,
            "severity": b.severity,
            "message": b.message,
            "user_id": b.user_id,
            "tasks": [t.to_dict() for t in b.tasks] if b.tasks else [],
        }
        for b in bottlenecks
    ]
```

### HTML Templates

**templates/admin/dashboard.html**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>nakamura-misaki Admin</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; }
        .metric { font-size: 2em; font-weight: bold; }
        canvas { max-width: 600px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>nakamura-misaki Admin</h1>

        <div class="card">
            <h2>Dashboard</h2>
            <div id="metrics"></div>
        </div>

        <div class="card">
            <h2>メンバー別タスク数</h2>
            <canvas id="tasksByUserChart"></canvas>
        </div>

        <div class="card">
            <h2>ボトルネック</h2>
            <div id="bottlenecks"></div>
        </div>
    </div>

    <script>
        // Fetch team tasks
        fetch('/api/team/tasks')
            .then(res => res.json())
            .then(data => {
                const taskCounts = {};
                for (const [userId, tasks] of Object.entries(data)) {
                    taskCounts[userId] = tasks.length;
                }

                // Display metrics
                const totalTasks = Object.values(taskCounts).reduce((a, b) => a + b, 0);
                document.getElementById('metrics').innerHTML = `
                    <p>チーム全体: <span class="metric">${totalTasks}</span> タスク</p>
                `;

                // Chart
                const ctx = document.getElementById('tasksByUserChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(taskCounts),
                        datasets: [{
                            label: 'タスク数',
                            data: Object.values(taskCounts),
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        }]
                    }
                });
            });

        // Fetch bottlenecks
        fetch('/api/team/bottlenecks')
            .then(res => res.json())
            .then(data => {
                if (data.length === 0) {
                    document.getElementById('bottlenecks').innerHTML = '<p>ボトルネックは検出されませんでした。</p>';
                } else {
                    const html = data.map(b => `
                        <div style="border-left: 4px solid ${b.severity === 'high' ? 'red' : 'orange'}; padding-left: 10px; margin: 10px 0;">
                            <strong>${b.message}</strong>
                        </div>
                    `).join('');
                    document.getElementById('bottlenecks').innerHTML = html;
                }
            });
    </script>
</body>
</html>
```

## Slack Integration

### Team Commands

```python
# src/adapters/primary/slack_event_adapter.py

async def _handle_team_command(self, text: str, user_id: str, channel: str):
    """チームコマンド処理"""
    if "チームのタスク" in text:
        # チーム全体のタスク一覧
        use_case = build_query_team_tasks_use_case()
        tasks_by_user = await use_case.execute()
        response = self._format_team_tasks(tasks_by_user)

    elif "今週の統計" in text:
        # 週次統計
        use_case = build_query_team_stats_use_case()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        stats = await use_case.execute(start_date, end_date)
        response = self._format_team_stats(stats)

    await self.slack_client.chat_postMessage(channel=channel, text=response)

def _format_team_tasks(self, tasks_by_user: dict[str, list[Task]]) -> str:
    """チーム全体のタスク一覧フォーマット"""
    total_count = sum(len(tasks) for tasks in tasks_by_user.values())
    lines = [f"📊 チーム全体のタスク（{total_count}件）\n"]

    for user_id, tasks in tasks_by_user.items():
        lines.append(f"<@{user_id}> ({len(tasks)}件):")
        for task in tasks[:3]:  # 最大3件表示
            due_str = task.due_at.strftime("%m/%d %H:%M") if task.due_at else "期限なし"
            status_icon = {"pending": "⏸️", "in_progress": "▶️", "completed": "✅"}.get(task.status, "")
            lines.append(f"- [{task.id}] {task.title} ({due_str}) {status_icon}")
        if len(tasks) > 3:
            lines.append(f"  ...他{len(tasks) - 3}件")
        lines.append("")

    return "\n".join(lines)
```

## Bottleneck Notification

### Scheduler (Daily)

```nix
# NixOS設定

systemd.timers.nakamura-misaki-bottleneck = {
  wantedBy = [ "timers.target" ];
  timerConfig = {
    OnCalendar = "daily";
    OnBootSec = "10m";
    Unit = "nakamura-misaki-bottleneck.service";
  };
};

systemd.services.nakamura-misaki-bottleneck = {
  description = "nakamura-misaki Bottleneck Detection";
  serviceConfig = {
    Type = "oneshot";
    ExecStart = "${pkgs.python3}/bin/python /path/to/detect_bottlenecks.py";
    User = "nakamura-misaki";
  };
};
```

### detect_bottlenecks.py

```python
#!/usr/bin/env python3
"""ボトルネック検出スクリプト"""

import asyncio
from src.infrastructure.di import build_detect_bottleneck_use_case, build_slack_client

async def main():
    use_case = await build_detect_bottleneck_use_case()
    slack_client = build_slack_client()

    bottlenecks = await use_case.execute()

    if bottlenecks:
        # PM宛にDM送信（設定から取得）
        pm_user_id = settings.pm_user_id

        message = "⚠️ タスクボトルネック検出\n\n"
        for bottleneck in bottlenecks:
            message += f"- {bottleneck.message}\n"

        await slack_client.chat_postMessage(channel=pm_user_id, text=message)

    print(f"Detected {len(bottlenecks)} bottlenecks")

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_detect_bottleneck_use_case.py

@pytest.mark.asyncio
async def test_detect_task_concentration():
    """タスク集中検出"""
    # モックリポジトリ: ユーザーU01に5件タスクあり
    task_repository = MockTaskRepository()
    for _ in range(5):
        await task_repository.create(Task(
            title="Test",
            assignee_user_id="U01ABC123",
            creator_user_id="U01ABC123",
        ))

    use_case = DetectBottleneckUseCase(task_repository)
    bottlenecks = await use_case.execute()

    assert len(bottlenecks) == 1
    assert bottlenecks[0].type == "task_concentration"
    assert bottlenecks[0].user_id == "U01ABC123"
```

### Integration Tests

```python
# tests/integration/test_admin_ui.py

@pytest.mark.asyncio
async def test_admin_ui_team_tasks():
    """Admin UI: チーム全体タスク一覧"""
    from httpx import AsyncClient
    from src.infrastructure.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/team/tasks")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
```

## Deployment

### Environment Variables

```bash
# Admin UI
ADMIN_UI_PORT=3002

# Bottleneck Detection
PM_USER_ID=U01ABC123  # PM宛にボトルネック通知
```

### NixOS Configuration

```nix
# modules/services/registry/nakamura-misaki-admin.nix

systemd.services.nakamura-misaki-admin = {
  description = "nakamura-misaki Admin UI";
  after = [ "network.target" "postgresql.service" ];
  wantedBy = [ "multi-user.target" ];

  serviceConfig = {
    Type = "simple";
    ExecStart = "${pkgs.python3}/bin/uvicorn src.infrastructure.main:app --host 0.0.0.0 --port 3002";
    User = "nakamura-misaki";
    Restart = "always";
  };

  environment = {
    DATABASE_URL = config.sops.secrets."nakamura-misaki/database_url".path;
  };
};
```

## Monitoring

### Metrics

- **Admin UI**: リクエスト数、レスポンスタイム
- **Bottleneck Detection**: 検出数、通知送信成功率

### Logging

```python
logger.info("Bottleneck detected", extra={
    "type": bottleneck.type,
    "severity": bottleneck.severity,
    "user_id": bottleneck.user_id,
})
```
