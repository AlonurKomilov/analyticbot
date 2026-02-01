"""
Performance monitoring middleware for tracking request metrics.
"""

import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Centralized performance metrics storage."""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history

        # Request metrics
        self.request_times = deque(maxlen=max_history)
        self.endpoint_stats = defaultdict(
            lambda: {
                "count": 0,
                "total_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "errors": 0,
                "recent_times": deque(maxlen=100),
            }
        )

        # Database query metrics
        self.db_query_times = deque(maxlen=max_history)
        self.slow_queries = deque(maxlen=100)

        # Cache metrics
        self.cache_hits = 0
        self.cache_misses = 0

        # Start time
        self.start_time = datetime.now()

    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record a request's performance metrics."""
        key = f"{method} {endpoint}"
        stats = self.endpoint_stats[key]

        stats["count"] += 1
        stats["total_time"] += duration
        stats["min_time"] = min(stats["min_time"], duration)
        stats["max_time"] = max(stats["max_time"], duration)
        stats["recent_times"].append(duration)

        if status_code >= 400:
            stats["errors"] += 1

        self.request_times.append(
            {
                "endpoint": endpoint,
                "method": method,
                "duration": duration,
                "status_code": status_code,
                "timestamp": datetime.now(),
            }
        )

    def record_db_query(self, query: str, duration: float):
        """Record database query performance."""
        self.db_query_times.append(
            {
                "query": query[:200],  # Truncate long queries
                "duration": duration,
                "timestamp": datetime.now(),
            }
        )

        # Track slow queries (>100ms)
        if duration > 0.1:
            self.slow_queries.append(
                {
                    "query": query[:500],
                    "duration": duration,
                    "timestamp": datetime.now(),
                }
            )

    def record_cache_hit(self):
        """Record cache hit."""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record cache miss."""
        self.cache_misses += 1

    def get_summary(self) -> dict:
        """Get performance summary."""
        now = datetime.now()
        uptime = now - self.start_time

        # Calculate overall stats
        recent_requests = [
            r for r in self.request_times if now - r["timestamp"] < timedelta(minutes=5)
        ]

        avg_response_time = (
            sum(r["duration"] for r in recent_requests) / len(recent_requests)
            if recent_requests
            else 0
        )

        # Requests per minute
        requests_per_minute = len(
            [r for r in self.request_times if now - r["timestamp"] < timedelta(minutes=1)]
        )

        # Error rate
        recent_errors = sum(1 for r in recent_requests if r["status_code"] >= 400)
        error_rate = (recent_errors / len(recent_requests) * 100) if recent_requests else 0

        # Top slow endpoints
        slow_endpoints = sorted(
            [(endpoint, stats) for endpoint, stats in self.endpoint_stats.items()],
            key=lambda x: x[1]["max_time"],
            reverse=True,
        )[:10]

        # Cache performance
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (
            (self.cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
        )

        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "total_requests": sum(stats["count"] for stats in self.endpoint_stats.values()),
            "requests_per_minute": requests_per_minute,
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "error_rate_percent": round(error_rate, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "slow_endpoints": [
                {
                    "endpoint": endpoint,
                    "count": stats["count"],
                    "avg_time_ms": round((stats["total_time"] / stats["count"]) * 1000, 2),
                    "max_time_ms": round(stats["max_time"] * 1000, 2),
                    "min_time_ms": round(stats["min_time"] * 1000, 2),
                    "errors": stats["errors"],
                }
                for endpoint, stats in slow_endpoints
            ],
            "slow_queries": [
                {
                    "query": q["query"],
                    "duration_ms": round(q["duration"] * 1000, 2),
                    "timestamp": q["timestamp"].isoformat(),
                }
                for q in list(self.slow_queries)[-10:]
            ],
            "recent_db_query_avg_ms": round(
                (
                    (
                        sum(q["duration"] for q in list(self.db_query_times)[-100:])
                        / min(100, len(self.db_query_times))
                        * 1000
                    )
                    if self.db_query_times
                    else 0
                ),
                2,
            ),
        }


# Global metrics instance
performance_metrics = PerformanceMetrics()


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor request performance."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request performance."""
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            performance_metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                duration=duration,
                status_code=response.status_code,
            )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.4f}"

            # Log slow requests (>1s)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} took {duration:.2f}s"
                )

            return response

        except Exception:
            duration = time.time() - start_time

            # Record error
            performance_metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                duration=duration,
                status_code=500,
            )

            raise


def get_performance_metrics() -> dict:
    """Get current performance metrics."""
    return performance_metrics.get_summary()
