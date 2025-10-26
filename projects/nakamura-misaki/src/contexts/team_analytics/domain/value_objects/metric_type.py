"""Metric Type Value Object"""

from enum import Enum


class MetricType(Enum):
    """Types of team metrics"""

    TASKS_COMPLETED = "tasks_completed"
    TASKS_PENDING = "tasks_pending"
    COMPLETION_RATE = "completion_rate"
    WORKLOAD = "workload"
    BOTTLENECK = "bottleneck"

    @classmethod
    def from_string(cls, value: str) -> "MetricType":
        """Create MetricType from string value

        Args:
            value: String representation of metric type

        Returns:
            MetricType instance

        Raises:
            ValueError: If value is not a valid metric type
        """
        try:
            return cls(value)
        except ValueError as e:
            valid_types = ", ".join([t.value for t in cls])
            raise ValueError(f"Invalid metric type: {value}. Valid types are: {valid_types}") from e
