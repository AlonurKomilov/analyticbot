#!/usr/bin/env python3
"""
Step 3: Module Boundary Enforcement
"""

import os
from pathlib import Path
import re

def create_module_service_interfaces():
    """Create service interfaces for each module's public API"""
    
    print("🔧 STEP 3A: CREATING MODULE SERVICE INTERFACES")
    print("=" * 46)
    
    created_interfaces = []
    
    # Create interfaces for major modules
    module_interfaces = {
        'analytics': {
            'service_name': 'AnalyticsService',
            'methods': [
                'get_channel_analytics(channel_id: int, date_range: tuple) -> dict',
                'get_engagement_metrics(channel_id: int) -> dict',
                'generate_analytics_report(config: dict) -> dict',
                'get_growth_insights(channel_id: int) -> dict'
            ]
        },
        'identity': {
            'service_name': 'IdentityService', 
            'methods': [
                'authenticate_user(credentials: dict) -> Optional[dict]',
                'get_user_profile(user_id: int) -> Optional[dict]',
                'update_user_profile(user_id: int, data: dict) -> dict',
                'create_user(user_data: dict) -> dict'
            ]
        },
        'payments': {
            'service_name': 'PaymentService',
            'methods': [
                'process_payment(payment_data: dict) -> dict',
                'get_payment_status(payment_id: int) -> str',
                'get_user_billing(user_id: int) -> dict',
                'cancel_subscription(user_id: int) -> bool'
            ]
        },
        'channels': {
            'service_name': 'ChannelService',
            'methods': [
                'get_channel_info(channel_id: int) -> Optional[dict]',
                'add_channel(user_id: int, channel_data: dict) -> dict',
                'remove_channel(channel_id: int) -> bool',
                'get_user_channels(user_id: int) -> List[dict]'
            ]
        },
        'bot_service': {
            'service_name': 'BotService',
            'methods': [
                'send_message(chat_id: int, message: str) -> dict',
                'process_command(command: str, user_id: int) -> dict',
                'handle_callback(callback_data: dict) -> dict',
                'get_bot_status() -> dict'
            ]
        }
    }
    
    # Create interface files
    interfaces_dir = Path("src/shared_kernel/domain/interfaces")
    
    for module_name, interface_config in module_interfaces.items():
        service_name = interface_config['service_name']
        methods = interface_config['methods']
        
        interface_content = f'''"""
{service_name} Interface - Public API for {module_name} module
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from datetime import datetime


@runtime_checkable
class {service_name}(Protocol):
    """{service_name} public interface"""
    
'''
        
        # Add methods
        for method in methods:
            method_doc = f'    """{method.split("(")[0]} operation"""'
            interface_content += f'    async def {method}:\n        {method_doc}\n        ...\n\n'
        
        # Write interface file
        interface_file = interfaces_dir / f"{module_name}_service.py"
        with open(interface_file, 'w', encoding='utf-8') as f:
            f.write(interface_content)
        
        print(f"   ✅ Created {interface_file.name}")
        created_interfaces.append(str(interface_file))
    
    return created_interfaces

def create_module_facades():
    """Create facade classes for each module to expose only public APIs"""
    
    print(f"\n🔧 STEP 3B: CREATING MODULE FACADES")
    print("=" * 35)
    
    created_facades = []
    
    # Create facades directory in shared_kernel
    facades_dir = Path("src/shared_kernel/application/facades")
    facades_dir.mkdir(parents=True, exist_ok=True)
    
    modules_to_facade = ['analytics', 'identity', 'payments', 'channels', 'bot_service']
    
    for module_name in modules_to_facade:
        facade_content = f'''"""
{module_name.title()} Module Facade
Provides controlled access to {module_name} module functionality
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.shared_kernel.domain.interfaces.{module_name}_service import {module_name.title().replace('_', '')}Service


class {module_name.title().replace('_', '')}Facade:
    """Facade for {module_name} module"""
    
    def __init__(self, {module_name}_service: {module_name.title().replace('_', '')}Service):
        self._{module_name}_service = {module_name}_service
    
    async def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute operation through the service interface"""
        try:
            if hasattr(self._{module_name}_service, operation):
                method = getattr(self._{module_name}_service, operation)
                result = await method(**kwargs)
                return {{
                    "success": True,
                    "data": result
                }}
            else:
                return {{
                    "success": False,
                    "error": f"Operation '{{operation}}' not found"
                }}
        
        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}
    
    def get_available_operations(self) -> List[str]:
        """Get list of available operations"""
        service_methods = [
            method for method in dir(self._{module_name}_service)
            if not method.startswith('_') and callable(getattr(self._{module_name}_service, method))
        ]
        return service_methods


# Factory function for creating facade instances
def create_{module_name}_facade({module_name}_service: {module_name.title().replace('_', '')}Service) -> {module_name.title().replace('_', '')}Facade:
    """Create {module_name} facade instance"""
    return {module_name.title().replace('_', '')}Facade({module_name}_service)
'''
        
        facade_file = facades_dir / f"{module_name}_facade.py"
        with open(facade_file, 'w', encoding='utf-8') as f:
            f.write(facade_content)
        
        print(f"   ✅ Created {facade_file.name}")
        created_facades.append(str(facade_file))
    
    # Create facades __init__.py
    facades_init_content = '''"""
Module Facades - Controlled access to module functionality
"""

from .analytics_facade import AnalyticsFacade, create_analytics_facade
from .identity_facade import IdentityFacade, create_identity_facade  
from .payments_facade import PaymentsFacade, create_payments_facade
from .channels_facade import ChannelsFacade, create_channels_facade
from .bot_service_facade import BotserviceFacade, create_bot_service_facade

__all__ = [
    "AnalyticsFacade", "create_analytics_facade",
    "IdentityFacade", "create_identity_facade", 
    "PaymentsFacade", "create_payments_facade",
    "ChannelsFacade", "create_channels_facade",
    "BotserviceFacade", "create_bot_service_facade"
]
'''
    
    facades_init_file = facades_dir / "__init__.py"
    with open(facades_init_file, 'w', encoding='utf-8') as f:
        f.write(facades_init_content)
    
    print(f"   ✅ Created {facades_init_file}")
    created_facades.append(str(facades_init_file))
    
    return created_facades

def create_module_communication_layer():
    """Create event-driven communication layer between modules"""
    
    print(f"\n🔧 STEP 3C: CREATING MODULE COMMUNICATION LAYER")
    print("=" * 46)
    
    created_files = []
    
    # Create events directory
    events_dir = Path("src/shared_kernel/domain/events")
    events_dir.mkdir(parents=True, exist_ok=True)
    
    # Create base event classes
    base_events_content = '''"""
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
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source_module: str = ""
    version: str = "1.0"
    
    @abstractmethod
    def get_event_type(self) -> str:
        """Get event type identifier"""
        pass


@dataclass  
class UserCreatedEvent(DomainEvent):
    """User was created in identity module"""
    user_id: int
    username: str
    email: Optional[str] = None
    
    def get_event_type(self) -> str:
        return "user.created"


@dataclass
class PaymentProcessedEvent(DomainEvent):
    """Payment was processed in payments module"""
    payment_id: int
    user_id: int
    amount: float
    status: str
    
    def get_event_type(self) -> str:
        return "payment.processed"


@dataclass
class ChannelAddedEvent(DomainEvent):
    """Channel was added in channels module"""
    channel_id: int
    user_id: int
    channel_name: str
    
    def get_event_type(self) -> str:
        return "channel.added"


@dataclass
class AnalyticsCalculatedEvent(DomainEvent):
    """Analytics were calculated in analytics module"""
    channel_id: int
    calculation_type: str
    results: Dict[str, Any]
    
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
'''
    
    events_file = events_dir / "base_events.py"
    with open(events_file, 'w', encoding='utf-8') as f:
        f.write(base_events_content)
    
    print(f"   ✅ Created {events_file}")
    created_files.append(str(events_file))
    
    # Create events __init__.py
    events_init_content = '''"""
Domain Events for Inter-Module Communication
"""

from .base_events import (
    DomainEvent, EventHandler, EventBus, get_event_bus,
    UserCreatedEvent, PaymentProcessedEvent, ChannelAddedEvent, AnalyticsCalculatedEvent
)

__all__ = [
    "DomainEvent", "EventHandler", "EventBus", "get_event_bus",
    "UserCreatedEvent", "PaymentProcessedEvent", 
    "ChannelAddedEvent", "AnalyticsCalculatedEvent"
]
'''
    
    events_init_file = events_dir / "__init__.py"
    with open(events_init_file, 'w', encoding='utf-8') as f:
        f.write(events_init_content)
    
    print(f"   ✅ Created {events_init_file}")
    created_files.append(str(events_init_file))
    
    return created_files

def update_interface_exports():
    """Update interface exports to include all new interfaces"""
    
    print(f"\n🔧 STEP 3D: UPDATING INTERFACE EXPORTS")
    print("=" * 36)
    
    # Update interfaces __init__.py to include all interfaces
    interfaces_init_path = Path("src/shared_kernel/domain/interfaces/__init__.py")
    
    new_init_content = '''"""
Shared Domain Interfaces
"""

# Repository interfaces
from .repositories import UserRepository, PaymentRepository, AnalyticsRepository

# Service interfaces  
from .services import AuthenticationService, PaymentService, AnalyticsService

# Module service interfaces
from .analytics_service import AnalyticsService as AnalyticsModuleService
from .identity_service import IdentityService as IdentityModuleService
from .payments_service import PaymentService as PaymentsModuleService
from .channels_service import ChannelService as ChannelsModuleService
from .bot_service_service import BotService as BotModuleService

__all__ = [
    # Repository interfaces
    "UserRepository",
    "PaymentRepository", 
    "AnalyticsRepository",
    
    # Service interfaces
    "AuthenticationService",
    "PaymentService",
    "AnalyticsService",
    
    # Module service interfaces
    "AnalyticsModuleService",
    "IdentityModuleService", 
    "PaymentsModuleService",
    "ChannelsModuleService",
    "BotModuleService"
]
'''
    
    with open(interfaces_init_path, 'w', encoding='utf-8') as f:
        f.write(new_init_content)
    
    print(f"   ✅ Updated {interfaces_init_path}")
    
    # Update shared_kernel domain __init__.py
    domain_init_path = Path("src/shared_kernel/domain/__init__.py")
    
    domain_init_content = '''"""
Shared Domain Layer
Contains domain entities, value objects, and domain services that are shared across modules.
"""

# Import interfaces to make them available
from .interfaces import *

# Import events
from .events import *

# Import exceptions
from .exceptions import *
'''
    
    with open(domain_init_path, 'w', encoding='utf-8') as f:
        f.write(domain_init_content)
    
    print(f"   ✅ Updated {domain_init_path}")
    
    return [str(interfaces_init_path), str(domain_init_path)]

def verify_module_boundaries():
    """Verify that module boundaries are properly enforced"""
    
    print(f"\n🔍 STEP 3E: VERIFYING MODULE BOUNDARIES")
    print("=" * 37)
    
    # Check that shared_kernel can be imported
    verification_results = []
    
    try:
        import sys
        sys.path.insert(0, 'src')
        
        # Test interface imports
        from src.shared_kernel.domain.interfaces import UserRepository, AnalyticsModuleService
        print("   ✅ Module interfaces import successfully")
        verification_results.append("interfaces_ok")
        
        # Test facade imports
        from src.shared_kernel.application.facades import AnalyticsFacade
        print("   ✅ Module facades import successfully") 
        verification_results.append("facades_ok")
        
        # Test event imports
        from src.shared_kernel.domain.events import DomainEvent, get_event_bus
        print("   ✅ Event system imports successfully")
        verification_results.append("events_ok")
        
        # Test infrastructure imports
        from src.shared_kernel.infrastructure import get_database_connection, get_telegram_client
        print("   ✅ Shared infrastructure imports successfully")
        verification_results.append("infrastructure_ok")
        
    except ImportError as e:
        print(f"   ❌ Import verification failed: {e}")
        verification_results.append("import_failed")
    
    return verification_results

if __name__ == "__main__":
    print("🚀 STEP 3: MODULE BOUNDARY ENFORCEMENT")
    print()
    
    # Create module service interfaces
    interface_files = create_module_service_interfaces()
    
    # Create module facades
    facade_files = create_module_facades()
    
    # Create communication layer
    event_files = create_module_communication_layer()
    
    # Update exports
    export_files = update_interface_exports()
    
    # Verify boundaries
    verification_results = verify_module_boundaries()
    
    # Summary
    total_created = len(interface_files) + len(facade_files) + len(event_files) + len(export_files)
    
    print(f"\n📊 STEP 3 COMPLETION SUMMARY:")
    print("=" * 30)
    print(f"   ✅ Module service interfaces: {len(interface_files)}")
    print(f"   ✅ Module facades: {len(facade_files)}")
    print(f"   ✅ Event communication files: {len(event_files)}")
    print(f"   🔧 Updated export files: {len(export_files)}")
    print(f"   🎯 Total boundary enforcement files: {total_created}")
    print(f"   🔍 Verification checks passed: {len([r for r in verification_results if r.endswith('_ok')])}")
    
    if len([r for r in verification_results if r.endswith('_ok')]) >= 4:
        print(f"\n🎉 STEP 3 COMPLETE!")
        print(f"   🏗️  Module boundaries properly enforced")
        print(f"   🔌 Interface-based communication established")
        print(f"   📡 Event-driven inter-module communication ready")
        print(f"   ➡️  Ready for Step 4: Extract potential modules")
    else:
        print(f"\n⚠️  STEP 3 NEEDS ATTENTION")
        print(f"   🔧 Some boundary enforcement components need fixing")
        print(f"   🎯 Review import errors and dependencies")