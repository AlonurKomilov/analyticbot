"""
🚀 Performance Monitoring Utilities

Advanced performance monitoring and optimization tools
for the AnalyticBot system.
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import wraps
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    load_average: float | None = None


class PerformanceMonitor:
    """
    🔍 Real-time Performance Monitor

    Tracks system performance metrics and provides optimization insights
    """

    def __init__(self, sampling_interval: int = 60):
        self.sampling_interval = sampling_interval
        self.metrics_history: list = []
        self.is_monitoring = False
        self.monitor_thread: threading.Thread | None = None
        self.optimization_suggestions: list = []

    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)

                # Keep only last 100 measurements
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)

                # Analyze and generate optimization suggestions
                self._analyze_performance()

            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")

            time.sleep(self.sampling_interval)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0

        # Network
        net_io = psutil.net_io_counters()
        net_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0
        net_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0

        # Active connections
        connections = len(psutil.net_connections())

        # Load average (Unix systems)
        load_avg = None
        try:
            load_avg = psutil.getloadavg()[0]
        except (OSError, AttributeError):
            pass  # Not available on Windows

        return PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=net_sent_mb,
            network_recv_mb=net_recv_mb,
            active_connections=connections,
            load_average=load_avg,
        )

    def _analyze_performance(self):
        """Analyze recent performance and generate optimization suggestions"""
        if len(self.metrics_history) < 5:
            return

        recent_metrics = self.metrics_history[-5:]
        self.optimization_suggestions.clear()

        # CPU Analysis
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        if avg_cpu > 80:
            self.optimization_suggestions.append(
                {
                    "type": "cpu_high",
                    "message": f"High CPU usage detected: {avg_cpu:.1f}%",
                    "recommendation": "Consider scaling up CPU resources or optimizing algorithms",
                }
            )

        # Memory Analysis
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        if avg_memory > 85:
            self.optimization_suggestions.append(
                {
                    "type": "memory_high",
                    "message": f"High memory usage detected: {avg_memory:.1f}%",
                    "recommendation": "Consider increasing memory or implementing memory optimization",
                }
            )

        # Connection Analysis
        avg_connections = sum(m.active_connections for m in recent_metrics) / len(recent_metrics)
        if avg_connections > 1000:
            self.optimization_suggestions.append(
                {
                    "type": "connections_high",
                    "message": f"High number of active connections: {avg_connections:.0f}",
                    "recommendation": "Consider connection pooling or rate limiting",
                }
            )

    def get_current_status(self) -> dict[str, Any]:
        """Get current performance status"""
        if not self.metrics_history:
            return {"status": "no_data", "message": "No performance data collected yet"}

        latest = self.metrics_history[-1]

        # Determine overall status
        status = "optimal"
        if latest.cpu_percent > 80 or latest.memory_percent > 85:
            status = "warning"
        if latest.cpu_percent > 95 or latest.memory_percent > 95:
            status = "critical"

        return {
            "status": status,
            "timestamp": latest.timestamp,
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "memory_mb": latest.memory_mb,
            "active_connections": latest.active_connections,
            "optimization_suggestions": self.optimization_suggestions,
        }

    def get_metrics_history(self, limit: int = 50) -> list:
        """Get historical metrics data"""
        return [asdict(m) for m in self.metrics_history[-limit:]]


# Performance decorator
def performance_monitor(func_name: str | None = None):
    """
    Decorator to monitor function performance

    Usage:
    @performance_monitor("critical_function")
    def my_function():
        pass
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            psutil.Process().cpu_percent()

            try:
                result = func(*args, **kwargs)
                status = "success"
                error = None
            except Exception as e:
                result = None
                status = "error"
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                end_cpu = psutil.Process().cpu_percent()

                # Log performance metrics
                logger.info(
                    f"PERF: {func_name or func.__name__} - "
                    f"Duration: {duration:.3f}s, "
                    f"CPU: {end_cpu:.1f}%, "
                    f"Status: {status}" + (f", Error: {error}" if error else "")
                )

            return result

        return wrapper

    return decorator


# Global performance monitor instance
performance_monitor_instance = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor_instance
