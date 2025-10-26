"""Team Analytics DTOs"""

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID


@dataclass
class DailySummaryDTO:
    """DTO for daily summary"""

    id: UUID
    date: date
    user_id: str | None
    tasks_completed: int
    tasks_pending: int
    summary_text: str | None
    completion_rate: float


@dataclass
class TeamMetricDTO:
    """DTO for team metric"""

    id: UUID
    date: date
    metric_type: str
    metric_value: float
    metadata: dict[str, Any] | None


@dataclass
class BottleneckResultDTO:
    """DTO for bottleneck detection results"""

    detected: bool
    bottleneck_users: list[str]
    message: str
    workload_threshold: int


@dataclass
class TeamWorkloadDTO:
    """DTO for team workload information"""

    date: date
    total_tasks: int
    total_completed: int
    total_pending: int
    user_workloads: dict[str, int]
    average_workload: float


@dataclass
class UserStatisticsDTO:
    """DTO for user statistics"""

    user_id: str
    total_completed: int
    total_pending: int
    completion_rate: float
    daily_summaries: list[DailySummaryDTO]


@dataclass
class CompletionRateDTO:
    """DTO for completion rate calculation"""

    start_date: date
    end_date: date
    total_completed: int
    total_pending: int
    completion_rate: float
    daily_rates: list[tuple[date, float]]
