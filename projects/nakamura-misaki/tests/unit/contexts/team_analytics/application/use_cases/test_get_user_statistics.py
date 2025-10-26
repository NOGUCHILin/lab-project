"""Tests for GetUserStatisticsUseCase"""

from datetime import date, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.team_analytics.application.use_cases.get_user_statistics import (
    GetUserStatisticsUseCase,
)
from src.contexts.team_analytics.domain.entities.daily_summary import DailySummary


@pytest.mark.asyncio
async def test_get_user_statistics_with_data():
    """Test getting user statistics with data"""
    # Arrange
    mock_repo = AsyncMock()
    today = date.today()
    summaries = [
        DailySummary(
            id=uuid4(),
            date=today - timedelta(days=1),
            user_id="U1",
            tasks_completed=5,
            tasks_pending=3,
            summary_text=None,
            created_at=today - timedelta(days=1),
        ),
        DailySummary(
            id=uuid4(),
            date=today,
            user_id="U1",
            tasks_completed=3,
            tasks_pending=2,
            summary_text=None,
            created_at=today,
        ),
    ]
    mock_repo.find_by_date_range.return_value = summaries

    use_case = GetUserStatisticsUseCase(mock_repo)

    # Act
    result = await use_case.execute(user_id="U1", days=30)

    # Assert
    assert result.user_id == "U1"
    assert result.total_completed == 8  # 5 + 3
    assert result.total_pending == 5  # 3 + 2
    assert result.completion_rate == 8 / 13  # 8 / (8+5)
    assert len(result.daily_summaries) == 2


@pytest.mark.asyncio
async def test_get_user_statistics_with_invalid_days():
    """Test that invalid days parameter raises ValueError"""
    # Arrange
    mock_repo = AsyncMock()
    use_case = GetUserStatisticsUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(user_id="U1", days=0)

    assert "days must be positive" in str(exc_info.value)
