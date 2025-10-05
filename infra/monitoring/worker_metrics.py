"""
Worker metrics enhancement for Celery workers.
This module extends the Prometheus metrics to track worker-specific metrics.
"""

import os
import time

import psutil
from celery import Celery
from prometheus_client import Counter, Gauge, Histogram

# TODO: Prometheus service should be injected via DI in clean architecture
# ARCHITECTURE FIX: No direct imports from apps layer in infra
from infra.logging.structlog_config import get_logger, performance_context

logger = get_logger(__name__)


class WorkerMetricsCollector:
    """Collects and reports Celery worker metrics to Prometheus."""

    def __init__(self, celery_app: Celery | None = None):
        self.celery_app = celery_app
        self._setup_worker_metrics()

    def _setup_worker_metrics(self):
        """Setup worker-specific metrics."""

        # Worker-specific metrics
        self.worker_memory_usage = Gauge(
            "celery_worker_memory_usage_bytes",
            "Memory usage by Celery worker in bytes",
            ["worker_name", "hostname"],
            # registry disabled for clean architecture
        )

        self.worker_cpu_usage = Gauge(
            "celery_worker_cpu_usage_percent",
            "CPU usage by Celery worker in percent",
            ["worker_name", "hostname"],
            # registry disabled for clean architecture
        )

        self.worker_tasks_active = Gauge(
            "celery_worker_tasks_active",
            "Number of active tasks per worker",
            ["worker_name", "hostname"],
            # registry disabled for clean architecture
        )

        self.worker_tasks_processed = Counter(
            "celery_worker_tasks_processed_total",
            "Total tasks processed by worker",
            ["worker_name", "hostname", "task_name", "status"],
            # registry disabled for clean architecture
        )

        self.worker_task_execution_time = Histogram(
            "celery_worker_task_execution_seconds",
            "Task execution time in seconds",
            ["worker_name", "hostname", "task_name"],
            # registry disabled for clean architecture
        )

        self.worker_heartbeat_timestamp = Gauge(
            "celery_worker_heartbeat_timestamp",
            "Last heartbeat timestamp from worker",
            ["worker_name", "hostname"],
            # registry disabled for clean architecture
        )

        self.worker_uptime_seconds = Gauge(
            "celery_worker_uptime_seconds",
            "Worker uptime in seconds",
            ["worker_name", "hostname"],
            # registry disabled for clean architecture
        )

        # Queue metrics
        self.queue_length = Gauge(
            "celery_queue_length",
            "Number of messages in queue",
            ["queue_name"],
            # registry disabled for clean architecture
        )

        self.queue_consumers = Gauge(
            "celery_queue_consumers",
            "Number of consumers for queue",
            ["queue_name"],
            # registry disabled for clean architecture
        )

        logger.info("Worker metrics initialized")

    async def collect_worker_stats(self) -> dict:
        """Collect comprehensive worker statistics."""

        with performance_context("collect_worker_stats", logger):
            stats = {
                "workers": {},
                "queues": {},
                "system": {},
                "timestamp": time.time(),
            }

            try:
                # Get Celery inspect instance
                if self.celery_app:
                    inspect = self.celery_app.control.inspect()

                    # Active workers
                    active_workers = inspect.active()
                    if active_workers:
                        for worker_name, tasks in active_workers.items():
                            stats["workers"][worker_name] = {
                                "active_tasks": len(tasks),
                                "task_names": [task["name"] for task in tasks],
                            }

                    # Worker stats (loads, memory, etc.)
                    worker_stats = inspect.stats()
                    if worker_stats:
                        for worker_name, worker_data in worker_stats.items():
                            if worker_name not in stats["workers"]:
                                stats["workers"][worker_name] = {}

                            stats["workers"][worker_name].update(
                                {
                                    "total_tasks": worker_data.get("total", {}),
                                    "pool": worker_data.get("pool", {}),
                                    "rusage": worker_data.get("rusage", {}),
                                }
                            )

                    # Queue lengths
                    try:
                        # This requires broker connection details
                        # Implementation would depend on broker type (Redis/RabbitMQ)
                        pass
                    except Exception as e:
                        logger.warning("Could not collect queue stats", error=str(e))

                # System metrics for current process
                current_process = psutil.Process()
                stats["system"] = {
                    "cpu_percent": current_process.cpu_percent(),
                    "memory_info": current_process.memory_info()._asdict(),
                    "memory_percent": current_process.memory_percent(),
                    "num_threads": current_process.num_threads(),
                    "create_time": current_process.create_time(),
                }

            except Exception as e:
                logger.error("Error collecting worker stats", error=str(e))

            return stats

    def update_worker_metrics(self, worker_stats: dict):
        """Update Prometheus metrics from worker statistics."""

        try:
            hostname = os.getenv("HOSTNAME", "localhost")
            current_time = time.time()

            # Update worker-specific metrics
            for worker_name, worker_data in worker_stats.get("workers", {}).items():
                # Active tasks
                active_tasks = worker_data.get("active_tasks", 0)
                self.worker_tasks_active.labels(worker_name=worker_name, hostname=hostname).set(
                    active_tasks
                )

                # Heartbeat
                self.worker_heartbeat_timestamp.labels(
                    worker_name=worker_name, hostname=hostname
                ).set(current_time)

                # Uptime (if we have create_time)
                rusage = worker_data.get("rusage", {})
                if "stime" in rusage:
                    # Calculate uptime from system time
                    uptime = current_time - worker_stats.get("timestamp", current_time)
                    self.worker_uptime_seconds.labels(
                        worker_name=worker_name, hostname=hostname
                    ).set(max(0, uptime))

            # Update system metrics for current process
            system_data = worker_stats.get("system", {})
            if system_data:
                worker_name = f"worker-{os.getpid()}"

                # Memory usage
                memory_info = system_data.get("memory_info", {})
                if "rss" in memory_info:
                    self.worker_memory_usage.labels(worker_name=worker_name, hostname=hostname).set(
                        memory_info["rss"]
                    )

                # CPU usage
                cpu_percent = system_data.get("cpu_percent", 0)
                self.worker_cpu_usage.labels(worker_name=worker_name, hostname=hostname).set(
                    cpu_percent
                )

                # Uptime
                create_time = system_data.get("create_time", current_time)
                uptime = current_time - create_time
                self.worker_uptime_seconds.labels(worker_name=worker_name, hostname=hostname).set(
                    uptime
                )

            logger.info("Worker metrics updated successfully")

        except Exception as e:
            logger.error("Error updating worker metrics", error=str(e))

    def record_task_execution(self, task_name: str, duration: float, status: str = "success"):
        """Record task execution metrics."""

        hostname = os.getenv("HOSTNAME", "localhost")
        worker_name = f"worker-{os.getpid()}"

        # Record execution time
        self.worker_task_execution_time.labels(
            worker_name=worker_name, hostname=hostname, task_name=task_name
        ).observe(duration)

        # Increment task counter
        self.worker_tasks_processed.labels(
            worker_name=worker_name,
            hostname=hostname,
            task_name=task_name,
            status=status,
        ).inc()


# Global worker metrics collector
worker_metrics = WorkerMetricsCollector()


def setup_worker_metrics(celery_app: Celery):
    """Setup worker metrics with Celery app instance."""
    global worker_metrics
    worker_metrics = WorkerMetricsCollector(celery_app)
    logger.info("Worker metrics configured with Celery app")


async def collect_and_update_worker_metrics():
    """Collect and update all worker metrics."""
    try:
        stats = await worker_metrics.collect_worker_stats()
        worker_metrics.update_worker_metrics(stats)
        return stats
    except Exception as e:
        logger.error("Failed to collect worker metrics", error=str(e))
        return {}


# Decorator for automatic task execution tracking
def track_task_execution(func):
    """Decorator to automatically track task execution metrics."""

    def wrapper(*args, **kwargs):
        task_name = getattr(func, "name", func.__name__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            worker_metrics.record_task_execution(task_name, duration, "success")
            return result
        except Exception:
            duration = time.time() - start_time
            worker_metrics.record_task_execution(task_name, duration, "failed")
            raise

    return wrapper
