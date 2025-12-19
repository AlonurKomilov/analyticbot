"""
Marketplace Services Integration Tests
======================================

Tests for marketplace service subscriptions including:
- Service subscription flow
- MTProto service configuration
- AI service configuration
- Quota management
- Service registry validation
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Any


pytestmark = [pytest.mark.integration, pytest.mark.marketplace]


# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def services_repo(test_db_pool):
    """Provide services repository for testing."""
    from infra.marketplace.repositories.services import ServicesRepository
    return ServicesRepository(test_db_pool)


@pytest_asyncio.fixture
async def test_subscriber(test_db_pool):
    """Create a test user with credits for subscribing to services."""
    user_id = 999999020
    
    await test_db_pool.execute("""
        INSERT INTO users (id, username, email, status, credit_balance)
        VALUES ($1, 'service_subscriber', 'subscriber@example.com', 'active', 10000)
        ON CONFLICT (id) DO UPDATE SET credit_balance = 10000
    """, user_id)
    
    yield {"id": user_id, "username": "service_subscriber", "credit_balance": 10000}
    
    # Cleanup
    await test_db_pool.execute("DELETE FROM user_service_subscriptions WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM service_usage_log WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest_asyncio.fixture
async def test_chat(test_db_pool, test_subscriber):
    """Create a test chat for service configuration."""
    chat_id = -1009999990020
    
    await test_db_pool.execute("""
        INSERT INTO user_chats (chat_id, user_id, title, chat_type, is_active)
        VALUES ($1, $2, 'Test Service Chat', 'supergroup', true)
        ON CONFLICT (chat_id, user_id) DO NOTHING
    """, chat_id, test_subscriber["id"])
    
    yield {"chat_id": chat_id, "title": "Test Service Chat"}
    
    # Cleanup
    await test_db_pool.execute(
        "DELETE FROM user_chats WHERE chat_id = $1 AND user_id = $2",
        chat_id, test_subscriber["id"]
    )


# ============================================================================
# Service Listing Tests
# ============================================================================


class TestServiceListing:
    """Test service listing and filtering."""
    
    async def test_get_all_services(self, services_repo):
        """Test getting all marketplace services."""
        services = await services_repo.get_services()
        
        assert len(services) > 0
        service = services[0]
        assert "id" in service
        assert "service_key" in service
        assert "name" in service
        assert "price_credits" in service
        assert "category_id" in service
    
    async def test_get_services_by_category(self, services_repo):
        """Test filtering services by category."""
        # Get bot services
        bot_services = await services_repo.get_services(category_slug="bot_service")
        
        for service in bot_services:
            assert service["service_key"].startswith("bot_")
    
    async def test_get_mtproto_services(self, services_repo):
        """Test getting MTProto services."""
        mtproto_services = await services_repo.get_services(category_slug="mtproto_services")
        
        expected_keys = [
            "mtproto_history_access",
            "mtproto_auto_collect",
            "mtproto_media_download",
            "mtproto_bulk_export",
        ]
        
        service_keys = [s["service_key"] for s in mtproto_services]
        for key in expected_keys:
            assert key in service_keys, f"Missing MTProto service: {key}"
    
    async def test_get_ai_services(self, services_repo):
        """Test getting AI services."""
        ai_services = await services_repo.get_services(category_slug="ai_services")
        
        expected_keys = [
            "ai_content_optimizer",
            "ai_sentiment_analyzer",
            "ai_smart_replies",
            "ai_content_moderation",
        ]
        
        service_keys = [s["service_key"] for s in ai_services]
        for key in expected_keys:
            assert key in service_keys, f"Missing AI service: {key}"
    
    async def test_get_featured_services(self, services_repo):
        """Test filtering featured services."""
        featured = await services_repo.get_services(is_featured=True)
        
        assert len(featured) > 0
        assert all(s["is_featured"] for s in featured)
    
    async def test_get_service_by_key(self, services_repo):
        """Test getting a specific service by key."""
        service = await services_repo.get_service_by_key("bot_anti_spam")
        
        assert service is not None
        assert service["service_key"] == "bot_anti_spam"
        assert service["name"] == "Anti-Spam Protection"
        assert service["price_credits"] > 0


# ============================================================================
# Subscription Flow Tests
# ============================================================================


class TestSubscriptionFlow:
    """Test service subscription flow."""
    
    async def test_subscribe_to_service(self, services_repo, test_subscriber, test_db_pool):
        """Test successful service subscription."""
        service = await services_repo.get_service_by_key("bot_anti_spam")
        
        result = await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        assert result["success"] is True
        assert result["subscription_id"] is not None
        
        # Verify credits were deducted
        balance = await test_db_pool.fetchval(
            "SELECT credit_balance FROM users WHERE id = $1",
            test_subscriber["id"]
        )
        assert balance == 10000 - service["price_credits"]
    
    async def test_subscribe_creates_expiration(self, services_repo, test_subscriber):
        """Test that subscription has proper expiration date."""
        service = await services_repo.get_service_by_key("bot_banned_words")
        
        result = await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        subscription = await services_repo.get_subscription(result["subscription_id"])
        
        assert subscription["expires_at"] is not None
        # Should expire roughly 30 days from now
        expected_expiry = datetime.utcnow() + timedelta(days=30)
        assert abs((subscription["expires_at"] - expected_expiry).days) <= 1
    
    async def test_duplicate_subscription_fails(self, services_repo, test_subscriber):
        """Test that duplicate active subscription fails."""
        service = await services_repo.get_service_by_key("bot_welcome_messages")
        
        # First subscription
        result1 = await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        assert result1["success"] is True
        
        # Second subscription should fail
        result2 = await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        assert result2["success"] is False
        assert "already subscribed" in result2.get("error", "").lower()
    
    async def test_subscription_insufficient_balance(self, services_repo, test_db_pool):
        """Test subscription with insufficient balance."""
        # Create user with low balance
        user_id = 999999021
        await test_db_pool.execute("""
            INSERT INTO users (id, username, email, status, credit_balance)
            VALUES ($1, 'poor_user', 'poor@example.com', 'active', 10)
            ON CONFLICT (id) DO UPDATE SET credit_balance = 10
        """, user_id)
        
        try:
            service = await services_repo.get_service_by_key("bot_analytics_advanced")
            
            result = await services_repo.subscribe_to_service(
                user_id=user_id,
                service_id=service["id"],
                price=service["price_credits"],
            )
            
            assert result["success"] is False
            assert "insufficient" in result.get("error", "").lower()
        finally:
            await test_db_pool.execute("DELETE FROM users WHERE id = $1", user_id)
    
    async def test_get_user_subscriptions(self, services_repo, test_subscriber):
        """Test getting user's active subscriptions."""
        # Subscribe to multiple services
        services_to_sub = ["bot_invite_tracking", "bot_warning_system"]
        
        for key in services_to_sub:
            service = await services_repo.get_service_by_key(key)
            await services_repo.subscribe_to_service(
                user_id=test_subscriber["id"],
                service_id=service["id"],
                price=service["price_credits"],
            )
        
        subscriptions = await services_repo.get_user_subscriptions(test_subscriber["id"])
        
        assert len(subscriptions) >= 2
        sub_keys = [s["service_key"] for s in subscriptions]
        for key in services_to_sub:
            assert key in sub_keys
    
    async def test_check_subscription_status(self, services_repo, test_subscriber):
        """Test checking subscription status."""
        service = await services_repo.get_service_by_key("mtproto_history_access")
        
        # Before subscription
        is_subscribed = await services_repo.is_subscribed(
            test_subscriber["id"], 
            service["service_key"]
        )
        assert is_subscribed is False
        
        # After subscription
        await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        is_subscribed = await services_repo.is_subscribed(
            test_subscriber["id"],
            service["service_key"]
        )
        assert is_subscribed is True


# ============================================================================
# MTProto Service Tests
# ============================================================================


class TestMTProtoServices:
    """Test MTProto-specific service functionality."""
    
    async def test_mtproto_service_pricing(self, services_repo):
        """Test MTProto service pricing is correct."""
        expected_prices = {
            "mtproto_history_access": 100,
            "mtproto_auto_collect": 150,
            "mtproto_media_download": 75,
            "mtproto_bulk_export": 200,
        }
        
        for key, expected_price in expected_prices.items():
            service = await services_repo.get_service_by_key(key)
            assert service is not None, f"Service {key} not found"
            assert service["price_credits"] == expected_price, \
                f"Price mismatch for {key}: expected {expected_price}, got {service['price_credits']}"
    
    async def test_mtproto_service_quotas(self, services_repo):
        """Test MTProto services have proper quotas."""
        mtproto_services = await services_repo.get_services(category_slug="mtproto_services")
        
        for service in mtproto_services:
            # MTProto services should have quotas
            assert service.get("quota_daily") is not None or service.get("quota_monthly") is not None, \
                f"Service {service['service_key']} missing quota"
    
    async def test_mtproto_history_access_features(self, services_repo):
        """Test MTProto History Access service features."""
        service = await services_repo.get_service_by_key("mtproto_history_access")
        
        assert service is not None
        features = service.get("features", [])
        
        expected_features = ["history", "messages", "fetch"]
        feature_text = " ".join(features).lower()
        assert any(f in feature_text for f in expected_features)


# ============================================================================
# AI Service Tests
# ============================================================================


class TestAIServices:
    """Test AI-specific service functionality."""
    
    async def test_ai_service_pricing(self, services_repo):
        """Test AI service pricing is correct."""
        expected_prices = {
            "ai_content_optimizer": 125,
            "ai_sentiment_analyzer": 100,
            "ai_smart_replies": 150,
            "ai_content_moderation": 175,
        }
        
        for key, expected_price in expected_prices.items():
            service = await services_repo.get_service_by_key(key)
            assert service is not None, f"Service {key} not found"
            assert service["price_credits"] == expected_price, \
                f"Price mismatch for {key}: expected {expected_price}, got {service['price_credits']}"
    
    async def test_ai_service_quotas(self, services_repo):
        """Test AI services have proper quotas."""
        expected_quotas = {
            "ai_content_optimizer": {"daily": 50, "monthly": 1000},
            "ai_sentiment_analyzer": {"daily": 100, "monthly": 2000},
            "ai_smart_replies": {"daily": 200, "monthly": 4000},
            "ai_content_moderation": {"daily": 500, "monthly": 10000},
        }
        
        for key, quotas in expected_quotas.items():
            service = await services_repo.get_service_by_key(key)
            assert service is not None, f"Service {key} not found"
            assert service.get("quota_daily") == quotas["daily"], \
                f"Daily quota mismatch for {key}"
            assert service.get("quota_monthly") == quotas["monthly"], \
                f"Monthly quota mismatch for {key}"
    
    async def test_ai_content_moderation_is_premium(self, services_repo):
        """Test that AI Content Moderation is premium priced."""
        service = await services_repo.get_service_by_key("ai_content_moderation")
        
        assert service["price_credits"] >= 150, "Content moderation should be premium"


# ============================================================================
# Quota Management Tests
# ============================================================================


class TestQuotaManagement:
    """Test service quota tracking and enforcement."""
    
    async def test_track_service_usage(self, services_repo, test_subscriber):
        """Test logging service usage."""
        service = await services_repo.get_service_by_key("ai_content_optimizer")
        
        # Subscribe first
        await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        # Log usage
        await services_repo.log_usage(
            user_id=test_subscriber["id"],
            service_key=service["service_key"],
            units_used=1,
            metadata={"action": "optimize_post"},
        )
        
        # Check usage
        usage = await services_repo.get_usage_today(
            test_subscriber["id"],
            service["service_key"]
        )
        
        assert usage >= 1
    
    async def test_check_quota_available(self, services_repo, test_subscriber):
        """Test checking if quota is available."""
        service = await services_repo.get_service_by_key("ai_sentiment_analyzer")
        
        # Subscribe
        await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        # Should have quota available
        has_quota = await services_repo.has_quota_available(
            test_subscriber["id"],
            service["service_key"]
        )
        
        assert has_quota is True
    
    async def test_quota_exhausted_check(self, services_repo, test_subscriber, test_db_pool):
        """Test that quota exhaustion is detected."""
        service = await services_repo.get_service_by_key("ai_content_optimizer")  # 50/day
        
        # Subscribe
        await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        # Simulate using all quota
        await test_db_pool.execute("""
            INSERT INTO service_usage_log (user_id, service_key, units_used, created_at)
            VALUES ($1, $2, $3, NOW())
        """, test_subscriber["id"], service["service_key"], 50)
        
        # Should not have quota available
        has_quota = await services_repo.has_quota_available(
            test_subscriber["id"],
            service["service_key"]
        )
        
        assert has_quota is False


# ============================================================================
# Service Cancellation Tests
# ============================================================================


class TestServiceCancellation:
    """Test service cancellation flow."""
    
    async def test_cancel_subscription(self, services_repo, test_subscriber):
        """Test cancelling an active subscription."""
        service = await services_repo.get_service_by_key("mtproto_bulk_export")
        
        # Subscribe
        result = await services_repo.subscribe_to_service(
            user_id=test_subscriber["id"],
            service_id=service["id"],
            price=service["price_credits"],
        )
        
        # Cancel
        cancel_result = await services_repo.cancel_subscription(
            result["subscription_id"]
        )
        
        assert cancel_result["success"] is True
        
        # Verify no longer subscribed
        is_subscribed = await services_repo.is_subscribed(
            test_subscriber["id"],
            service["service_key"]
        )
        assert is_subscribed is False
    
    async def test_cancel_nonexistent_subscription(self, services_repo):
        """Test cancelling a non-existent subscription."""
        result = await services_repo.cancel_subscription(99999999)
        
        assert result["success"] is False
