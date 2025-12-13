"""
Performance Analysis Service
============================

Focused microservice for system performance analysis and metrics collection.

Single Responsibility:
- System performance analysis
- Performance metrics collection
- Query performance analysis
- Resource utilization analysis
- Cache performance analysis

Core capabilities extracted from AutonomousOptimizationService performance analysis methods.
"""

import logging
from datetime import datetime
from typing import Any

from ..protocols.optimization_protocols import (
    PerformanceAnalysisProtocol,
    PerformanceBaseline,
)

logger = logging.getLogger(__name__)


class PerformanceAnalysisService(PerformanceAnalysisProtocol):
    """
    Performance analysis microservice for system metrics collection and analysis.

    Single responsibility: Performance analysis and metrics collection only.
    """

    def __init__(self, analytics_service=None, cache_service=None, config_manager=None):
        self.analytics_service = analytics_service
        self.cache_service = cache_service
        self.config_manager = config_manager

        # Performance thresholds configuration
        self.optimization_thresholds = {
            "query_time_ms": 1000,
            "memory_usage_percent": 80,
            "cpu_usage_percent": 75,
            "cache_hit_rate": 0.85,
            "error_rate_percent": 1.0,
            "disk_io_threshold": 100,  # MB/s
            "network_latency_ms": 200,
        }

        # Historical data retention
        self.metrics_history: dict[str, list[float]] = {}
        self.analysis_window_hours = 24

        logger.info("📊 Performance Analysis Service initialized - metrics collection focus")

    async def analyze_system_performance(self) -> dict[str, PerformanceBaseline]:
        """
        Comprehensive analysis of current system performance across all metrics.

        Main orchestration method for performance analysis.
        """
        try:
            logger.info("🔍 Starting comprehensive performance analysis")

            # Collect all performance metrics
            raw_metrics = await self.collect_performance_metrics()
            query_metrics = await self.analyze_query_performance()
            resource_metrics = await self.analyze_resource_utilization()
            cache_metrics = await self.analyze_cache_performance()

            # Combine all metrics
            combined_metrics = {
                **raw_metrics,
                **query_metrics,
                **resource_metrics,
                **cache_metrics,
            }

            # Create performance baselines
            baselines = {}

            # Query performance baselines
            if "avg_query_time" in combined_metrics:
                baselines["avg_query_time"] = PerformanceBaseline(
                    metric_name="avg_query_time",
                    current_value=combined_metrics["avg_query_time"],
                    historical_average=self._get_historical_average("avg_query_time"),
                    trend=self._calculate_trend("avg_query_time"),
                    threshold=self.optimization_thresholds["query_time_ms"],
                    is_concerning=combined_metrics["avg_query_time"]
                    > self.optimization_thresholds["query_time_ms"],
                )

            # CPU performance baseline
            if "cpu_usage" in combined_metrics:
                baselines["cpu_usage"] = PerformanceBaseline(
                    metric_name="cpu_usage",
                    current_value=combined_metrics["cpu_usage"],
                    historical_average=self._get_historical_average("cpu_usage"),
                    trend=self._calculate_trend("cpu_usage"),
                    threshold=self.optimization_thresholds["cpu_usage_percent"],
                    is_concerning=combined_metrics["cpu_usage"]
                    > self.optimization_thresholds["cpu_usage_percent"],
                )

            # Memory performance baseline
            if "memory_usage" in combined_metrics:
                baselines["memory_usage"] = PerformanceBaseline(
                    metric_name="memory_usage",
                    current_value=combined_metrics["memory_usage"],
                    historical_average=self._get_historical_average("memory_usage"),
                    trend=self._calculate_trend("memory_usage"),
                    threshold=self.optimization_thresholds["memory_usage_percent"],
                    is_concerning=combined_metrics["memory_usage"]
                    > self.optimization_thresholds["memory_usage_percent"],
                )

            # Cache performance baseline
            if "cache_hit_rate" in combined_metrics:
                baselines["cache_hit_rate"] = PerformanceBaseline(
                    metric_name="cache_hit_rate",
                    current_value=combined_metrics["cache_hit_rate"],
                    historical_average=self._get_historical_average("cache_hit_rate"),
                    trend=self._calculate_trend("cache_hit_rate"),
                    threshold=self.optimization_thresholds["cache_hit_rate"],
                    is_concerning=combined_metrics["cache_hit_rate"]
                    < self.optimization_thresholds["cache_hit_rate"],
                )

            # Error rate baseline
            if "error_rate" in combined_metrics:
                baselines["error_rate"] = PerformanceBaseline(
                    metric_name="error_rate",
                    current_value=combined_metrics["error_rate"],
                    historical_average=self._get_historical_average("error_rate"),
                    trend=self._calculate_trend("error_rate"),
                    threshold=self.optimization_thresholds["error_rate_percent"],
                    is_concerning=combined_metrics["error_rate"]
                    > self.optimization_thresholds["error_rate_percent"],
                )

            # Store metrics for historical analysis
            self._update_metrics_history(combined_metrics)

            logger.info(f"✅ Performance analysis completed - {len(baselines)} baselines created")
            logger.info(
                f"🚨 Concerning metrics: {sum(1 for b in baselines.values() if b.is_concerning)}"
            )

            return baselines

        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {e}")
            return {}

    async def collect_performance_metrics(self) -> dict[str, Any]:
        """
        Collect raw performance metrics from various system components.
        """
        try:
            logger.info("📋 Collecting raw performance metrics")

            metrics = {}

            # System-level metrics
            metrics.update(
                {
                    "timestamp": datetime.now().isoformat(),
                    "uptime_hours": 24.5,  # Mock data - replace with real metrics
                    "active_connections": 45,
                    "total_requests_last_hour": 1250,
                    "error_count_last_hour": 8,
                    "avg_response_time_ms": 245,
                }
            )

            # Database metrics (if analytics service available)
            if self.analytics_service:
                try:
                    db_metrics = await self._collect_database_metrics()
                    metrics.update(db_metrics)
                except Exception as e:
                    logger.warning(f"⚠️ Could not collect database metrics: {e}")
                    metrics["database_metrics_error"] = str(e)

            # Cache metrics (if cache service available)
            if self.cache_service:
                try:
                    cache_metrics = await self._collect_cache_metrics()
                    metrics.update(cache_metrics)
                except Exception as e:
                    logger.warning(f"⚠️ Could not collect cache metrics: {e}")
                    metrics["cache_metrics_error"] = str(e)

            # Calculate derived metrics
            if "error_count_last_hour" in metrics and "total_requests_last_hour" in metrics:
                metrics["error_rate"] = (
                    metrics["error_count_last_hour"] / max(metrics["total_requests_last_hour"], 1)
                ) * 100

            logger.info(f"✅ Collected {len(metrics)} performance metrics")
            return metrics

        except Exception as e:
            logger.error(f"❌ Metrics collection failed: {e}")
            return {"collection_error": str(e)}

    async def analyze_query_performance(self) -> dict[str, Any]:
        """
        Analyze query performance metrics and identify slow queries.
        """
        try:
            logger.info("🔍 Analyzing query performance")

            query_metrics = {}

            # Mock query analysis - replace with real analytics service calls
            if self.analytics_service:
                # Simulate query performance analysis
                query_metrics = {
                    "avg_query_time": 850,  # milliseconds
                    "max_query_time": 2500,
                    "slow_queries_count": 12,
                    "total_queries_analyzed": 450,
                    "queries_over_threshold": 8,
                    "most_expensive_queries": [
                        {
                            "query": "SELECT * FROM analytics_data WHERE...",
                            "avg_time_ms": 2100,
                        },
                        {"query": "JOIN heavy_table ON...", "avg_time_ms": 1850},
                        {
                            "query": "GROUP BY complex_aggregation...",
                            "avg_time_ms": 1650,
                        },
                    ],
                    "index_suggestions": [
                        {
                            "table": "analytics_data",
                            "column": "timestamp",
                            "impact": "high",
                        },
                        {
                            "table": "user_metrics",
                            "column": "channel_id",
                            "impact": "medium",
                        },
                    ],
                }
            else:
                query_metrics = {
                    "avg_query_time": 0,
                    "analysis_status": "analytics_service_unavailable",
                }

            logger.info("✅ Query performance analysis completed")
            return query_metrics

        except Exception as e:
            logger.error(f"❌ Query performance analysis failed: {e}")
            return {"query_analysis_error": str(e)}

    async def analyze_resource_utilization(self) -> dict[str, Any]:
        """
        Analyze CPU, memory, and other resource utilization patterns.
        """
        try:
            logger.info("🖥️ Analyzing resource utilization")

            # Mock resource analysis - replace with real system monitoring
            resource_metrics = {
                "cpu_usage": 72.5,  # percentage
                "memory_usage": 68.3,  # percentage
                "disk_usage": 45.7,  # percentage
                "disk_io_read_mb_s": 15.2,
                "disk_io_write_mb_s": 8.7,
                "network_in_mb_s": 5.4,
                "network_out_mb_s": 3.8,
                "network_latency_avg_ms": 145,
                "swap_usage": 2.1,  # percentage
                "load_average_1m": 1.85,
                "load_average_5m": 1.92,
                "load_average_15m": 2.05,
                "memory_available_gb": 12.8,
                "processes_count": 156,
                "threads_count": 892,
            }

            # Analyze resource trends
            resource_metrics["cpu_trend"] = self._calculate_trend("cpu_usage")
            resource_metrics["memory_trend"] = self._calculate_trend("memory_usage")
            resource_metrics["disk_trend"] = self._calculate_trend("disk_usage")

            # Resource health assessment
            resource_metrics["resource_health"] = {
                "cpu_healthy": resource_metrics["cpu_usage"]
                < self.optimization_thresholds["cpu_usage_percent"],
                "memory_healthy": resource_metrics["memory_usage"]
                < self.optimization_thresholds["memory_usage_percent"],
                "disk_healthy": resource_metrics["disk_usage"] < 90,
                "network_healthy": resource_metrics["network_latency_avg_ms"]
                < self.optimization_thresholds.get("network_latency_ms", 200),
            }

            logger.info("✅ Resource utilization analysis completed")
            return resource_metrics

        except Exception as e:
            logger.error(f"❌ Resource utilization analysis failed: {e}")
            return {"resource_analysis_error": str(e)}

    async def analyze_cache_performance(self) -> dict[str, Any]:
        """
        Analyze cache effectiveness and hit rates.
        """
        try:
            logger.info("💾 Analyzing cache performance")

            cache_metrics = {}

            if self.cache_service:
                # Simulate cache performance analysis
                cache_metrics = {
                    "cache_hit_rate": 0.82,  # 82%
                    "cache_miss_rate": 0.18,  # 18%
                    "cache_size_mb": 256,
                    "cache_max_size_mb": 512,
                    "cache_utilization": 0.5,  # 50%
                    "avg_cache_retrieval_time_ms": 2.5,
                    "cache_evictions_last_hour": 45,
                    "most_accessed_keys": [
                        {"key": "user_analytics:123", "hits": 250},
                        {"key": "channel_metrics:456", "hits": 189},
                        {"key": "performance_data:789", "hits": 167},
                    ],
                    "cache_efficiency_score": 0.85,
                }

                # Cache health assessment
                cache_metrics["cache_health"] = {
                    "hit_rate_healthy": cache_metrics["cache_hit_rate"]
                    >= self.optimization_thresholds["cache_hit_rate"],
                    "utilization_healthy": cache_metrics["cache_utilization"] < 0.9,
                    "retrieval_speed_healthy": cache_metrics["avg_cache_retrieval_time_ms"] < 10,
                    "eviction_rate_healthy": cache_metrics["cache_evictions_last_hour"] < 100,
                }
            else:
                cache_metrics = {
                    "cache_hit_rate": 0,
                    "analysis_status": "cache_service_unavailable",
                }

            logger.info("✅ Cache performance analysis completed")
            return cache_metrics

        except Exception as e:
            logger.error(f"❌ Cache performance analysis failed: {e}")
            return {"cache_analysis_error": str(e)}

    async def _collect_database_metrics(self) -> dict[str, Any]:
        """Collect database-specific performance metrics"""
        # Mock database metrics collection
        return {
            "db_connections_active": 25,
            "db_connections_max": 100,
            "db_query_count_last_hour": 1150,
            "db_avg_query_time_ms": 185,
            "db_slow_queries_count": 8,
            "db_deadlocks_count": 0,
            "db_table_scans_count": 45,
            "db_index_usage_efficiency": 0.88,
        }

    async def _collect_cache_metrics(self) -> dict[str, Any]:
        """Collect cache-specific performance metrics"""
        # Mock cache metrics collection
        return {
            "cache_operations_per_second": 145.7,
            "cache_memory_used_mb": 128.5,
            "cache_cpu_usage_percent": 12.3,
            "cache_network_io_mb_s": 8.9,
        }

    def _get_historical_average(self, metric_name: str) -> float:
        """Get historical average for a metric"""
        history = self.metrics_history.get(metric_name, [])
        return sum(history) / len(history) if history else 0.0

    def _calculate_trend(self, metric_name: str) -> str:
        """Calculate trend direction for a metric"""
        history = self.metrics_history.get(metric_name, [])

        if len(history) < 2:
            return "insufficient_data"

        recent_avg = sum(history[-5:]) / min(len(history), 5)
        older_avg = sum(history[:-5]) / max(len(history) - 5, 1) if len(history) > 5 else recent_avg

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _update_metrics_history(self, metrics: dict[str, Any]) -> None:
        """Update historical metrics data"""
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                if metric_name not in self.metrics_history:
                    self.metrics_history[metric_name] = []

                self.metrics_history[metric_name].append(value)

                # Keep only recent history (last 100 data points)
                if len(self.metrics_history[metric_name]) > 100:
                    self.metrics_history[metric_name] = self.metrics_history[metric_name][-100:]

    async def health_check(self) -> dict[str, Any]:
        """Health check for performance analysis service"""
        # Check service dependencies
        dependency_health = {
            "analytics_service": ("available" if self.analytics_service else "unavailable"),
            "cache_service": "available" if self.cache_service else "unavailable",
            "config_manager": "available" if self.config_manager else "unavailable",
        }

        return {
            "service_name": "PerformanceAnalysisService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "performance_analysis",
            "dependency_health": dependency_health,
            "capabilities": [
                "system_performance_analysis",
                "metrics_collection",
                "query_performance_analysis",
                "resource_utilization_analysis",
                "cache_performance_analysis",
                "historical_trend_analysis",
            ],
            "thresholds": self.optimization_thresholds,
            "metrics_history_size": len(self.metrics_history),
        }
