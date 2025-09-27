"""
Shared Logging and Monitoring Infrastructure
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class AnalyticBotLogger:
    """Centralized logging for all modules"""

    def __init__(self, name: str = "analyticbot", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers"""

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(logs_dir / "analyticbot.log")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def info(self, message: str, extra: dict[str, Any] | None = None):
        """Log info message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.info(message)

    def error(self, message: str, extra: dict[str, Any] | None = None):
        """Log error message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.error(message)

    def warning(self, message: str, extra: dict[str, Any] | None = None):
        """Log warning message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.warning(message)

    def debug(self, message: str, extra: dict[str, Any] | None = None):
        """Log debug message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.debug(message)


class MetricsCollector:
    """Simple metrics collection"""

    def __init__(self):
        self.metrics: dict[str, Any] = {}
        self.logger = AnalyticBotLogger("metrics")

    def increment_counter(self, name: str, value: int = 1, tags: dict[str, str] | None = None):
        """Increment a counter metric"""
        key = f"counter.{name}"
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value

        self.logger.info(
            f"Metric incremented: {name}",
            {"value": value, "total": self.metrics[key], "tags": tags or {}},
        )

    def set_gauge(self, name: str, value: float, tags: dict[str, str] | None = None):
        """Set a gauge metric"""
        key = f"gauge.{name}"
        self.metrics[key] = value

        self.logger.info(f"Gauge set: {name}", {"value": value, "tags": tags or {}})

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics"""
        return {"timestamp": datetime.now().isoformat(), "metrics": self.metrics.copy()}


# Global instances
_logger: AnalyticBotLogger | None = None
_metrics: MetricsCollector | None = None


def get_logger(name: str = "analyticbot") -> AnalyticBotLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = AnalyticBotLogger(name)
    return _logger


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics
