"""Team Metric Entity"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from ..value_objects.metric_type import MetricType


@dataclass(frozen=True)
class TeamMetric:
    """Team-level metric measurement"""

    id: UUID
    date: date
    metric_type: MetricType
    metric_value: float
    metadata: dict[str, Any] | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        date: date,
        metric_type: MetricType,
        metric_value: float,
        metadata: dict[str, Any] | None = None,
    ) -> "TeamMetric":
        """Create a new team metric

        Args:
            date: Date of the metric
            metric_type: Type of metric
            metric_value: Numeric value of the metric
            metadata: Optional additional metadata

        Returns:
            TeamMetric instance

        Raises:
            ValueError: If metric_value is negative (for most metric types)
        """
        # Validate metric value based on type
        if metric_type in [MetricType.TASKS_COMPLETED, MetricType.TASKS_PENDING, MetricType.WORKLOAD]:
            if metric_value < 0:
                raise ValueError(f"{metric_type.value} cannot be negative")

        if metric_type == MetricType.COMPLETION_RATE:
            if not 0.0 <= metric_value <= 1.0:
                raise ValueError("completion_rate must be between 0.0 and 1.0")

        return cls(
            id=uuid4(),
            date=date,
            metric_type=metric_type,
            metric_value=metric_value,
            metadata=metadata or {},
            created_at=datetime.now(),
        )

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get value from metadata dictionary

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
