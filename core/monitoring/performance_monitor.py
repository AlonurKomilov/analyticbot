"""
Performance Monitoring Module

Tracks query performance, response times, and provides alerting
for recommendation system queries.
"""

import asyncio
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Collects and stores performance metrics"""

    def __init__(self):
        self.query_times: dict[str, list[float]] = defaultdict(list)
        self.query_counts: dict[str, int] = defaultdict(int)
        self.slow_queries: list[dict[str, Any]] = []
        self.error_counts: dict[str, int] = defaultdict(int)

        # Thresholds (in seconds)
        self.SLOW_QUERY_THRESHOLD = 3.0
        self.CRITICAL_THRESHOLD = 5.0

    def record_query(self, query_name: str, duration: float, success: bool = True):
        """Record a query execution"""
        self.query_times[query_name].append(duration)
        self.query_counts[query_name] += 1

        if not success:
            self.error_counts[query_name] += 1

        if duration > self.SLOW_QUERY_THRESHOLD:
            self.slow_queries.append(
                {
                    "query": query_name,
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat(),
                    "critical": duration > self.CRITICAL_THRESHOLD,
                }
            )

            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]

    def get_average_time(self, query_name: str) -> float:
        """Get average execution time for a query"""
        times = self.query_times.get(query_name, [])
        return sum(times) / len(times) if times else 0.0

    def get_p95_time(self, query_name: str) -> float:
        """Get 95th percentile execution time"""
        times = sorted(self.query_times.get(query_name, []))
        if not times:
            return 0.0

        index = int(len(times) * 0.95)
        return times[index] if index < len(times) else times[-1]

    def get_stats(self) -> dict[str, Any]:
        """Get all performance statistics"""
        stats = {}

        for query_name in self.query_counts:
            stats[query_name] = {
                "count": self.query_counts[query_name],
                "avg_time": round(self.get_average_time(query_name), 3),
                "p95_time": round(self.get_p95_time(query_name), 3),
                "errors": self.error_counts.get(query_name, 0),
                "error_rate": (
                    round(
                        self.error_counts.get(query_name, 0) / self.query_counts[query_name] * 100,
                        2,
                    )
                    if self.query_counts[query_name] > 0
                    else 0
                ),
            }

        return {
            "query_stats": stats,
            "slow_queries_count": len(self.slow_queries),
            "recent_slow_queries": self.slow_queries[-10:],  # Last 10
            "total_queries": sum(self.query_counts.values()),
            "total_errors": sum(self.error_counts.values()),
        }

    def clear(self):
        """Clear all metrics"""
        self.query_times.clear()
        self.query_counts.clear()
        self.slow_queries.clear()
        self.error_counts.clear()


# Global metrics instance
performance_metrics = PerformanceMetrics()


def monitor_performance(query_name: str):
    """Decorator to monitor function performance"""

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    logger.error(f"Error in {query_name}: {e}")
                    raise
                finally:
                    duration = time.time() - start_time
                    performance_metrics.record_query(query_name, duration, success)

                    if duration > performance_metrics.SLOW_QUERY_THRESHOLD:
                        logger.warning(f"Slow query detected: {query_name} took {duration:.2f}s")

                    if duration > performance_metrics.CRITICAL_THRESHOLD:
                        logger.error(
                            f"CRITICAL: {query_name} took {duration:.2f}s (threshold: {performance_metrics.CRITICAL_THRESHOLD}s)"
                        )

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    logger.error(f"Error in {query_name}: {e}")
                    raise
                finally:
                    duration = time.time() - start_time
                    performance_metrics.record_query(query_name, duration, success)

                    if duration > performance_metrics.SLOW_QUERY_THRESHOLD:
                        logger.warning(f"Slow query detected: {query_name} took {duration:.2f}s")

                    if duration > performance_metrics.CRITICAL_THRESHOLD:
                        logger.error(
                            f"CRITICAL: {query_name} took {duration:.2f}s (threshold: {performance_metrics.CRITICAL_THRESHOLD}s)"
                        )

            return sync_wrapper

    return decorator


class QueryPerformanceLogger:
    """Context manager for logging query performance"""

    def __init__(self, query_name: str, log_sql: bool = False):
        self.query_name = query_name
        self.log_sql = log_sql
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        if self.log_sql:
            logger.debug(f"Executing query: {self.query_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None

        performance_metrics.record_query(self.query_name, duration, success)

        if duration > performance_metrics.SLOW_QUERY_THRESHOLD:
            logger.warning(f"Slow query: {self.query_name} took {duration:.3f}s")

        if exc_type:
            logger.error(f"Query failed: {self.query_name} - {exc_val}")


def get_performance_report() -> str:
    """Generate a formatted performance report"""
    stats = performance_metrics.get_stats()

    report = []
    report.append("=" * 60)
    report.append("PERFORMANCE REPORT")
    report.append("=" * 60)
    report.append(f"Total Queries: {stats['total_queries']}")
    report.append(f"Total Errors: {stats['total_errors']}")
    report.append(f"Slow Queries: {stats['slow_queries_count']}")
    report.append("")

    report.append("Query Statistics:")
    report.append("-" * 60)

    for query_name, query_stats in stats["query_stats"].items():
        report.append(f"\n{query_name}:")
        report.append(f"  Count: {query_stats['count']}")
        report.append(f"  Avg Time: {query_stats['avg_time']}s")
        report.append(f"  P95 Time: {query_stats['p95_time']}s")
        report.append(f"  Errors: {query_stats['errors']} ({query_stats['error_rate']}%)")

    if stats["recent_slow_queries"]:
        report.append("\n" + "=" * 60)
        report.append("Recent Slow Queries:")
        report.append("-" * 60)
        for sq in stats["recent_slow_queries"]:
            critical_marker = " ⚠️ CRITICAL" if sq["critical"] else ""
            report.append(
                f"{sq['timestamp']} - {sq['query']}: {sq['duration']:.2f}s{critical_marker}"
            )

    report.append("=" * 60)

    return "\n".join(report)
