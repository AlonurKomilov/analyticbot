"""
Infrastructure Package for Mock Services
"""

from .base import BaseMockService, mock_metrics
from .registry import MockRegistry, mock_registry  
from .factory import MockFactory, mock_factory

# Auto-register services
from .auto_register import register_all_services
register_all_services()

__all__ = [
    "BaseMockService",
    "mock_metrics", 
    "MockRegistry",
    "mock_registry",
    "MockFactory", 
    "mock_factory"
]