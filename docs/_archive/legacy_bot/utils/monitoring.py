"""
Monitoring utilities for application health and performance tracking.
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Container for metric data points"""

    timestamp: datetime
    value: float
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Performance statistics container"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests * 100

    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests * 100

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests


class MetricsCollector:
    """Centralized metrics collection and monitoring"""

    def __init__(self, max_metrics_age_hours: int = 24):
        self._metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._performance_stats: dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self._max_age = timedelta(hours=max_metrics_age_hours)
        self._lock = threading.RLock()
        self._start_time = datetime.now()

    def record_metric(self, name: str, value: float, labels: dict[str, str] | None = None):
        """Record a metric value"""
        with self._lock:
            metric_data = MetricData(timestamp=datetime.now(), value=value, labels=labels or {})
            self._metrics[name].append(metric_data)

    def record_request(self, endpoint: str, success: bool, response_time: float):
        """Record request performance data"""
        with self._lock:
            stats = self._performance_stats[endpoint]
            stats.total_requests += 1
            if success:
                stats.successful_requests += 1
                stats.total_response_time += response_time
                stats.min_response_time = min(stats.min_response_time, response_time)
                stats.max_response_time = max(stats.max_response_time, response_time)
            else:
                stats.failed_requests += 1

    def get_metric_values(self, name: str, since: datetime | None = None) -> list[MetricData]:
        """Get metric values, optionally filtered by time"""
        with self._lock:
            if name not in self._metrics:
                return []
            metrics = list(self._metrics[name])
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]
            return metrics

    def get_performance_stats(self, endpoint: str | None = None) -> dict[str, PerformanceStats]:
        """Get performance statistics"""
        with self._lock:
            if endpoint:
                return {endpoint: self._performance_stats.get(endpoint, PerformanceStats())}
            return dict(self._performance_stats)

    def get_summary(self) -> dict[str, Any]:
        """Get overall system metrics summary"""
        with self._lock:
            now = datetime.now()
            uptime = now - self._start_time
            total_requests = sum(stats.total_requests for stats in self._performance_stats.values())
            total_errors = sum(stats.failed_requests for stats in self._performance_stats.values())
            return {
                "uptime_seconds": uptime.total_seconds(),
                "total_requests": total_requests,
                "total_errors": total_errors,
                "overall_error_rate": (
                    total_errors / total_requests * 100 if total_requests > 0 else 0
                ),
                "endpoints": len(self._performance_stats),
                "metrics_count": sum(len(metrics) for metrics in self._metrics.values()),
                "timestamp": now.isoformat(),
            }

    def cleanup_old_metrics(self):
        """Remove old metrics to prevent memory leaks"""
        cutoff_time = datetime.now() - self._max_age
        with self._lock:
            for _metric_name, metrics in self._metrics.items():
                while metrics and metrics[0].timestamp < cutoff_time:
                    metrics.popleft()


metrics = MetricsCollector()


def record_performance(func_name: str):
    """Decorator to record function performance metrics"""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    logger.error(f"Error in {func_name}: {e}")
                    raise
                finally:
                    response_time = time.time() - start_time
                    metrics.record_request(func_name, success, response_time)

            return async_wrapper
        else:

            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    logger.error(f"Error in {func_name}: {e}")
                    raise
                finally:
                    response_time = time.time() - start_time
                    metrics.record_request(func_name, success, response_time)

            return sync_wrapper

    return decorator


class HealthMonitor:
    """System health monitoring"""

    def __init__(self):
        self._checks: dict[str, Any] = {}
        self._last_check_time: datetime | None = None
        self._check_interval = timedelta(minutes=5)

    def register_check(self, name: str, check_func, timeout: int = 10):
        """Register a health check function"""
        self._checks[name] = {
            "function": check_func,
            "timeout": timeout,
            "last_result": None,
            "last_check": None,
        }

    async def run_health_checks(self) -> dict[str, Any]:
        """Run all registered health checks"""
        results = {
            "overall_status": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat(),
        }
        unhealthy_count = 0
        for name, check_config in self._checks.items():
            try:
                check_func = check_config["function"]
                timeout = check_config["timeout"]
                if asyncio.iscoroutinefunction(check_func):
                    result = await asyncio.wait_for(check_func(), timeout=timeout)
                else:
                    result = await asyncio.get_event_loop().run_in_executor(None, check_func)
                results["checks"][name] = {
                    "status": "healthy",
                    "result": result,
                    "response_time": timeout,
                }
                check_config["last_result"] = result
                check_config["last_check"] = datetime.now()
            except TimeoutError:
                unhealthy_count += 1
                results["checks"][name] = {
                    "status": "timeout",
                    "error": f"Health check timed out after {timeout}s",
                }
            except Exception as e:
                unhealthy_count += 1
                results["checks"][name] = {"status": "unhealthy", "error": str(e)}
                logger.error(f"Health check '{name}' failed: {e}")
        if unhealthy_count > 0:
            if unhealthy_count == len(self._checks):
                results["overall_status"] = "unhealthy"
            else:
                results["overall_status"] = "degraded"
        self._last_check_time = datetime.now()
        return results


health_monitor = HealthMonitor()


def setup_default_health_checks():
    """Setup default health checks for common components"""

    async def check_database():
        """Check database connectivity"""
        try:
            from apps.bot.database.db import is_db_healthy

            return await is_db_healthy()
        except Exception as e:
            raise Exception(f"Database check failed: {e}")

    def check_memory_usage():
        """Check memory usage (if psutil available)"""
        try:
            import psutil

            memory = psutil.virtual_memory()
            if memory.percent > 90:
                raise Exception(f"High memory usage: {memory.percent}%")
            return {"memory_percent": memory.percent}
        except ImportError:
            return {"message": "Memory monitoring not available (psutil required)"}

    health_monitor.register_check("database", check_database)
    health_monitor.register_check("memory", check_memory_usage)


setup_default_health_checks()
