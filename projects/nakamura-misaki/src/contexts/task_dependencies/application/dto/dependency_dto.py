"""Dependency DTOs (Data Transfer Objects)"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateDependencyDTO:
    """DTO for creating a task dependency"""

    blocking_task_id: UUID
    blocked_task_id: UUID


@dataclass
class DependencyDTO:
    """DTO for dependency data"""

    id: UUID
    blocking_task_id: UUID
    blocked_task_id: UUID
    dependency_type: str
    created_at: datetime


@dataclass
class BlockerCheckDTO:
    """DTO for blocker check results"""

    task_id: UUID
    is_blocked: bool
    blocking_task_ids: list[UUID]
    blocking_task_count: int
    can_start: bool
    blocker_details: list[dict] | None = None  # Optional: タスク名などの詳細情報


@dataclass
class DependencyChainDTO:
    """DTO for dependency chain (全依存関係の視覚化用)"""

    task_id: UUID
    blocking_dependencies: list[DependencyDTO]  # このタスクをブロックしている依存関係
    blocked_dependencies: list[DependencyDTO]  # このタスクがブロックしている依存関係
    all_blocking_task_ids: list[UUID]  # 依存関係チェーン全体（再帰的）
