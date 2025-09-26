"""
Migration Adapter Registry
=========================

Central registry for all migration adapters.
Provides unified access to services during migration phase.
"""

from .identity_adapter import get_identity_service
from .analytics_adapter import get_analytics_service  
from .payments_adapter import get_payments_service
from .channels_adapter import get_channels_service
from .scheduling_adapter import get_scheduling_service

__all__ = [
    'get_identity_service',
    'get_analytics_service',
    'get_payments_service', 
    'get_channels_service',
    'get_scheduling_service'
]

def get_service(domain: str, service_name: str = "default"):
    """Get service from any domain using migration adapter"""
    service_getters = {
        'identity': get_identity_service,
        'analytics': get_analytics_service,
        'payments': get_payments_service,
        'channels': get_channels_service,
        'scheduling': get_scheduling_service
    }
    
    getter = service_getters.get(domain)
    if not getter:
        raise ValueError(f"Unknown domain: {domain}")
    
    return getter(service_name)
