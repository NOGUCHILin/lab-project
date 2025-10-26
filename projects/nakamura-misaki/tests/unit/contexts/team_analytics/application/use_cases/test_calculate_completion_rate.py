"""Tests for CalculateCompletionRateUseCase"""

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.team_analytics.application.use_cases.calculate_completion_rate import (
    CalculateCompletionRateUseCase,
)
from src.contexts.team_analytics.domain.entities.daily_summary import DailySummary


@pytest.mark.asyncio
async def test_calculate_completion_rate_with_data():
    """Test calculating completion rate with valid data"""
    # Arrange
    mock_repo = AsyncMock()
    summaries = [
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 24),
            user_id="U1",
            tasks_completed=5,
            tasks_pending=3,
            summary_text=None,
            created_at=date(2025, 10, 24),
        ),
        DailySummary(
            id=uuid4(),
            date=date(2025, 10, 25),
            user_id="U1",
            tasks_completed=3,
            tasks_pending=2,
            summary_text=None,
            created_at=date(2025, 10, 25),
        ),
    ]
    mock_repo.find_by_date_range.return_value = summaries

    use_case = CalculateCompletionRateUseCase(mock_repo)

    # Act
    result = await use_case.execute(
        start_date=date(2025, 10, 24),
        end_date=date(2025, 10, 25),
    )

    # Assert
    assert result.total_completed == 8  # 5 + 3
    assert result.total_pending == 5  # 3 + 2
    assert result.completion_rate == 8 / 13  # 8 / (8+5)
    assert len(result.daily_rates) == 2


@pytest.mark.asyncio
async def test_calculate_completion_rate_with_invalid_date_range():
    """Test that invalid date range raises ValueError"""
    # Arrange
    mock_repo = AsyncMock()
    use_case = CalculateCompletionRateUseCase(mock_repo)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute(
            start_date=date(2025, 10, 26),
            end_date=date(2025, 10, 24),  # Earlier than start_date
        )

    assert "start_date cannot be after end_date" in str(exc_info.value)


@pytest.mark.asyncio
async def test_calculate_completion_rate_with_no_data():
    """Test calculating completion rate with no data returns 0.0"""
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.find_by_date_range.return_value = []

    use_case = CalculateCompletionRateUseCase(mock_repo)

    # Act
    result = await use_case.execute(
        start_date=date(2025, 10, 24),
        end_date=date(2025, 10, 26),
    )

    # Assert
    assert result.total_completed == 0
    assert result.total_pending == 0
    assert result.completion_rate == 0.0
    assert len(result.daily_rates) == 0
