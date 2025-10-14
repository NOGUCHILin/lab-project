"""Bottleneck detection model"""

from dataclasses import dataclass
from enum import Enum


class BottleneckType(str, Enum):
    """ボトルネックタイプ"""

    TASK_CONCENTRATION = "task_concentration"
    OVERDUE_TASKS = "overdue_tasks"
    STALE_TASKS = "stale_tasks"


class Severity(str, Enum):
    """重要度"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Bottleneck:
    """ボトルネック"""

    type: BottleneckType
    severity: Severity
    description: str
    affected_user_id: str | None = None
    task_count: int = 0
