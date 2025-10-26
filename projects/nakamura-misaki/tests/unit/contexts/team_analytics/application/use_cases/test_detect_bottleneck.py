"""Tests for DetectBottleneckUseCase"""

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.team_analytics.application.use_cases.detect_bottleneck import (
    DetectBottleneckUseCase,
)
from src.contexts.team_analytics.domain.entities.daily_summary import DailySummary


@pytest.mark.asyncio
async def test_detect_bottleneck_found():
    """Test detecting bottleneck when users have high pending tasks"""
    # Arrange
    mock_repo = AsyncMock()
    summaries = [
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 26),
            user_id="U1",
            tasks_completed=5,
            tasks_pending=15,  # Above threshold (10)
            summary_text=None,
            created_at=date(2025, 10, 26),
        ),
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 26),
            user_id="U2",
            tasks_completed=8,
            tasks_pending=5,  # Below threshold
            summary_text=None,
            created_at=date(2025, 10, 26),
        ),
    ]
    mock_repo.find_by_date_range.return_value = summaries

    use_case = DetectBottleneckUseCase(mock_repo, workload_threshold=10)

    # Act
    result = await use_case.execute(date(2025, 10, 26))

    # Assert
    assert result.detected is True
    assert "U1" in result.bottleneck_users
    assert "U2" not in result.bottleneck_users
    assert "1 user(s)" in result.message


@pytest.mark.asyncio
async def test_detect_bottleneck_not_found():
    """Test detecting bottleneck when no users have high pending tasks"""
    # Arrange
    mock_repo = AsyncMock()
    summaries = [
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 26),
            user_id="U1",
            tasks_completed=5,
            tasks_pending=5,  # Below threshold
            summary_text=None,
            created_at=date(2025, 10, 26),
        ),
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 26),
            user_id="U2",
            tasks_completed=8,
            tasks_pending=3,  # Below threshold
            summary_text=None,
            created_at=date(2025, 10, 26),
        ),
    ]
    mock_repo.find_by_date_range.return_value = summaries

    use_case = DetectBottleneckUseCase(mock_repo, workload_threshold=10)

    # Act
    result = await use_case.execute(date(2025, 10, 26))

    # Assert
    assert result.detected is False
    assert len(result.bottleneck_users) == 0
    assert "No bottlenecks detected" in result.message
