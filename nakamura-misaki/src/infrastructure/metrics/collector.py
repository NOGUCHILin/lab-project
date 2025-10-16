"""Metrics collector for monitoring application performance"""

import logging
from collections import defaultdict
from datetime import UTC, datetime
from threading import Lock

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple metrics collector for tracking API calls and performance"""

    def __init__(self):
        self._lock = Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._errors: dict[str, int] = defaultdict(int)
        self._last_reset = datetime.now(UTC)

    def increment(self, metric_name: str, value: int = 1) -> None:
        """Increment a counter metric

        Args:
            metric_name: Name of the metric
            value: Value to increment by (default: 1)
        """
        with self._lock:
            self._counters[metric_name] += value

    def record_time(self, metric_name: str, duration_ms: float) -> None:
        """Record a timing metric

        Args:
            metric_name: Name of the metric
            duration_ms: Duration in milliseconds
        """
        with self._lock:
            self._timers[metric_name].append(duration_ms)

    def record_error(self, error_type: str) -> None:
        """Record an error

        Args:
            error_type: Type of error
        """
        with self._lock:
            self._errors[error_type] += 1

    def get_metrics(self) -> dict:
        """Get current metrics snapshot

        Returns:
            Dictionary of metrics
        """
        with self._lock:
            metrics = {
                "timestamp": datetime.now(UTC).isoformat(),
                "uptime_seconds": (datetime.now(UTC) - self._last_reset).total_seconds(),
                "counters": dict(self._counters),
                "errors": dict(self._errors),
                "timings": {},
            }

            # Calculate timing statistics
            for name, durations in self._timers.items():
                if durations:
                    metrics["timings"][name] = {
                        "count": len(durations),
                        "min_ms": min(durations),
                        "max_ms": max(durations),
                        "avg_ms": sum(durations) / len(durations),
                        "p95_ms": self._percentile(durations, 95),
                        "p99_ms": self._percentile(durations, 99),
                    }

            return metrics

    def reset(self) -> None:
        """Reset all metrics"""
        with self._lock:
            self._counters.clear()
            self._timers.clear()
            self._errors.clear()
            self._last_reset = datetime.now(UTC)
        logger.info("Metrics reset")

    @staticmethod
    def _percentile(values: list[float], percentile: int) -> float:
        """Calculate percentile

        Args:
            values: List of values
            percentile: Percentile (0-100)

        Returns:
            Percentile value
        """
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global metrics collector instance
_metrics_collector: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector instance

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
