"""
Centralized Mock Services Compatibility Layer

This module provides backward compatibility for existing code while
encouraging migration to the centralized mock infrastructure.
"""

import warnings
from typing import Any

from .auto_register import register_all_services
from .factory import mock_factory

# Ensure all services are registered
register_all_services()


class CompatibilityWarning(UserWarning):
    """Warning for deprecated mock imports"""


def get_mock_analytics_service(**config):
    """Get mock analytics service with backward compatibility"""
    warnings.warn(
        "Direct mock service import is deprecated. Use tests.mocks.mock_factory.create_analytics_service() instead.",
        CompatibilityWarning,
        stacklevel=2,
    )
    return mock_factory.create_analytics_service(**config)


def get_mock_payment_service(**config):
    """Get mock payment service with backward compatibility"""
    warnings.warn(
        "Direct mock service import is deprecated. Use tests.mocks.mock_factory.create_payment_service() instead.",
        CompatibilityWarning,
        stacklevel=2,
    )
    return mock_factory.create_payment_service(**config)


def get_mock_email_service(**config):
    """Get mock email service with backward compatibility"""
    warnings.warn(
        "Direct mock service import is deprecated. Use tests.mocks.mock_factory.create_email_service() instead.",
        CompatibilityWarning,
        stacklevel=2,
    )
    return mock_factory.create_email_service(**config)


# Backward compatibility aliases
MockAnalyticsService = get_mock_analytics_service
MockPaymentService = get_mock_payment_service
MockEmailService = get_mock_email_service


def create_testing_environment(services: list = None) -> dict[str, Any]:
    """Create a complete testing environment with all mock services"""
    return mock_factory.create_testing_suite(services)


def reset_all_mocks():
    """Reset all mock services to clean state"""
    mock_factory.reset_all_services()


__all__ = [
    "get_mock_analytics_service",
    "get_mock_payment_service",
    "get_mock_email_service",
    "create_testing_environment",
    "reset_all_mocks",
    # Backward compatibility
    "MockAnalyticsService",
    "MockPaymentService",
    "MockEmailService",
]
