"""
Bot Clients Package - Clean Architecture

Provides clean client abstractions for external service integration.
All clients follow clean architecture principles with proper error handling.
"""

from .analytics_client import (
    AnalyticsClient,
    AnalyticsClientError,
    # Backward compatibility aliases
    AnalyticsV2Client,
    AnalyticsV2ClientError,
)

__all__ = [
    # Clean Architecture (primary)
    "AnalyticsClient",
    "AnalyticsClientError",
    # Backward compatibility
    "AnalyticsV2Client",
    "AnalyticsV2ClientError",
]
