"""
Event Bus for Inter-Domain Communication
========================================

Provides event-driven communication between domains following Clean Architecture.
Enables loose coupling between Identity, Analytics, and Payments domains.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class DomainEvent(ABC):
    """Base class for all domain events"""
    
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_id = f"{self.__class__.__name__}_{int(self.occurred_at.timestamp() * 1000)}"
    
    @property
    @abstractmethod
    def event_name(self) -> str:
        """Unique event name"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        pass


class EventBus(ABC):
    """Abstract event bus for inter-domain communication"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_name: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe to an event type"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_name: str, handler: Callable[[DomainEvent], None]) -> None:
        """Unsubscribe from an event type"""
        pass


class InMemoryEventBus(EventBus):
    """In-memory event bus implementation for local domain communication"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish event to all subscribers"""
        event_name = event.event_name
        handlers = self._subscribers.get(event_name, [])
        
        logger.debug(f"Publishing {event_name} to {len(handlers)} handlers")
        
        # Execute all handlers concurrently
        if handlers:
            tasks = [self._safe_handle(handler, event) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def subscribe(self, event_name: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe handler to event type"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)
            logger.debug(f"Subscribed handler to {event_name}")
    
    async def unsubscribe(self, event_name: str, handler: Callable[[DomainEvent], None]) -> None:
        """Unsubscribe handler from event type"""
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(handler)
                logger.debug(f"Unsubscribed handler from {event_name}")
            except ValueError:
                logger.warning(f"Handler not found for {event_name}")
    
    async def _safe_handle(self, handler: Callable, event: DomainEvent) -> None:
        """Safely execute event handler with error handling"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Event handler failed for {event.event_name}: {e}")


# ==============================
# INTER-DOMAIN EVENTS
# ==============================

class UserRegisteredEvent(DomainEvent):
    """Event emitted when a new user registers"""
    
    def __init__(self, user_id: str, email: str, username: str = None):
        super().__init__()
        self.user_id = user_id
        self.email = email
        self.username = username
    
    @property
    def event_name(self) -> str:
        return "identity.user_registered"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'occurred_at': self.occurred_at.isoformat(),
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username
        }


class UserEmailVerifiedEvent(DomainEvent):
    """Event emitted when user email is verified"""
    
    def __init__(self, user_id: str, email: str):
        super().__init__()
        self.user_id = user_id
        self.email = email
    
    @property
    def event_name(self) -> str:
        return "identity.user_email_verified"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'occurred_at': self.occurred_at.isoformat(),
            'user_id': self.user_id,
            'email': self.email
        }


class PaymentCompletedEvent(DomainEvent):
    """Event emitted when a payment is completed"""
    
    def __init__(self, payment_id: str, customer_id: str, amount: str, currency: str):
        super().__init__()
        self.payment_id = payment_id
        self.customer_id = customer_id
        self.amount = amount
        self.currency = currency
    
    @property
    def event_name(self) -> str:
        return "payments.payment_completed"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'occurred_at': self.occurred_at.isoformat(),
            'payment_id': self.payment_id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'currency': self.currency
        }


class SubscriptionCreatedEvent(DomainEvent):
    """Event emitted when a subscription is created"""
    
    def __init__(self, subscription_id: str, customer_id: str, plan_name: str):
        super().__init__()
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.plan_name = plan_name
    
    @property
    def event_name(self) -> str:
        return "payments.subscription_created"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'occurred_at': self.occurred_at.isoformat(),
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'plan_name': self.plan_name
        }


class AnalyticsTrackingEnabledEvent(DomainEvent):
    """Event emitted when analytics tracking is enabled for a user"""
    
    def __init__(self, user_id: str, channel_id: str = None):
        super().__init__()
        self.user_id = user_id
        self.channel_id = channel_id
    
    @property
    def event_name(self) -> str:
        return "analytics.tracking_enabled"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'occurred_at': self.occurred_at.isoformat(),
            'user_id': self.user_id,
            'channel_id': self.channel_id
        }


# ==============================
# GLOBAL EVENT BUS INSTANCE
# ==============================

# Global event bus instance for the application
_event_bus: EventBus = None

def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
    return _event_bus

def set_event_bus(event_bus: EventBus) -> None:
    """Set a custom event bus implementation"""
    global _event_bus
    _event_bus = event_bus