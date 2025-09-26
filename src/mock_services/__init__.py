"""
Centralized Mock Services Infrastructure

Single source of truth for all mock services in the AnalyticBot project.
Consolidates all scattered mock implementations into one organized location.

Location: src/mock_services/
Purpose: Centralized, consistent mock services for testing and demo modes

Usage:
    from src.mock_services import mock_factory
    
    # Create services
    analytics = mock_factory.create_analytics_service()
    payment = mock_factory.create_payment_service()
    
    # Create complete suite
    test_env = mock_factory.create_testing_suite()
"""

from .infrastructure.registry import mock_registry
from .infrastructure.factory import mock_factory
from .infrastructure.base import BaseMockService, mock_metrics

# Auto-register all services on import
from .infrastructure.auto_register import register_all_services
register_all_services()

__all__ = [
    # Core infrastructure
    "mock_registry",
    "mock_factory", 
    "mock_metrics",
    "BaseMockService",
    
    # Convenience access to services
    "get_analytics_service",
    "get_payment_service",
    "get_email_service",
    "get_testing_suite",
    "reset_all_services"
]

# Convenience functions
def get_analytics_service(**config):
    """Get mock analytics service"""
    return mock_factory.create_analytics_service(**config)

def get_payment_service(**config):  
    """Get mock payment service"""
    return mock_factory.create_payment_service(**config)

def get_email_service(**config):
    """Get mock email service"""
    return mock_factory.create_email_service(**config)

def get_testing_suite(services=None):
    """Get complete testing suite"""
    return mock_factory.create_testing_suite(services)

def reset_all_services():
    """Reset all mock services"""
    mock_factory.reset_all_services()