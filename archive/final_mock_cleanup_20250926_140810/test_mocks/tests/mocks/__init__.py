"""
Centralized Mock Infrastructure for AnalyticBot

This module provides a unified testing infrastructure that separates
all mock services from production code.

Design Principles:
1. Single source of truth for all mocks
2. Clean separation of test code from production
3. Consistent mocking patterns across domains
4. Easy mock discovery and management

Usage:
    from tests.mocks import mock_factory
    
    # Create individual services
    analytics = mock_factory.create_analytics_service()
    payment = mock_factory.create_payment_service()
    
    # Create complete testing suite
    test_env = mock_factory.create_testing_suite()
    
    # Reset all services
    mock_factory.reset_all_services()
"""

from .registry import MockRegistry, mock_registry
from .factory import MockFactory, mock_factory
from .base import BaseMockService, mock_metrics
from .compat import create_testing_environment, reset_all_mocks

# Auto-register services
from .auto_register import register_all_services
register_all_services()

__all__ = [
    # Core infrastructure
    "MockRegistry", 
    "MockFactory", 
    "BaseMockService",
    
    # Global instances
    "mock_registry",
    "mock_factory", 
    "mock_metrics",
    
    # Convenience functions
    "create_testing_environment",
    "reset_all_mocks"
]