"""Tests for TeamMetric Entity"""

from datetime import date

import pytest

from src.contexts.team_analytics.domain.entities.team_metric import TeamMetric
from src.contexts.team_analytics.domain.value_objects.metric_type import MetricType


def test_create_team_metric_with_valid_data():
    """Test creating a team metric with valid data"""
    metric = TeamMetric.create(
        date=date(2025, 10, 26),
        metric_type=MetricType.TASKS_COMPLETED,
        metric_value=25.0,
        metadata={"team": "engineering"},
    )

    assert metric.date == date(2025, 10, 26)
    assert metric.metric_type == MetricType.TASKS_COMPLETED
    assert metric.metric_value == 25.0
    assert metric.metadata == {"team": "engineering"}
    assert metric.id is not None
    assert metric.created_at is not None


def test_create_team_metric_with_negative_tasks_completed_raises_error():
    """Test that creating metric with negative TASKS_COMPLETED raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        TeamMetric.create(
            date=date(2025, 10, 26),
            metric_type=MetricType.TASKS_COMPLETED,
            metric_value=-5.0,
        )

    assert "cannot be negative" in str(exc_info.value)


def test_create_team_metric_with_negative_tasks_pending_raises_error():
    """Test that creating metric with negative TASKS_PENDING raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        TeamMetric.create(
            date=date(2025, 10, 26),
            metric_type=MetricType.TASKS_PENDING,
            metric_value=-3.0,
        )

    assert "cannot be negative" in str(exc_info.value)


def test_create_team_metric_with_negative_workload_raises_error():
    """Test that creating metric with negative WORKLOAD raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        TeamMetric.create(
            date=date(2025, 10, 26),
            metric_type=MetricType.WORKLOAD,
            metric_value=-10.0,
        )

    assert "cannot be negative" in str(exc_info.value)


def test_create_team_metric_with_invalid_completion_rate_too_low_raises_error():
    """Test that creating metric with COMPLETION_RATE < 0.0 raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        TeamMetric.create(
            date=date(2025, 10, 26),
            metric_type=MetricType.COMPLETION_RATE,
            metric_value=-0.1,
        )

    assert "must be between 0.0 and 1.0" in str(exc_info.value)


def test_create_team_metric_with_invalid_completion_rate_too_high_raises_error():
    """Test that creating metric with COMPLETION_RATE > 1.0 raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        TeamMetric.create(
            date=date(2025, 10, 26),
            metric_type=MetricType.COMPLETION_RATE,
            metric_value=1.5,
        )

    assert "must be between 0.0 and 1.0" in str(exc_info.value)


def test_get_metadata_value_returns_value_when_key_exists():
    """Test that get_metadata_value returns value when key exists"""
    metric = TeamMetric.create(
        date=date(2025, 10, 26),
        metric_type=MetricType.BOTTLENECK,
        metric_value=1.0,
        metadata={"user_id": "U12345", "pending_tasks": 15},
    )

    assert metric.get_metadata_value("user_id") == "U12345"
    assert metric.get_metadata_value("pending_tasks") == 15


def test_get_metadata_value_returns_default_when_key_not_exists():
    """Test that get_metadata_value returns default when key does not exist"""
    metric = TeamMetric.create(
        date=date(2025, 10, 26),
        metric_type=MetricType.WORKLOAD,
        metric_value=50.0,
        metadata={"team": "engineering"},
    )

    assert metric.get_metadata_value("nonexistent", "default") == "default"
    assert metric.get_metadata_value("nonexistent") is None
