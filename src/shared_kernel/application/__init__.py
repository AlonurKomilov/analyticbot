"""
Shared Kernel Application Layer
==============================

Application services and patterns shared across all domains.
"""

from .event_bus import (
    DomainEvent,
    EventBus,
    InMemoryEventBus,
    UserRegisteredEvent,
    UserEmailVerifiedEvent,
    PaymentCompletedEvent,
    SubscriptionCreatedEvent,
    AnalyticsTrackingEnabledEvent,
    get_event_bus,
    set_event_bus
)

# Import facades
from .facades import *

__all__ = [
    'DomainEvent',
    'EventBus', 
    'InMemoryEventBus',
    'UserRegisteredEvent',
    'UserEmailVerifiedEvent',
    'PaymentCompletedEvent',
    'SubscriptionCreatedEvent',
    'AnalyticsTrackingEnabledEvent',
    'get_event_bus',
    'set_event_bus'
]