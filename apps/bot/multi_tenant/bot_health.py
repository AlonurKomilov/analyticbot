"""
Bot Health Monitoring System

Tracks health metrics for all user bots including:
- Success/failure rates
- Response times
- Error types
- Bot status (healthy, degraded, unhealthy)
- Rate limiting status
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar


class BotHealthStatus(Enum):
    """Health status for user bots"""

    HEALTHY = "healthy"  # Working normally
    DEGRADED = "degraded"  # High error rate but still working
    UNHEALTHY = "unhealthy"  # Not responding or failing constantly
    SUSPENDED = "suspended"  # Manually suspended by admin


@dataclass
class BotHealthMetrics:
    """Health metrics for a single user bot"""

    user_id: int
    status: BotHealthStatus = BotHealthStatus.HEALTHY

    # Request counters
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # Timestamps
    last_success: datetime | None = None
    last_failure: datetime | None = None
    last_check: datetime = field(default_factory=datetime.now)

    # Performance metrics
    error_rate: float = 0.0  # Percentage (0-1)
    avg_response_time_ms: float = 0.0
    consecutive_failures: int = 0

    # Status flags
    is_rate_limited: bool = False
    last_error_type: str | None = None


class BotHealthMonitor:
    """
    Singleton health monitor for all user bots

    Tracks metrics, detects issues, and provides health status.
    """

    _instance: ClassVar["BotHealthMonitor | None"] = None

    def __init__(self):
        """Private constructor - use get_instance() instead"""
        self.metrics: dict[int, BotHealthMetrics] = {}

        # Alert thresholds
        self.error_rate_warning = 0.2  # 20% error rate
        self.error_rate_critical = 0.5  # 50% error rate
        self.max_consecutive_failures = 5
        self.response_time_warning_ms = 1000  # 1 second
        self.response_time_critical_ms = 3000  # 3 seconds

    @classmethod
    def get_instance(cls) -> "BotHealthMonitor":
        """
        Get singleton instance

        Returns:
            Shared BotHealthMonitor instance
        """
        if cls._instance is None:
            cls._instance = cls()
            print("✅ Bot health monitor initialized")
        return cls._instance

    def record_success(
        self, user_id: int, response_time_ms: float, method: str = "unknown"
    ) -> None:
        """
        Record successful request

        Args:
            user_id: User ID of the bot
            response_time_ms: Request response time in milliseconds
            method: API method name
        """
        if user_id not in self.metrics:
            self.metrics[user_id] = BotHealthMetrics(user_id=user_id)

        metrics = self.metrics[user_id]
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.last_success = datetime.now()
        metrics.consecutive_failures = 0  # Reset failure count
        metrics.last_check = datetime.now()

        # Update average response time (exponential moving average)
        alpha = 0.3  # Weight for new value
        if metrics.avg_response_time_ms == 0:
            metrics.avg_response_time_ms = response_time_ms
        else:
            metrics.avg_response_time_ms = (
                alpha * response_time_ms + (1 - alpha) * metrics.avg_response_time_ms
            )

        # Recalculate error rate
        if metrics.total_requests > 0:
            metrics.error_rate = metrics.failed_requests / metrics.total_requests

        # Update status based on metrics
        self._update_status(user_id)

    def record_failure(self, user_id: int, error_type: str, method: str = "unknown") -> None:
        """
        Record failed request

        Args:
            user_id: User ID of the bot
            error_type: Type of error that occurred
            method: API method name
        """
        if user_id not in self.metrics:
            self.metrics[user_id] = BotHealthMetrics(user_id=user_id)

        metrics = self.metrics[user_id]
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.last_failure = datetime.now()
        metrics.consecutive_failures += 1
        metrics.last_error_type = error_type
        metrics.last_check = datetime.now()

        # Check if rate limited
        error_lower = error_type.lower()
        if any(x in error_lower for x in ["rate", "429", "too many requests"]):
            metrics.is_rate_limited = True

        # Recalculate error rate
        if metrics.total_requests > 0:
            metrics.error_rate = metrics.failed_requests / metrics.total_requests

        # Update status based on metrics
        self._update_status(user_id)

    def _update_status(self, user_id: int) -> None:
        """
        Update bot health status based on metrics

        Args:
            user_id: User ID of the bot
        """
        metrics = self.metrics[user_id]

        # Don't change if manually suspended
        if metrics.status == BotHealthStatus.SUSPENDED:
            return

        # Check consecutive failures
        if metrics.consecutive_failures >= self.max_consecutive_failures:
            metrics.status = BotHealthStatus.UNHEALTHY
            print(
                f"⚠️  Bot for user {user_id} marked UNHEALTHY: "
                f"{metrics.consecutive_failures} consecutive failures"
            )
            return

        # Check error rate
        if metrics.error_rate >= self.error_rate_critical:
            metrics.status = BotHealthStatus.UNHEALTHY
            print(
                f"⚠️  Bot for user {user_id} marked UNHEALTHY: "
                f"{metrics.error_rate * 100:.1f}% error rate"
            )
        elif metrics.error_rate >= self.error_rate_warning:
            metrics.status = BotHealthStatus.DEGRADED
            print(
                f"⚠️  Bot for user {user_id} marked DEGRADED: "
                f"{metrics.error_rate * 100:.1f}% error rate"
            )
        else:
            # Check response time
            if metrics.avg_response_time_ms >= self.response_time_critical_ms:
                metrics.status = BotHealthStatus.DEGRADED
            elif metrics.avg_response_time_ms >= self.response_time_warning_ms:
                if metrics.status == BotHealthStatus.UNHEALTHY:
                    metrics.status = BotHealthStatus.DEGRADED
            else:
                metrics.status = BotHealthStatus.HEALTHY

    def get_metrics(self, user_id: int) -> BotHealthMetrics | None:
        """
        Get metrics for specific bot

        Args:
            user_id: User ID of the bot

        Returns:
            BotHealthMetrics if found, None otherwise
        """
        return self.metrics.get(user_id)

    def get_all_metrics(self) -> dict[int, BotHealthMetrics]:
        """
        Get all bot metrics

        Returns:
            Dictionary of user_id -> BotHealthMetrics
        """
        return self.metrics.copy()

    def get_unhealthy_bots(self) -> list[int]:
        """
        Get list of unhealthy bot user IDs

        Returns:
            List of user IDs with degraded or unhealthy bots
        """
        return [
            user_id
            for user_id, metrics in self.metrics.items()
            if metrics.status in [BotHealthStatus.DEGRADED, BotHealthStatus.UNHEALTHY]
        ]

    def get_health_summary(self) -> dict[str, any]:
        """
        Get overall health summary

        Returns:
            Dictionary with health statistics
        """
        total_bots = len(self.metrics)
        if total_bots == 0:
            return {
                "total_bots": 0,
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "suspended": 0,
                "overall_health": "unknown",
            }

        status_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "suspended": 0,
        }

        total_requests = 0
        total_failures = 0
        total_response_time = 0.0
        active_bots = 0

        for metrics in self.metrics.values():
            status_counts[metrics.status.value] += 1
            total_requests += metrics.total_requests
            total_failures += metrics.failed_requests

            if metrics.total_requests > 0:
                active_bots += 1
                total_response_time += metrics.avg_response_time_ms

        # Calculate overall health
        healthy_percent = status_counts["healthy"] / total_bots
        if healthy_percent >= 0.9:
            overall_health = "excellent"
        elif healthy_percent >= 0.7:
            overall_health = "good"
        elif healthy_percent >= 0.5:
            overall_health = "fair"
        else:
            overall_health = "poor"

        return {
            "total_bots": total_bots,
            "active_bots": active_bots,
            "healthy": status_counts["healthy"],
            "degraded": status_counts["degraded"],
            "unhealthy": status_counts["unhealthy"],
            "suspended": status_counts["suspended"],
            "overall_health": overall_health,
            "total_requests": total_requests,
            "total_failures": total_failures,
            "global_error_rate": (total_failures / total_requests if total_requests > 0 else 0),
            "avg_response_time_ms": (total_response_time / active_bots if active_bots > 0 else 0),
        }

    def suspend_bot(self, user_id: int, reason: str = "Manual suspension") -> None:
        """
        Manually suspend a bot

        Args:
            user_id: User ID of the bot
            reason: Reason for suspension
        """
        if user_id not in self.metrics:
            self.metrics[user_id] = BotHealthMetrics(user_id=user_id)

        self.metrics[user_id].status = BotHealthStatus.SUSPENDED
        self.metrics[user_id].last_error_type = reason
        print(f"⏸️  Bot for user {user_id} suspended: {reason}")

    def resume_bot(self, user_id: int) -> None:
        """
        Resume a suspended bot

        Args:
            user_id: User ID of the bot
        """
        if user_id in self.metrics:
            self.metrics[user_id].status = BotHealthStatus.HEALTHY
            self.metrics[user_id].consecutive_failures = 0
            print(f"▶️  Bot for user {user_id} resumed")

    def reset_metrics(self, user_id: int) -> None:
        """
        Reset metrics for a bot

        Args:
            user_id: User ID of the bot
        """
        if user_id in self.metrics:
            del self.metrics[user_id]
            print(f"🔄 Metrics reset for user {user_id}")

    @classmethod
    def close(cls) -> None:
        """Close and reset the health monitor"""
        if cls._instance is not None:
            print("✅ Bot health monitor closed")
            cls._instance = None


# Convenience function
def get_health_monitor() -> BotHealthMonitor:
    """
    Get health monitor instance (convenience function)

    Returns:
        Shared BotHealthMonitor instance

    Example:
        monitor = get_health_monitor()
        monitor.record_success(user_id=123, response_time_ms=150)
    """
    return BotHealthMonitor.get_instance()
