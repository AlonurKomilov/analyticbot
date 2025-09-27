"""
Shared Kernel Application Layer
==============================

Application services and patterns shared across all domains.
"""

from .event_bus import (
    AnalyticsTrackingEnabledEvent,
    DomainEvent,
    EventBus,
    InMemoryEventBus,
    PaymentCompletedEvent,
    SubscriptionCreatedEvent,
    UserEmailVerifiedEvent,
    UserRegisteredEvent,
    get_event_bus,
    set_event_bus,
)

# Import facades

__all__ = [
    "DomainEvent",
    "EventBus",
    "InMemoryEventBus",
    "UserRegisteredEvent",
    "UserEmailVerifiedEvent",
    "PaymentCompletedEvent",
    "SubscriptionCreatedEvent",
    "AnalyticsTrackingEnabledEvent",
    "get_event_bus",
    "set_event_bus",
]
