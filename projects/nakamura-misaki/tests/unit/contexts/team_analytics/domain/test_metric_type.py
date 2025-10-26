"""Tests for MetricType Value Object"""

import pytest

from src.contexts.team_analytics.domain.value_objects.metric_type import MetricType


def test_metric_type_has_expected_values():
    """Test that MetricType has all expected values"""
    assert MetricType.TASKS_COMPLETED.value == "tasks_completed"
    assert MetricType.TASKS_PENDING.value == "tasks_pending"
    assert MetricType.COMPLETION_RATE.value == "completion_rate"
    assert MetricType.WORKLOAD.value == "workload"
    assert MetricType.BOTTLENECK.value == "bottleneck"


def test_metric_type_from_string_valid():
    """Test from_string with valid metric type"""
    metric_type = MetricType.from_string("tasks_completed")
    assert metric_type == MetricType.TASKS_COMPLETED


def test_metric_type_from_string_invalid():
    """Test from_string with invalid metric type raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        MetricType.from_string("invalid_metric")

    assert "Invalid metric type" in str(exc_info.value)
    assert "invalid_metric" in str(exc_info.value)
