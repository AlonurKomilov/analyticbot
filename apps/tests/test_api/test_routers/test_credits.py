"""
Credit System Integration Tests
===============================

Comprehensive tests for the credit system including:
- Credit balance operations
- Credit transactions
- Daily rewards and streaks
- Referral system
- Achievement system
- Marketplace operations
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from httpx import AsyncClient

pytestmark = [pytest.mark.integration, pytest.mark.api]


# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def credit_repo(test_db_pool):
    """Provide credit repository for testing."""
    from infra.db.repositories.credit_repository import CreditRepository
    return CreditRepository(test_db_pool)


@pytest_asyncio.fixture
async def marketplace_repo(test_db_pool):
    """Provide marketplace repository for testing."""
    from infra.db.repositories.marketplace_repository import MarketplaceRepository
    return MarketplaceRepository(test_db_pool)


@pytest_asyncio.fixture
async def test_user(test_db_pool):
    """Create a test user with credits."""
    user_id = 999999001
    
    # Create user
    await test_db_pool.execute("""
        INSERT INTO users (id, username, email, status, credit_balance, referral_code)
        VALUES ($1, 'credit_test_user', 'credit_test@example.com', 'active', 1000, 'TESTCODE1')
        ON CONFLICT (id) DO UPDATE SET credit_balance = 1000, referral_code = 'TESTCODE1'
    """, user_id)
    
    # Create user_credits record
    await test_db_pool.execute("""
        INSERT INTO user_credits (user_id, balance, lifetime_earned, lifetime_spent, daily_streak)
        VALUES ($1, 1000, 1000, 0, 0)
        ON CONFLICT (user_id) DO UPDATE SET balance = 1000, lifetime_earned = 1000, lifetime_spent = 0, daily_streak = 0
    """, user_id)
    
    yield {"id": user_id, "username": "credit_test_user", "referral_code": "TESTCODE1"}
    
    # Cleanup
    await test_db_pool.execute("DELETE FROM user_credits WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM user_achievements WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM user_referrals WHERE referrer_user_id = $1 OR referred_user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM user_purchases WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest_asyncio.fixture
async def second_test_user(test_db_pool):
    """Create a second test user for referral testing."""
    user_id = 999999002
    
    await test_db_pool.execute("""
        INSERT INTO users (id, username, email, status, credit_balance)
        VALUES ($1, 'credit_test_user2', 'credit_test2@example.com', 'active', 0)
        ON CONFLICT (id) DO UPDATE SET credit_balance = 0
    """, user_id)
    
    yield {"id": user_id, "username": "credit_test_user2"}
    
    # Cleanup
    await test_db_pool.execute("DELETE FROM user_credits WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM user_referrals WHERE referrer_user_id = $1 OR referred_user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM users WHERE id = $1", user_id)


# ============================================================================
# Balance Operations Tests
# ============================================================================


class TestCreditBalanceOperations:
    """Test credit balance operations."""

    async def test_get_balance(self, credit_repo, test_user):
        """Test getting user balance."""
        balance = await credit_repo.get_balance(test_user["id"])
        
        assert balance is not None
        assert float(balance["balance"]) == 1000.0
        assert float(balance["lifetime_earned"]) == 1000.0
        assert float(balance["lifetime_spent"]) == 0.0
        assert balance["daily_streak"] == 0

    async def test_add_credits(self, credit_repo, test_user):
        """Test adding credits to user balance."""
        transaction = await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=Decimal("100"),
            transaction_type="bonus",
            category="test",
            description="Test bonus credits",
        )
        
        assert transaction is not None
        assert float(transaction["amount"]) == 100.0
        assert float(transaction["balance_after"]) == 1100.0
        
        # Verify new balance
        balance = await credit_repo.get_balance(test_user["id"])
        assert float(balance["balance"]) == 1100.0

    async def test_add_credits_with_negative_amount_fails(self, credit_repo, test_user):
        """Test that adding negative credits raises error."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            await credit_repo.add_credits(
                user_id=test_user["id"],
                amount=Decimal("-50"),
                transaction_type="bonus",
                category="test",
            )

    async def test_spend_credits(self, credit_repo, test_user):
        """Test spending credits."""
        # First add a service for testing
        from infra.db.repositories.credit_repository import CreditRepository
        
        transaction = await credit_repo.spend_credits(
            user_id=test_user["id"],
            amount=Decimal("50"),
            service_key="test_service",
            description="Test service usage",
        )
        
        assert transaction is not None
        assert float(transaction["amount"]) == -50.0
        assert float(transaction["balance_after"]) == 950.0

    async def test_spend_credits_insufficient_balance(self, credit_repo, test_user):
        """Test spending more credits than available."""
        with pytest.raises(ValueError, match="Insufficient credits"):
            await credit_repo.spend_credits(
                user_id=test_user["id"],
                amount=Decimal("5000"),
                service_key="test_service",
            )

    async def test_can_afford(self, credit_repo, test_user):
        """Test affordability check."""
        assert await credit_repo.can_afford(test_user["id"], Decimal("500")) is True
        assert await credit_repo.can_afford(test_user["id"], Decimal("1000")) is True
        assert await credit_repo.can_afford(test_user["id"], Decimal("1001")) is False


# ============================================================================
# Transaction History Tests
# ============================================================================


class TestTransactionHistory:
    """Test credit transaction history."""

    async def test_get_transactions(self, credit_repo, test_user):
        """Test getting transaction history."""
        # Add some transactions first
        await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=Decimal("50"),
            transaction_type="bonus",
            category="test",
            description="Test transaction 1",
        )
        await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=Decimal("25"),
            transaction_type="reward",
            category="daily",
            description="Test transaction 2",
        )
        
        transactions = await credit_repo.get_transactions(test_user["id"])
        
        assert len(transactions) >= 2
        # Most recent first
        assert transactions[0]["description"] == "Test transaction 2"

    async def test_get_transactions_with_filter(self, credit_repo, test_user):
        """Test filtering transactions by type."""
        # Add different transaction types
        await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=Decimal("10"),
            transaction_type="bonus",
            category="test",
        )
        await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=Decimal("20"),
            transaction_type="reward",
            category="daily",
        )
        
        bonus_transactions = await credit_repo.get_transactions(
            test_user["id"],
            transaction_type="bonus"
        )
        
        assert all(t["type"] == "bonus" for t in bonus_transactions)

    async def test_get_transaction_count(self, credit_repo, test_user):
        """Test getting transaction count."""
        # Add transactions
        await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=Decimal("10"),
            transaction_type="bonus",
            category="test",
        )
        
        count = await credit_repo.get_transaction_count(test_user["id"])
        assert count >= 1


# ============================================================================
# Daily Rewards Tests
# ============================================================================


class TestDailyRewards:
    """Test daily reward system."""

    async def test_claim_daily_reward_first_time(self, credit_repo, test_user):
        """Test claiming daily reward for the first time."""
        result = await credit_repo.claim_daily_reward(test_user["id"])
        
        assert result is not None
        assert result["streak"] == 1
        assert result["credits_earned"] >= 1.0  # Base reward

    async def test_claim_daily_reward_already_claimed(self, credit_repo, test_user, test_db_pool):
        """Test claiming daily reward when already claimed today."""
        # Set last claim to today
        await test_db_pool.execute("""
            UPDATE user_credits 
            SET last_daily_reward_at = NOW(), daily_streak = 1 
            WHERE user_id = $1
        """, test_user["id"])
        
        result = await credit_repo.claim_daily_reward(test_user["id"])
        
        assert result is None  # Already claimed

    async def test_daily_reward_streak_continues(self, credit_repo, test_user, test_db_pool):
        """Test that streak continues when claimed on consecutive days."""
        # Set last claim to yesterday with streak of 3
        yesterday = datetime.utcnow() - timedelta(days=1)
        await test_db_pool.execute("""
            UPDATE user_credits 
            SET last_daily_reward_at = $2, daily_streak = 3 
            WHERE user_id = $1
        """, test_user["id"], yesterday)
        
        result = await credit_repo.claim_daily_reward(test_user["id"])
        
        assert result is not None
        assert result["streak"] == 4  # Streak continues

    async def test_daily_reward_streak_breaks(self, credit_repo, test_user, test_db_pool):
        """Test that streak resets when skipping a day."""
        # Set last claim to 2 days ago
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        await test_db_pool.execute("""
            UPDATE user_credits 
            SET last_daily_reward_at = $2, daily_streak = 5 
            WHERE user_id = $1
        """, test_user["id"], two_days_ago)
        
        result = await credit_repo.claim_daily_reward(test_user["id"])
        
        assert result is not None
        assert result["streak"] == 1  # Streak reset


# ============================================================================
# Referral System Tests
# ============================================================================


class TestReferralSystem:
    """Test referral system."""

    async def test_get_referral_stats(self, credit_repo, test_user):
        """Test getting referral statistics."""
        stats = await credit_repo.get_referral_stats(test_user["id"])
        
        assert stats is not None
        assert stats["referral_code"] == "TESTCODE1"
        assert stats["total_referrals"] >= 0

    async def test_apply_referral_success(self, credit_repo, test_user, second_test_user):
        """Test applying a referral code successfully."""
        result = await credit_repo.apply_referral(
            referred_user_id=second_test_user["id"],
            referral_code=test_user["referral_code"],
        )
        
        assert result is not None
        assert result["referrer_id"] == test_user["id"]
        assert result["referrer_bonus"] == 100.0  # Default referrer bonus
        assert result["referred_bonus"] == 50.0   # Default referred bonus

    async def test_apply_referral_invalid_code(self, credit_repo, second_test_user):
        """Test applying an invalid referral code."""
        with pytest.raises(ValueError, match="Invalid referral code"):
            await credit_repo.apply_referral(
                referred_user_id=second_test_user["id"],
                referral_code="INVALIDCODE",
            )

    async def test_apply_referral_self_referral(self, credit_repo, test_user):
        """Test that self-referral is not allowed."""
        with pytest.raises(ValueError, match="Cannot use your own referral code"):
            await credit_repo.apply_referral(
                referred_user_id=test_user["id"],
                referral_code=test_user["referral_code"],
            )

    async def test_apply_referral_already_referred(self, credit_repo, test_user, second_test_user, test_db_pool):
        """Test applying referral when already referred."""
        # First, apply the referral
        await credit_repo.apply_referral(
            referred_user_id=second_test_user["id"],
            referral_code=test_user["referral_code"],
        )
        
        # Try to apply again
        with pytest.raises(ValueError, match="already been referred"):
            await credit_repo.apply_referral(
                referred_user_id=second_test_user["id"],
                referral_code=test_user["referral_code"],
            )


# ============================================================================
# Achievement System Tests
# ============================================================================


class TestAchievementSystem:
    """Test achievement system."""

    async def test_get_all_achievements(self, credit_repo):
        """Test getting all achievements."""
        achievements = await credit_repo.get_all_achievements()
        
        assert len(achievements) > 0
        # Check that seeded achievements exist
        achievement_keys = [a["achievement_key"] for a in achievements]
        assert "first_login" in achievement_keys
        assert "streak_7" in achievement_keys

    async def test_get_user_achievements_empty(self, credit_repo, test_user):
        """Test getting achievements for user with none."""
        achievements = await credit_repo.get_user_achievements(test_user["id"])
        
        assert achievements == []

    async def test_check_and_award_achievement(self, credit_repo, test_user):
        """Test awarding an achievement."""
        result = await credit_repo.check_and_award_achievement(
            user_id=test_user["id"],
            achievement_key="first_login",
        )
        
        assert result is not None
        assert result["achievement_key"] == "first_login"
        assert result["credits_awarded"] == 10.0

    async def test_check_and_award_achievement_already_earned(self, credit_repo, test_user):
        """Test that achievement is not awarded twice."""
        # Award first time
        await credit_repo.check_and_award_achievement(
            user_id=test_user["id"],
            achievement_key="first_login",
        )
        
        # Try to award again
        result = await credit_repo.check_and_award_achievement(
            user_id=test_user["id"],
            achievement_key="first_login",
        )
        
        assert result is None  # Not awarded again

    async def test_get_achievement_progress(self, credit_repo, test_user):
        """Test getting achievement progress."""
        progress = await credit_repo.get_achievement_progress(test_user["id"])
        
        assert progress is not None
        assert progress["total_achievements"] > 0
        assert "achievements" in progress

    async def test_check_streak_achievements(self, credit_repo, test_user):
        """Test streak-based achievements."""
        # Award streak achievements for streak of 7
        awarded = await credit_repo.check_streak_achievements(test_user["id"], 7)
        
        # Should award streak_3 and streak_7
        awarded_keys = [a["achievement_key"] for a in awarded]
        assert "streak_3" in awarded_keys
        assert "streak_7" in awarded_keys


# ============================================================================
# Marketplace Tests
# ============================================================================


class TestMarketplace:
    """Test marketplace operations."""

    async def test_get_marketplace_items(self, marketplace_repo):
        """Test getting marketplace items."""
        items = await marketplace_repo.get_items()
        
        assert len(items) > 0
        # Check seeded items exist
        slugs = [i["slug"] for i in items]
        assert "dark-mode-pro" in slugs

    async def test_get_items_by_category(self, marketplace_repo):
        """Test filtering items by category."""
        themes = await marketplace_repo.get_items(category="themes")
        
        assert all(item["category"] == "themes" for item in themes)
        assert len(themes) > 0

    async def test_get_featured_items(self, marketplace_repo):
        """Test getting featured items."""
        featured = await marketplace_repo.get_items(is_featured=True)
        
        assert all(item["is_featured"] for item in featured)

    async def test_get_item_by_slug(self, marketplace_repo):
        """Test getting single item by slug."""
        item = await marketplace_repo.get_item_by_slug("dark-mode-pro")
        
        assert item is not None
        assert item["name"] == "Dark Mode Pro"
        assert item["category"] == "themes"

    async def test_get_item_by_slug_not_found(self, marketplace_repo):
        """Test getting non-existent item."""
        item = await marketplace_repo.get_item_by_slug("non-existent-item")
        
        assert item is None

    async def test_get_categories(self, marketplace_repo):
        """Test getting all categories."""
        categories = await marketplace_repo.get_categories()
        
        assert len(categories) > 0
        category_names = [c["category"] for c in categories]
        assert "themes" in category_names
        assert "ai_models" in category_names

    async def test_purchase_item(self, marketplace_repo, test_user, test_db_pool):
        """Test purchasing a marketplace item."""
        # Get an item
        item = await marketplace_repo.get_item_by_slug("dark-mode-pro")
        
        result = await marketplace_repo.purchase_item(
            user_id=test_user["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        
        assert result["success"] is True
        assert "purchase_id" in result

    async def test_purchase_item_insufficient_credits(self, marketplace_repo, second_test_user):
        """Test purchase with insufficient credits."""
        item = await marketplace_repo.get_item_by_slug("neon-cyberpunk")  # 200 credits
        
        result = await marketplace_repo.purchase_item(
            user_id=second_test_user["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        
        assert result["success"] is False
        assert "Insufficient credits" in result["error"]

    async def test_purchase_item_already_purchased(self, marketplace_repo, test_user):
        """Test purchasing already owned item."""
        item = await marketplace_repo.get_item_by_slug("minimalist-white")
        
        # First purchase
        await marketplace_repo.purchase_item(
            user_id=test_user["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        
        # Try to purchase again
        result = await marketplace_repo.purchase_item(
            user_id=test_user["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        
        assert result["success"] is False
        assert "already purchased" in result["error"]

    async def test_get_user_purchases(self, marketplace_repo, test_user):
        """Test getting user's purchases."""
        # Make a purchase first
        item = await marketplace_repo.get_item_by_slug("ocean-breeze")
        await marketplace_repo.purchase_item(
            user_id=test_user["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        
        purchases = await marketplace_repo.get_user_purchases(test_user["id"])
        
        assert len(purchases) > 0

    async def test_has_purchased(self, marketplace_repo, test_user):
        """Test checking if user has purchased item."""
        item = await marketplace_repo.get_item_by_slug("sunset-gradient")
        
        # Before purchase
        assert await marketplace_repo.has_purchased(test_user["id"], item["id"]) is False
        
        # After purchase
        await marketplace_repo.purchase_item(
            user_id=test_user["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        
        assert await marketplace_repo.has_purchased(test_user["id"], item["id"]) is True


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestCreditsAPI:
    """Test credits API endpoints."""

    async def test_get_balance_endpoint(self, authenticated_client: AsyncClient):
        """Test GET /credits/balance endpoint."""
        response = await authenticated_client.get("/credits/balance")
        
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert "lifetime_earned" in data
        assert "can_claim_daily" in data

    async def test_get_packages_endpoint(self, api_client: AsyncClient):
        """Test GET /credits/packages endpoint."""
        response = await api_client.get("/credits/packages")
        
        assert response.status_code == 200
        packages = response.json()
        assert len(packages) > 0
        assert any(p["slug"] == "popular" for p in packages)

    async def test_get_services_endpoint(self, api_client: AsyncClient):
        """Test GET /credits/services endpoint."""
        response = await api_client.get("/credits/services")
        
        assert response.status_code == 200
        services = response.json()
        assert len(services) > 0

    async def test_get_transactions_endpoint(self, authenticated_client: AsyncClient):
        """Test GET /credits/transactions endpoint."""
        response = await authenticated_client.get("/credits/transactions")
        
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data

    async def test_get_achievements_endpoint(self, authenticated_client: AsyncClient):
        """Test GET /credits/achievements endpoint."""
        response = await authenticated_client.get("/credits/achievements")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_achievements" in data
        assert "achievements" in data

    async def test_get_leaderboard_endpoint(self, api_client: AsyncClient):
        """Test GET /credits/leaderboard endpoint."""
        response = await api_client.get("/credits/leaderboard")
        
        assert response.status_code == 200
        leaderboard = response.json()
        assert isinstance(leaderboard, list)


class TestMarketplaceAPI:
    """Test marketplace API endpoints."""

    async def test_get_items_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/items endpoint."""
        response = await api_client.get("/marketplace/items")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_get_items_with_category_filter(self, api_client: AsyncClient):
        """Test GET /marketplace/items with category filter."""
        response = await api_client.get("/marketplace/items?category=themes")
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["category"] == "themes" for item in data["items"])

    async def test_get_item_by_slug_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/items/{slug} endpoint."""
        response = await api_client.get("/marketplace/items/dark-mode-pro")
        
        assert response.status_code == 200
        item = response.json()
        assert item["name"] == "Dark Mode Pro"

    async def test_get_categories_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/categories endpoint."""
        response = await api_client.get("/marketplace/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    async def test_purchase_endpoint_unauthorized(self, api_client: AsyncClient):
        """Test POST /marketplace/purchase without auth."""
        response = await api_client.post("/marketplace/purchase", json={"item_id": 1})
        
        assert response.status_code == 401

    async def test_get_bundles_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/bundles endpoint."""
        response = await api_client.get("/marketplace/bundles")
        
        assert response.status_code == 200
        data = response.json()
        assert "bundles" in data


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    async def test_get_balance_nonexistent_user(self, credit_repo):
        """Test getting balance for non-existent user."""
        balance = await credit_repo.get_balance(999999999)
        
        # Should return default values
        assert float(balance["balance"]) == 0.0

    async def test_ensure_user_credits_exists(self, credit_repo, test_db_pool):
        """Test ensuring user_credits record exists."""
        new_user_id = 999999100
        
        # Create user without user_credits
        await test_db_pool.execute("""
            INSERT INTO users (id, username, status)
            VALUES ($1, 'temp_user', 'active')
            ON CONFLICT (id) DO NOTHING
        """, new_user_id)
        
        # Ensure record exists
        await credit_repo.ensure_user_credits_exists(new_user_id)
        
        # Verify record was created
        balance = await credit_repo.get_balance(new_user_id)
        assert balance is not None
        
        # Cleanup
        await test_db_pool.execute("DELETE FROM user_credits WHERE user_id = $1", new_user_id)
        await test_db_pool.execute("DELETE FROM users WHERE id = $1", new_user_id)

    async def test_concurrent_credit_operations(self, credit_repo, test_user):
        """Test concurrent credit operations don't cause race conditions."""
        import asyncio
        
        async def add_credits():
            await credit_repo.add_credits(
                user_id=test_user["id"],
                amount=Decimal("10"),
                transaction_type="bonus",
                category="test",
            )
        
        # Run multiple concurrent operations
        await asyncio.gather(*[add_credits() for _ in range(5)])
        
        # Check final balance is correct
        balance = await credit_repo.get_balance(test_user["id"])
        assert float(balance["balance"]) == 1050.0  # 1000 + (5 * 10)

    async def test_large_credit_amount(self, credit_repo, test_user):
        """Test handling large credit amounts."""
        large_amount = Decimal("999999999.99")
        
        transaction = await credit_repo.add_credits(
            user_id=test_user["id"],
            amount=large_amount,
            transaction_type="bonus",
            category="test",
        )
        
        assert transaction is not None
        assert float(transaction["amount"]) == float(large_amount)
