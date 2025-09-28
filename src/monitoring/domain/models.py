"""
Monitoring Domain Models
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Log entry domain model"""

    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    extra_data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "module": self.module,
            "extra_data": self.extra_data or {},
        }


@dataclass
class Metric:
    """Metric domain model"""

    name: str
    value: float
    timestamp: datetime
    tags: dict[str, str] | None = None
    metric_type: str = "gauge"  # gauge, counter, histogram

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags or {},
            "type": self.metric_type,
        }


@dataclass
class HealthCheck:
    """Health check domain model"""

    component: str
    status: str  # healthy, unhealthy, degraded
    timestamp: datetime
    details: dict[str, Any] | None = None

    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return self.status == "healthy"
