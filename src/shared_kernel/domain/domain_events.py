"""
Domain Events - Event-driven architecture support
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    """
    Base class for all domain events.

    Domain events represent something that happened in the domain
    that other parts of the system might be interested in.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_version: int = field(default=1)

    @property
    def event_type(self) -> str:
        """Get the event type (class name)"""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "event_version": self.event_version,
            **self._get_event_data(),
        }

    def _get_event_data(self) -> dict[str, Any]:
        """Override this method to provide event-specific data"""
        return {}


class DomainEventDispatcher:
    """
    Simple domain event dispatcher.

    In a more complex system, this would integrate with
    a message broker or event store.
    """

    def __init__(self):
        self._handlers: dict[str, list] = {}

    def register_handler(self, event_type: str, handler) -> None:
        """Register an event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an event to all registered handlers"""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                # In production, you'd want proper error handling and logging
                print(f"Error handling event {event.event_type}: {e}")


# Global event dispatcher instance
event_dispatcher = DomainEventDispatcher()
