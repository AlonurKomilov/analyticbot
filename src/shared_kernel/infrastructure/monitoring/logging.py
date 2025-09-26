"""
Shared Logging and Monitoring Infrastructure
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import json
from datetime import datetime


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
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(logs_dir / "analyticbot.log")
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.info(message)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.error(message)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.warning(message)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.debug(message)


class MetricsCollector:
    """Simple metrics collection"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.logger = AnalyticBotLogger("metrics")
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = f"counter.{name}"
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += value
        
        self.logger.info(f"Metric incremented: {name}", {
            "value": value,
            "total": self.metrics[key],
            "tags": tags or {}
        })
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        key = f"gauge.{name}"
        self.metrics[key] = value
        
        self.logger.info(f"Gauge set: {name}", {
            "value": value,
            "tags": tags or {}
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.copy()
        }


# Global instances
_logger: Optional[AnalyticBotLogger] = None
_metrics: Optional[MetricsCollector] = None

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
