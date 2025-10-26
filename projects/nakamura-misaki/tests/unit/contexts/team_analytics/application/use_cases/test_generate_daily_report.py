"""Tests for GenerateDailyReportUseCase"""

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.contexts.team_analytics.application.use_cases.generate_daily_report import (
    GenerateDailyReportUseCase,
)
from src.contexts.team_analytics.domain.entities.daily_summary import DailySummary


@pytest.mark.asyncio
async def test_generate_daily_report_creates_new_summary():
    """Test generating daily report creates new team summary"""
    # Arrange
    mock_repo = AsyncMock()
    user_summaries = [
        DailySummary.create(
            summary_date=date(2025, 10, 26),
            user_id="U1",
            tasks_completed=5,
            tasks_pending=3,
            summary_text=None,
        ),
        DailySummary.create(
            summary_date=date(2025, 10, 26),
            user_id="U2",
            tasks_completed=8,
            tasks_pending=2,
            summary_text=None,
        ),
    ]
    mock_repo.find_by_date_range.return_value = user_summaries
    mock_repo.find_team_summary_by_date.return_value = None  # No existing team summary

    use_case = GenerateDailyReportUseCase(mock_repo)

    # Act
    result = await use_case.execute(
        report_date=date(2025, 10, 26),
        summary_text="Daily team summary",
    )

    # Assert
    assert result.user_id is None  # Team-wide
    assert result.tasks_completed == 13  # 5 + 8
    assert result.tasks_pending == 5  # 3 + 2
    assert result.summary_text == "Daily team summary"
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_generate_daily_report_with_no_user_summaries():
    """Test generating daily report with no user summaries creates zero summary"""
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.find_by_date_range.return_value = []  # No user summaries
    mock_repo.find_team_summary_by_date.return_value = None

    use_case = GenerateDailyReportUseCase(mock_repo)

    # Act
    result = await use_case.execute(report_date=date(2025, 10, 26))

    # Assert
    assert result.tasks_completed == 0
    assert result.tasks_pending == 0
    mock_repo.save.assert_called_once()
