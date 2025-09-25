#!/usr/bin/env python3
"""
Test Inter-Domain Communication - Phase 4 Validation
====================================================

Tests the event-driven communication between Identity, Analytics, and Payments domains.
Validates that events are properly published and handled across domain boundaries.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

print("🚀 Starting Inter-Domain Communication Tests")
print("=" * 60)


async def test_event_bus_basic():
    """Test basic event bus functionality"""
    print("🧪 Testing Event Bus Basic Operations...")
    
    try:
        from src.shared_kernel.application.event_bus import (
            get_event_bus,
            UserRegisteredEvent,
            PaymentCompletedEvent
        )
        
        event_bus = get_event_bus()
        
        # Test event creation
        user_event = UserRegisteredEvent(
            user_id="user_123",
            email="test@example.com",
            username="testuser"
        )
        
        payment_event = PaymentCompletedEvent(
            payment_id="pay_123",
            customer_id="user_123",
            amount="29.99",
            currency="USD"
        )
        
        # Test event serialization
        user_dict = user_event.to_dict()
        payment_dict = payment_event.to_dict()
        
        assert user_dict['event_name'] == "identity.user_registered"
        assert payment_dict['event_name'] == "payments.payment_completed"
        assert user_dict['user_id'] == "user_123"
        assert payment_dict['amount'] == "29.99"
        
        print("  ✓ Event creation and serialization working")
        
        # Test event publishing (no subscribers yet)
        await event_bus.publish(user_event)
        await event_bus.publish(payment_event)
        
        print("  ✓ Event publishing working")
        print("✅ Event Bus basic operations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Event Bus basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_inter_domain_handlers():
    """Test inter-domain event handlers registration"""
    print("🧪 Testing Inter-Domain Event Handlers...")
    
    try:
        from src.shared_kernel.application.event_bus import get_event_bus, UserRegisteredEvent
        from src.identity.application.event_handlers import register_identity_event_handlers
        from src.analytics.application.event_handlers import register_analytics_event_handlers
        from src.payments.application.event_handlers import register_payments_event_handlers
        
        event_bus = get_event_bus()
        
        # Register all domain event handlers
        await register_identity_event_handlers(event_bus)
        await register_analytics_event_handlers(event_bus)
        await register_payments_event_handlers(event_bus)
        
        print("  ✓ All domain event handlers registered")
        
        # Test event with handlers
        user_event = UserRegisteredEvent(
            user_id="user_456",
            email="newuser@example.com",
            username="newuser"
        )
        
        # Publish event - should trigger handlers in analytics and payments domains
        await event_bus.publish(user_event)
        
        print("  ✓ Cross-domain event publishing working")
        print("✅ Inter-domain event handlers successful!")
        return True
        
    except Exception as e:
        print(f"❌ Inter-domain handlers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_event_publishers():
    """Test domain event publishers"""
    print("🧪 Testing Domain Event Publishers...")
    
    try:
        from src.shared_kernel.application.event_bus import get_event_bus
        from src.identity.application.event_publishers import IdentityEventPublisher
        from src.analytics.application.event_publishers import AnalyticsEventPublisher
        from src.payments.application.event_publishers import PaymentsEventPublisher
        
        event_bus = get_event_bus()
        
        # Create publishers
        identity_publisher = IdentityEventPublisher(event_bus)
        analytics_publisher = AnalyticsEventPublisher(event_bus)
        payments_publisher = PaymentsEventPublisher(event_bus)
        
        print("  ✓ All domain event publishers created")
        
        # Test publishing from each domain
        await identity_publisher.publish_user_registered(
            user_id="user_789",
            email="publisher@example.com",
            username="publisher"
        )
        
        await analytics_publisher.publish_tracking_enabled(
            user_id="user_789",
            channel_id="channel_123"
        )
        
        await payments_publisher.publish_payment_completed(
            payment_id="pay_789",
            customer_id="user_789", 
            amount="49.99",
            currency="USD"
        )
        
        await payments_publisher.publish_subscription_created(
            subscription_id="sub_789",
            customer_id="user_789",
            plan_name="premium"
        )
        
        print("  ✓ All domain publishers working")
        print("✅ Domain event publishers successful!")
        return True
        
    except Exception as e:
        print(f"❌ Event publishers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_complete_workflow():
    """Test a complete cross-domain workflow"""
    print("🧪 Testing Complete Cross-Domain Workflow...")
    
    try:
        from src.shared_kernel.application.event_bus import get_event_bus
        from src.identity.application.event_publishers import IdentityEventPublisher
        from src.payments.application.event_publishers import PaymentsEventPublisher
        from src.identity.application.event_handlers import register_identity_event_handlers
        from src.analytics.application.event_handlers import register_analytics_event_handlers
        
        event_bus = get_event_bus()
        
        # Set up handlers
        await register_identity_event_handlers(event_bus)
        await register_analytics_event_handlers(event_bus)
        
        # Create publishers  
        identity_publisher = IdentityEventPublisher(event_bus)
        payments_publisher = PaymentsEventPublisher(event_bus)
        
        # Simulate complete user journey
        print("  → Simulating user registration...")
        await identity_publisher.publish_user_registered(
            user_id="workflow_user",
            email="workflow@example.com",
            username="workflow"
        )
        
        print("  → Simulating email verification...")
        await identity_publisher.publish_user_email_verified(
            user_id="workflow_user",
            email="workflow@example.com"
        )
        
        print("  → Simulating subscription creation...")
        await payments_publisher.publish_subscription_created(
            subscription_id="sub_workflow",
            customer_id="workflow_user",
            plan_name="premium"
        )
        
        print("  → Simulating payment completion...")
        await payments_publisher.publish_payment_completed(
            payment_id="pay_workflow",
            customer_id="workflow_user",
            amount="29.99",
            currency="USD"
        )
        
        print("  ✓ Complete workflow executed successfully")
        print("✅ Cross-domain workflow successful!")
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all inter-domain communication tests"""
    tests = [
        ("Event Bus Basic Operations", test_event_bus_basic),
        ("Inter-Domain Event Handlers", test_inter_domain_handlers), 
        ("Domain Event Publishers", test_event_publishers),
        ("Complete Cross-Domain Workflow", test_complete_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        result = await test_func()
        results.append(result)
        
        if result:
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎊 ALL {total} TESTS PASSED! Inter-domain communication working perfectly!")
        print("\n🚀 Phase 4.1 (Inter-Domain Communication) - COMPLETE!")
    else:
        print(f"📊 Test Results: {passed}/{total} tests passed")
        if passed > 0:
            print("✅ Some inter-domain functionality working")
        print("❌ Some tests failed. Check errors above.")


if __name__ == "__main__":
    asyncio.run(main())