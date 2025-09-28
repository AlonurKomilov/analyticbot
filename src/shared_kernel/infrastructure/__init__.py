"""
Shared Infrastructure Layer
Contains all shared infrastructure components (database, messaging, monitoring)
"""

# Database infrastructure
from .database import DatabaseConfig, DatabaseConnection, get_database_connection

# Messaging infrastructure
from .messaging import SharedTelegramClient, TelegramConfig, get_telegram_client

# Monitoring infrastructure
from .monitoring import (
    AnalyticBotLogger,
    MetricsCollector,
    get_logger,
    get_metrics_collector,
)

__all__ = [
    # Database
    "DatabaseConfig",
    "DatabaseConnection",
    "get_database_connection",
    # Messaging
    "TelegramConfig",
    "SharedTelegramClient",
    "get_telegram_client",
    # Monitoring
    "AnalyticBotLogger",
    "MetricsCollector",
    "get_logger",
    "get_metrics_collector",
]
