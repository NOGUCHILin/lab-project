"""Tests for GetTeamWorkloadUseCase"""

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.team_analytics.application.use_cases.get_team_workload import (
    GetTeamWorkloadUseCase,
)
from src.contexts.team_analytics.domain.entities.daily_summary import DailySummary


@pytest.mark.asyncio
async def test_get_team_workload_with_users():
    """Test getting team workload with user summaries"""
    # Arrange
    mock_repo = AsyncMock()
    summaries = [
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 26),
            user_id="U1",
            tasks_completed=5,
            tasks_pending=3,
            summary_text=None,
            created_at=date(2025, 10, 26),
        ),
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 26),
            user_id="U2",
            tasks_completed=8,
            tasks_pending=2,
            summary_text=None,
            created_at=date(2025, 10, 26),
        ),
    ]
    mock_repo.find_by_date_range.return_value = summaries

    use_case = GetTeamWorkloadUseCase(mock_repo)

    # Act
    result = await use_case.execute(workload_date=date(2025, 10, 26))

    # Assert
    assert result.total_tasks == 18  # (5+3) + (8+2)
    assert result.total_completed == 13  # 5 + 8
    assert result.total_pending == 5  # 3 + 2
    assert result.user_workloads == {"U1": 8, "U2": 10}
    assert result.average_workload == 9.0  # 18 / 2


@pytest.mark.asyncio
async def test_get_team_workload_with_no_users():
    """Test getting team workload with no user summaries returns zeros"""
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.find_by_date_range.return_value = []

    use_case = GetTeamWorkloadUseCase(mock_repo)

    # Act
    result = await use_case.execute(workload_date=date(2025, 10, 26))

    # Assert
    assert result.total_tasks == 0
    assert result.total_completed == 0
    assert result.total_pending == 0
    assert result.user_workloads == {}
    assert result.average_workload == 0.0
