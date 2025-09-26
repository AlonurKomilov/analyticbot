"""
Base Event Classes for Inter-Module Communication
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid


@dataclass
class DomainEvent(ABC):
    """Base domain event"""
    source_module: str = ""
    version: str = "1.0"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    @abstractmethod
    def get_event_type(self) -> str:
        """Get event type identifier"""
        pass


@dataclass  
class UserCreatedEvent(DomainEvent):
    """User was created in identity module"""
    user_id: int = 0
    username: str = ""
    email: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "user.created"


@dataclass
class PaymentProcessedEvent(DomainEvent):
    """Payment was processed in payments module"""
    payment_id: int = 0
    user_id: int = 0
    amount: float = 0.0
    status: str = ""
    
    def get_event_type(self) -> str:
        return "payment.processed"


@dataclass
class ChannelAddedEvent(DomainEvent):
    """Channel was added in channels module"""
    channel_id: int = 0
    user_id: int = 0
    channel_name: str = ""
    
    def get_event_type(self) -> str:
        return "channel.added"


@dataclass
class AnalyticsCalculatedEvent(DomainEvent):
    """Analytics were calculated in analytics module"""
    channel_id: int = 0
    calculation_type: str = ""
    results: Dict[str, Any] = field(default_factory=dict)
    
    def get_event_type(self) -> str:
        return "analytics.calculated"


class EventHandler(ABC):
    """Base event handler interface"""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle domain event"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if handler can process event type"""
        pass


class EventBus:
    """Simple in-memory event bus for module communication"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_log: List[DomainEvent] = []
    
    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe handler to event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent):
        """Publish event to all subscribers"""
        event_type = event.get_event_type()
        
        # Log event
        self._event_log.append(event)
        
        # Notify handlers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler.handle(event)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Event handler error: {e}")
    
    def get_event_log(self) -> List[DomainEvent]:
        """Get event log for debugging"""
        return self._event_log.copy()
    
    def clear_event_log(self):
        """Clear event log"""
        self._event_log.clear()


# Global event bus instance
_event_bus: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    """Get global event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
