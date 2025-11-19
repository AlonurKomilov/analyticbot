"""
Process Lifecycle Manager

Provides comprehensive process management capabilities:
- Max runtime enforcement with graceful shutdown
- Signal handling (SIGTERM, SIGINT)
- Health monitoring and metrics
- Resource usage tracking (CPU, memory)
- Auto-restart on resource limit violations
- Graceful cleanup on exit

Usage:
    from apps.shared.process_manager import ProcessManager

    manager = ProcessManager(
        name="mtproto_worker",
        max_runtime_hours=24,
        memory_limit_mb=2048,
        cpu_limit_percent=80
    )

    # Start monitoring
    manager.start()

    # Check if should continue running
    while manager.should_continue():
        # Do work
        await asyncio.sleep(60)
        manager.heartbeat()  # Update activity

    # Clean exit
    manager.shutdown()
"""

import asyncio
import logging
import os
import signal
import time
from collections.abc import Callable
from dataclasses import dataclass

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ProcessMetrics:
    """Process health metrics."""

    pid: int
    name: str
    uptime_seconds: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    num_threads: int
    status: str
    heartbeat_age_seconds: float


class ProcessManager:
    """
    Manages process lifecycle with health monitoring and graceful shutdown.

    Features:
    - Enforces max runtime limits
    - Handles shutdown signals (SIGTERM, SIGINT)
    - Tracks resource usage (CPU, memory)
    - Auto-shutdown on resource limit violations
    - Health check HTTP endpoint support
    - Graceful cleanup callbacks
    """

    def __init__(
        self,
        name: str,
        max_runtime_hours: float | None = None,
        memory_limit_mb: int | None = None,
        cpu_limit_percent: float | None = None,
        heartbeat_timeout_seconds: int = 300,
        grace_period_seconds: int = 30,
    ):
        """
        Initialize process manager.

        Args:
            name: Process name for logging/identification
            max_runtime_hours: Maximum hours to run (None = infinite)
            memory_limit_mb: Memory limit in MB (None = no limit)
            cpu_limit_percent: Average CPU limit % (None = no limit)
            heartbeat_timeout_seconds: Seconds without heartbeat before considering unhealthy
            grace_period_seconds: Seconds to wait for graceful shutdown
        """
        self.name = name
        self.max_runtime_hours = max_runtime_hours
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit_percent = cpu_limit_percent
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self.grace_period_seconds = grace_period_seconds

        # Runtime tracking
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.last_heartbeat: float | None = None
        self.running = False
        self.shutdown_requested = False
        self.shutdown_reason: str | None = None

        # Process info
        self.pid = os.getpid()
        self.process = psutil.Process(self.pid)

        # CPU tracking (need samples over time)
        self.cpu_samples: list[float] = []
        self.max_cpu_samples = 10  # Track last 10 samples

        # Cleanup callbacks
        self.cleanup_callbacks: list[Callable] = []

        # Signal handlers
        self._original_sigterm = None
        self._original_sigint = None

    def start(self):
        """Start the process manager and install signal handlers."""
        if self.running:
            logger.warning(f"ProcessManager '{self.name}' already started")
            return

        self.start_time = time.time()
        self.last_heartbeat = time.time()
        self.running = True
        self.shutdown_requested = False
        self.shutdown_reason = None

        # Install signal handlers
        self._install_signal_handlers()

        logger.info(
            f"✅ ProcessManager '{self.name}' started (PID: {self.pid})\n"
            f"   Max runtime: {self.max_runtime_hours}h\n"
            f"   Memory limit: {self.memory_limit_mb}MB\n"
            f"   CPU limit: {self.cpu_limit_percent}%"
        )

    def _install_signal_handlers(self):
        """Install signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            logger.info(f"🛑 Received signal {signal_name} ({signum})")
            self.request_shutdown(f"signal_{signal_name}")

        # Save original handlers
        self._original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
        self._original_sigint = signal.signal(signal.SIGINT, signal_handler)

        logger.debug(f"Installed signal handlers for {self.name}")

    def _restore_signal_handlers(self):
        """Restore original signal handlers."""
        if self._original_sigterm:
            signal.signal(signal.SIGTERM, self._original_sigterm)
        if self._original_sigint:
            signal.signal(signal.SIGINT, self._original_sigint)

    def heartbeat(self):
        """Update heartbeat timestamp to indicate process is alive."""
        self.last_heartbeat = time.time()

    def should_continue(self) -> bool:
        """
        Check if process should continue running.

        Returns:
            True if should continue, False if should shutdown
        """
        if not self.running:
            return False

        if self.shutdown_requested:
            return False

        # Check max runtime
        if self.max_runtime_hours and self.start_time:
            elapsed_hours = (time.time() - self.start_time) / 3600
            if elapsed_hours >= self.max_runtime_hours:
                self.request_shutdown(f"max_runtime_reached_{elapsed_hours:.1f}h")
                return False

        # Check memory limit
        if self.memory_limit_mb:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                if memory_mb > self.memory_limit_mb:
                    self.request_shutdown(f"memory_limit_exceeded_{memory_mb:.0f}MB")
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Check CPU limit (average over samples)
        if self.cpu_limit_percent:
            try:
                cpu = self.process.cpu_percent(interval=1.0)
                self.cpu_samples.append(cpu)

                # Keep only recent samples
                if len(self.cpu_samples) > self.max_cpu_samples:
                    self.cpu_samples.pop(0)

                # Check average
                if len(self.cpu_samples) >= self.max_cpu_samples:
                    avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
                    if avg_cpu > self.cpu_limit_percent:
                        self.request_shutdown(f"cpu_limit_exceeded_{avg_cpu:.1f}%")
                        return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return True

    def request_shutdown(self, reason: str):
        """
        Request graceful shutdown.

        Args:
            reason: Reason for shutdown (for logging)
        """
        if self.shutdown_requested:
            return

        self.shutdown_requested = True
        self.shutdown_reason = reason
        logger.info(f"🛑 Shutdown requested for '{self.name}': {reason}")

    def shutdown(self):
        """Perform graceful shutdown with cleanup."""
        if not self.running:
            return

        logger.info(f"🔄 Shutting down '{self.name}'...")

        # Execute cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                logger.debug(f"Executing cleanup callback: {callback.__name__}")
                if asyncio.iscoroutinefunction(callback):
                    # Run async cleanup
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(callback())
                    else:
                        asyncio.run(callback())
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback {callback.__name__}: {e}")

        # Mark as stopped
        self.running = False
        self.end_time = time.time()

        # Restore signal handlers
        self._restore_signal_handlers()

        # Log final stats
        if self.start_time and self.end_time:
            uptime = self.end_time - self.start_time
            logger.info(
                f"✅ '{self.name}' shutdown complete\n"
                f"   Reason: {self.shutdown_reason or 'normal'}\n"
                f"   Uptime: {uptime/3600:.2f}h\n"
                f"   PID: {self.pid}"
            )

    def add_cleanup_callback(self, callback: Callable):
        """
        Add a cleanup callback to execute on shutdown.

        Args:
            callback: Sync or async function to call during shutdown
        """
        self.cleanup_callbacks.append(callback)
        logger.debug(f"Added cleanup callback: {callback.__name__}")

    def get_metrics(self) -> ProcessMetrics:
        """
        Get current process metrics.

        Returns:
            ProcessMetrics with current health data
        """
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = self.process.memory_percent()

            # Get CPU (non-blocking)
            cpu_percent = self.process.cpu_percent(interval=0)

            uptime = time.time() - self.start_time if self.start_time else 0
            heartbeat_age = time.time() - self.last_heartbeat if self.last_heartbeat else 999999

            return ProcessMetrics(
                pid=self.pid,
                name=self.name,
                uptime_seconds=uptime,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                num_threads=self.process.num_threads(),
                status=self.process.status(),
                heartbeat_age_seconds=heartbeat_age,
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error getting metrics: {e}")
            return ProcessMetrics(
                pid=self.pid,
                name=self.name,
                uptime_seconds=0,
                cpu_percent=0,
                memory_mb=0,
                memory_percent=0,
                num_threads=0,
                status="unknown",
                heartbeat_age_seconds=999999,
            )

    def is_healthy(self) -> tuple[bool, str]:
        """
        Check if process is healthy.

        Returns:
            Tuple of (is_healthy, reason)
        """
        if not self.running:
            return False, "not_running"

        if self.shutdown_requested:
            return False, f"shutdown_requested_{self.shutdown_reason}"

        # Check heartbeat
        if self.last_heartbeat:
            heartbeat_age = time.time() - self.last_heartbeat
            if heartbeat_age > self.heartbeat_timeout_seconds:
                return False, f"heartbeat_timeout_{heartbeat_age:.0f}s"

        # Check process still exists
        try:
            if not self.process.is_running():
                return False, "process_not_running"
        except psutil.NoSuchProcess:
            return False, "process_not_found"

        return True, "healthy"

    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        if not self.start_time:
            return 0
        end = self.end_time or time.time()
        return end - self.start_time

    def get_remaining_runtime(self) -> float | None:
        """
        Get remaining runtime in seconds before max runtime reached.

        Returns:
            Remaining seconds, or None if no max runtime set
        """
        if not self.max_runtime_hours or not self.start_time:
            return None

        max_runtime_seconds = self.max_runtime_hours * 3600
        elapsed = time.time() - self.start_time
        remaining = max_runtime_seconds - elapsed

        return max(0, remaining)

    def __enter__(self):
        """Context manager support."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.shutdown()
        return False  # Don't suppress exceptions
