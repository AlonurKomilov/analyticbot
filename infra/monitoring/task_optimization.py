"""
Celery Task Performance Optimizations
Enhanced task processing with monitoring and optimization features
"""

import functools
import time
from typing import Any

from celery import Celery, Task
from celery.signals import task_failure, task_postrun, task_prerun
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class PerformanceMetrics:
    """Track task performance metrics"""

    def __init__(self):
        self.metrics = {}

    def record_execution(self, task_name: str, duration: float, success: bool = True):
        """Record task execution metrics"""
        if task_name not in self.metrics:
            self.metrics[task_name] = {
                "total_executions": 0,
                "total_duration": 0.0,
                "success_count": 0,
                "failure_count": 0,
                "average_duration": 0.0,
                "min_duration": float("inf"),
                "max_duration": 0.0,
            }

        metrics = self.metrics[task_name]
        metrics["total_executions"] += 1
        metrics["total_duration"] += duration

        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1

        metrics["average_duration"] = metrics["total_duration"] / metrics["total_executions"]
        metrics["min_duration"] = min(metrics["min_duration"], duration)
        metrics["max_duration"] = max(metrics["max_duration"], duration)

    def get_metrics(self, task_name: str | None = None) -> dict:
        """Get performance metrics"""
        if task_name:
            return self.metrics.get(task_name, {})
        return self.metrics

    def reset_metrics(self, task_name: str | None = None):
        """Reset performance metrics"""
        if task_name and task_name in self.metrics:
            del self.metrics[task_name]
        else:
            self.metrics.clear()


# Global metrics instance
performance_metrics = PerformanceMetrics()


class OptimizedTask(Task):
    """Enhanced Celery task with performance optimizations"""

    def __init__(self):
        super().__init__()
        self.execution_history = []
        self.max_history = 100

    def __call__(self, *args, **kwargs):
        """Enhanced task execution with monitoring"""
        start_time = time.time()
        task_name = getattr(self, "name", "unknown_task")
        success = True

        try:
            logger.info(f"🚀 Starting task: {task_name}")
            result = super().__call__(*args, **kwargs)
            logger.info(f"✅ Task completed: {task_name}")
            return result
        except Exception as e:
            success = False
            logger.error(f"❌ Task failed: {task_name} - {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            performance_metrics.record_execution(task_name, duration, success)

            # Store execution history
            self.execution_history.append(
                {
                    "timestamp": start_time,
                    "duration": duration,
                    "success": success,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                }
            )

            # Limit history size
            if len(self.execution_history) > self.max_history:
                self.execution_history = self.execution_history[-self.max_history :]


def optimized_task(*args, **kwargs):
    """Decorator for creating optimized Celery tasks"""

    def decorator(func):
        # Set optimized task class
        kwargs["base"] = OptimizedTask

        # Configure task options for performance
        if "bind" not in kwargs:
            kwargs["bind"] = True

        # Add retry configuration if not present
        if "autoretry_for" not in kwargs:
            kwargs["autoretry_for"] = (Exception,)
        if "retry_kwargs" not in kwargs:
            kwargs["retry_kwargs"] = {"max_retries": 3, "countdown": 60}
        if "retry_backoff" not in kwargs:
            kwargs["retry_backoff"] = True

        return Celery.task(*args, **kwargs)(func)

    return decorator


def batch_task(batch_size: int = 100, max_wait_time: int = 30):
    """
    Decorator for batching task executions
    Collects multiple task calls and processes them together
    """

    def decorator(func):
        batch_queue = []
        last_execution = time.time()

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            nonlocal batch_queue, last_execution

            # Add to batch queue
            batch_queue.append((args, kwargs))
            current_time = time.time()

            # Process batch if conditions are met
            should_process = (
                len(batch_queue) >= batch_size or current_time - last_execution >= max_wait_time
            )

            if should_process:
                batch_to_process = batch_queue.copy()
                batch_queue.clear()
                last_execution = current_time

                logger.info(
                    f"📦 Processing batch of {len(batch_to_process)} items for {func.__name__}"
                )

                # Process batch
                results = []
                for batch_args, batch_kwargs in batch_to_process:
                    try:
                        result = func(self, *batch_args, **batch_kwargs)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing batch item: {e}")
                        results.append(None)

                return results

            return None  # Item added to queue, not processed yet

        return wrapper

    return decorator


def memory_efficient_task(chunk_size: int = 1000):
    """
    Decorator for memory-efficient task processing
    Processes large datasets in chunks to avoid memory issues
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, data: list[Any], *args, **kwargs):
            if not isinstance(data, list):
                return func(self, data, *args, **kwargs)

            total_items = len(data)
            results = []

            logger.info(f"🔄 Processing {total_items} items in chunks of {chunk_size}")

            for i in range(0, total_items, chunk_size):
                chunk = data[i : i + chunk_size]
                chunk_num = (i // chunk_size) + 1
                total_chunks = (total_items + chunk_size - 1) // chunk_size

                logger.info(f"Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} items)")

                try:
                    chunk_result = func(self, chunk, *args, **kwargs)
                    if isinstance(chunk_result, list):
                        results.extend(chunk_result)
                    else:
                        results.append(chunk_result)
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk_num}: {e}")
                    # Continue with next chunk instead of failing entire task
                    continue

            logger.info(f"✅ Completed processing {total_items} items, got {len(results)} results")
            return results

        return wrapper

    return decorator


def priority_task(priority: int = 5):
    """
    Decorator for setting task priority
    Higher numbers = higher priority
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set task priority in routing key
            kwargs.setdefault("priority", priority)
            return func.apply_async(*args, **kwargs)

        return wrapper

    return decorator


class TaskOptimizer:
    """Utility class for task optimization"""

    @staticmethod
    def get_performance_report() -> dict:
        """Generate comprehensive performance report"""
        metrics = performance_metrics.get_metrics()

        report = {"total_tasks": len(metrics), "summary": {}, "tasks": metrics}

        if metrics:
            total_executions = sum(m["total_executions"] for m in metrics.values())
            total_duration = sum(m["total_duration"] for m in metrics.values())
            total_failures = sum(m["failure_count"] for m in metrics.values())

            report["summary"] = {
                "total_executions": total_executions,
                "total_duration": total_duration,
                "average_duration": total_duration / total_executions
                if total_executions > 0
                else 0,
                "failure_rate": total_failures / total_executions if total_executions > 0 else 0,
                "most_used_task": max(metrics.keys(), key=lambda k: metrics[k]["total_executions"])
                if metrics
                else None,
                "slowest_task": max(metrics.keys(), key=lambda k: metrics[k]["average_duration"])
                if metrics
                else None,
            }

        return report

    @staticmethod
    def optimize_task_routing() -> dict[str, dict]:
        """Suggest optimal task routing based on performance"""
        metrics = performance_metrics.get_metrics()
        routing_suggestions = {}

        for task_name, task_metrics in metrics.items():
            avg_duration = task_metrics["average_duration"]
            failure_rate = task_metrics["failure_count"] / task_metrics["total_executions"]

            # Suggest routing based on performance characteristics
            if avg_duration > 60:  # Long-running tasks
                queue = "long_running"
                worker_concurrency = 2
            elif failure_rate > 0.1:  # High failure rate
                queue = "retry_queue"
                worker_concurrency = 4
            elif avg_duration < 1:  # Fast tasks
                queue = "fast_queue"
                worker_concurrency = 20
            else:  # Regular tasks
                queue = "default"
                worker_concurrency = 10

            routing_suggestions[task_name] = {
                "queue": queue,
                "worker_concurrency": worker_concurrency,
                "priority": 9 if failure_rate < 0.05 and avg_duration < 10 else 5,
            }

        return routing_suggestions

    @staticmethod
    def identify_bottlenecks() -> list[dict]:
        """Identify performance bottlenecks"""
        metrics = performance_metrics.get_metrics()
        bottlenecks = []

        for task_name, task_metrics in metrics.items():
            issues = []

            # Check average duration
            if task_metrics["average_duration"] > 30:
                issues.append(f"High average duration: {task_metrics['average_duration']:.2f}s")

            # Check failure rate
            failure_rate = task_metrics["failure_count"] / task_metrics["total_executions"]
            if failure_rate > 0.05:
                issues.append(f"High failure rate: {failure_rate:.2%}")

            # Check duration variance
            duration_variance = task_metrics["max_duration"] - task_metrics["min_duration"]
            if duration_variance > 60:
                issues.append(f"High duration variance: {duration_variance:.2f}s")

            if issues:
                bottlenecks.append(
                    {"task_name": task_name, "issues": issues, "metrics": task_metrics}
                )

        return sorted(bottlenecks, key=lambda x: len(x["issues"]), reverse=True)


# Signal handlers for automatic metrics collection
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task prerun signal"""
    task_name = getattr(task, "name", "unknown_task") if task else "unknown_task"
    logger.debug(f"📋 Task starting: {task_name} (ID: {task_id})")


@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds
):
    """Handle task postrun signal"""
    task_name = getattr(task, "name", "unknown_task") if task else "unknown_task"
    logger.debug(f"✅ Task completed: {task_name} (ID: {task_id}, State: {state})")


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds
):
    """Handle task failure signal"""
    task_name = getattr(sender, "name", "unknown_task") if sender else "unknown_task"
    logger.error(f"❌ Task failed: {task_name} (ID: {task_id}) - {exception}")


# Example optimized tasks
@optimized_task(name="analytics.process_channel_data")
@memory_efficient_task(chunk_size=500)
def process_channel_data_optimized(self, channel_data: list[dict]):
    """Optimized channel data processing task"""
    results = []

    for data in channel_data:
        try:
            # Process individual channel data
            processed = {
                "channel_id": data.get("channel_id"),
                "processed_at": time.time(),
                "status": "success",
            }
            results.append(processed)
        except Exception as e:
            logger.error(f"Error processing channel {data.get('channel_id')}: {e}")
            results.append(
                {"channel_id": data.get("channel_id"), "error": str(e), "status": "error"}
            )

    return results


@optimized_task(name="analytics.generate_reports")
@batch_task(batch_size=50, max_wait_time=60)
def generate_reports_optimized(self, report_requests: list[dict]):
    """Optimized report generation task with batching"""
    logger.info(f"Generating {len(report_requests)} reports")

    reports = []
    for request in report_requests:
        try:
            report = {
                "request_id": request.get("id"),
                "generated_at": time.time(),
                "status": "completed",
            }
            reports.append(report)
        except Exception as e:
            logger.error(f"Error generating report {request.get('id')}: {e}")

    return reports
