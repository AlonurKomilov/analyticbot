"""
Base module for alert runner
Shared imports and configuration
"""

import logging

# Shared logger
logger = logging.getLogger(__name__)

# Alert type constants
ALERT_TYPE_SPIKE = "spike"
ALERT_TYPE_QUIET = "quiet"
ALERT_TYPE_GROWTH = "growth"

# Default configuration
DEFAULT_INTERVAL_SECONDS = 300
DEFAULT_PERIOD_HOURS = 24
DEFAULT_BASELINE_DAYS = 7
MAX_CONCURRENT_ALERTS = 10
