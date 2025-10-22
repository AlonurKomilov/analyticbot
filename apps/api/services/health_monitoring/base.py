"""
Base module for health monitoring
Shared imports, constants, and re-exports from core models
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

# Re-export core health models for convenience
from core.common.health.models import (
    ComponentHealth,
    DependencyType,
    HealthStatus,
    HealthThresholds,
    SystemHealth,
    default_thresholds,
)

# Shared logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SERVICE_NAME = "analyticbot"
DEFAULT_VERSION = "2.1.0"
DEFAULT_ENVIRONMENT = "development"
MAX_HISTORY_SIZE = 100
DEFAULT_CHECK_TIMEOUT = 5.0

# Health check intervals
FAST_CHECK_INTERVAL = 30  # seconds
NORMAL_CHECK_INTERVAL = 60  # seconds
SLOW_CHECK_INTERVAL = 300  # seconds

__all__ = [
    "ComponentHealth",
    "DependencyType",
    "HealthStatus",
    "HealthThresholds",
    "SystemHealth",
    "default_thresholds",
    "logger",
    "DEFAULT_SERVICE_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_ENVIRONMENT",
    "MAX_HISTORY_SIZE",
    "DEFAULT_CHECK_TIMEOUT",
]
