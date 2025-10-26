"""Tests for DailySummary Entity"""

from datetime import date

import pytest

from src.contexts.team_analytics.domain.entities.daily_summary import DailySummary


def test_create_daily_summary_with_valid_data():
    """Test creating a daily summary with valid data"""
    summary = DailySummary.create(
            
        summary_date=date(2025, 10, 26),
        user_id="U12345",
        tasks_completed=5,
        tasks_pending=3,
        summary_text="Good progress today",
    )

    assert summary.date == date(2025, 10, 26)
    assert summary.user_id == "U12345"
    assert summary.tasks_completed == 5
    assert summary.tasks_pending == 3
    assert summary.summary_text == "Good progress today"
    assert summary.id is not None
    assert summary.created_at is not None


def test_create_daily_summary_with_negative_completed_raises_error():
    """Test that creating summary with negative tasks_completed raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        DailySummary.create(
            
            summary_date=date(2025, 10, 26),
            user_id="U12345",
            tasks_completed=-1,
            tasks_pending=3,
        )

    assert "tasks_completed cannot be negative" in str(exc_info.value)


def test_create_daily_summary_with_negative_pending_raises_error():
    """Test that creating summary with negative tasks_pending raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        DailySummary.create(
            
            summary_date=date(2025, 10, 26),
            user_id="U12345",
            tasks_completed=5,
            tasks_pending=-1,
        )

    assert "tasks_pending cannot be negative" in str(exc_info.value)


def test_total_tasks_property():
    """Test that total_tasks property calculates correctly"""
    summary = DailySummary.create(
            
        summary_date=date(2025, 10, 26),
        user_id="U12345",
        tasks_completed=5,
        tasks_pending=3,
    )

    assert summary.total_tasks == 8


def test_completion_rate_property():
    """Test that completion_rate property calculates correctly"""
    summary = DailySummary.create(
            
        summary_date=date(2025, 10, 26),
        user_id="U12345",
        tasks_completed=6,
        tasks_pending=4,
    )

    assert summary.completion_rate == 0.6


def test_completion_rate_with_zero_tasks():
    """Test that completion_rate returns 0.0 when there are no tasks"""
    summary = DailySummary.create(
            
        summary_date=date(2025, 10, 26),
        user_id="U12345",
        tasks_completed=0,
        tasks_pending=0,
    )

    assert summary.completion_rate == 0.0


def test_is_team_summary_returns_true_for_none_user_id():
    """Test that is_team_summary returns True when user_id is None"""
    summary = DailySummary.create(
            
        summary_date=date(2025, 10, 26),
        user_id=None,  # Team-wide summary
        tasks_completed=50,
        tasks_pending=30,
    )

    assert summary.is_team_summary() is True


def test_is_team_summary_returns_false_for_user_id():
    """Test that is_team_summary returns False when user_id is provided"""
    summary = DailySummary.create(
            
        summary_date=date(2025, 10, 26),
        user_id="U12345",
        tasks_completed=5,
        tasks_pending=3,
    )

    assert summary.is_team_summary() is False
