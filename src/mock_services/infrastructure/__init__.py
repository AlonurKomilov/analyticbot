"""
Infrastructure Package for Mock Services
"""

# Auto-register services
from .auto_register import register_all_services
from .base import BaseMockService, mock_metrics
from .factory import MockFactory, mock_factory
from .registry import MockRegistry, mock_registry

register_all_services()

__all__ = [
    "BaseMockService",
    "mock_metrics",
    "MockRegistry",
    "mock_registry",
    "MockFactory",
    "mock_factory",
]
