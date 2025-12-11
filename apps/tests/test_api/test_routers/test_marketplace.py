"""
Marketplace Integration Tests
=============================

Comprehensive tests for marketplace functionality including:
- Items listing and filtering
- Purchase flow
- Reviews system
- Bundle operations
- Gift functionality
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = [pytest.mark.integration, pytest.mark.api]


# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def marketplace_repo(test_db_pool):
    """Provide marketplace repository for testing."""
    from infra.db.repositories.marketplace_repository import MarketplaceRepository

    return MarketplaceRepository(test_db_pool)


@pytest_asyncio.fixture
async def test_buyer(test_db_pool):
    """Create a test user with credits for purchasing."""
    user_id = 999999011

    await test_db_pool.execute(
        """
        INSERT INTO users (id, username, email, status, credit_balance)
        VALUES ($1, 'marketplace_buyer', 'buyer@example.com', 'active', 5000)
        ON CONFLICT (id) DO UPDATE SET credit_balance = 5000
    """,
        user_id,
    )

    yield {"id": user_id, "username": "marketplace_buyer", "credit_balance": 5000}

    # Cleanup
    await test_db_pool.execute("DELETE FROM item_reviews WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM user_purchases WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest_asyncio.fixture
async def test_recipient(test_db_pool):
    """Create a test user to receive gifts."""
    user_id = 999999012

    await test_db_pool.execute(
        """
        INSERT INTO users (id, username, email, status, credit_balance)
        VALUES ($1, 'gift_recipient', 'recipient@example.com', 'active', 0)
        ON CONFLICT (id) DO UPDATE SET credit_balance = 0
    """,
        user_id,
    )

    yield {"id": user_id, "username": "gift_recipient"}

    # Cleanup
    await test_db_pool.execute("DELETE FROM user_purchases WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
    await test_db_pool.execute("DELETE FROM users WHERE id = $1", user_id)


# ============================================================================
# Items Tests
# ============================================================================


class TestMarketplaceItems:
    """Test marketplace item operations."""

    async def test_get_all_items(self, marketplace_repo):
        """Test getting all marketplace items."""
        items = await marketplace_repo.get_items()

        assert len(items) > 0
        # Verify structure
        item = items[0]
        assert "id" in item
        assert "name" in item
        assert "slug" in item
        assert "price_credits" in item
        assert "category" in item

    async def test_get_items_paginated(self, marketplace_repo):
        """Test paginated items retrieval."""
        first_page = await marketplace_repo.get_items(limit=3, offset=0)
        second_page = await marketplace_repo.get_items(limit=3, offset=3)

        assert len(first_page) <= 3
        # Ensure different items on different pages
        if len(second_page) > 0:
            first_ids = {i["id"] for i in first_page}
            second_ids = {i["id"] for i in second_page}
            assert first_ids.isdisjoint(second_ids)

    async def test_filter_by_category(self, marketplace_repo):
        """Test filtering items by category."""
        themes = await marketplace_repo.get_items(category="themes")
        ai_models = await marketplace_repo.get_items(category="ai_models")
        widgets = await marketplace_repo.get_items(category="widgets")

        assert all(i["category"] == "themes" for i in themes)
        assert all(i["category"] == "ai_models" for i in ai_models)
        assert all(i["category"] == "widgets" for i in widgets)

    async def test_filter_featured(self, marketplace_repo):
        """Test filtering featured items."""
        featured = await marketplace_repo.get_items(is_featured=True)

        assert len(featured) > 0
        assert all(i["is_featured"] for i in featured)

    async def test_filter_premium(self, marketplace_repo):
        """Test filtering premium items."""
        premium = await marketplace_repo.get_items(is_premium=True)

        assert all(i["is_premium"] for i in premium)

    async def test_search_items(self, marketplace_repo):
        """Test searching items by name/description."""
        results = await marketplace_repo.get_items(search="dark")

        assert len(results) > 0
        # At least one result should contain "dark" in name or description
        assert any(
            "dark" in i["name"].lower() or (i["description"] and "dark" in i["description"].lower())
            for i in results
        )

    async def test_get_item_by_id(self, marketplace_repo):
        """Test getting item by ID."""
        # First get any item
        items = await marketplace_repo.get_items(limit=1)
        item_id = items[0]["id"]

        item = await marketplace_repo.get_item_by_id(item_id)

        assert item is not None
        assert item["id"] == item_id

    async def test_get_item_by_slug(self, marketplace_repo):
        """Test getting item by slug."""
        item = await marketplace_repo.get_item_by_slug("neon-cyberpunk")

        assert item is not None
        assert item["name"] == "Neon Cyberpunk"
        assert item["price_credits"] == 200


# ============================================================================
# Purchase Flow Tests
# ============================================================================


class TestPurchaseFlow:
    """Test marketplace purchase flow."""

    async def test_successful_purchase(self, marketplace_repo, test_buyer, test_db_pool):
        """Test successful item purchase."""
        item = await marketplace_repo.get_item_by_slug("forest-green")  # 100 credits

        result = await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        assert result["success"] is True
        assert result["credits_spent"] == 100

        # Verify balance was deducted
        balance = await test_db_pool.fetchval(
            "SELECT credit_balance FROM users WHERE id = $1", test_buyer["id"]
        )
        assert balance == 4900  # 5000 - 100

    async def test_purchase_increments_download_count(self, marketplace_repo, test_buyer):
        """Test that purchase increments download count."""
        item_before = await marketplace_repo.get_item_by_slug("realtime-widget")
        download_count_before = item_before["download_count"]

        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item_before["id"],
            price=item_before["price_credits"],
        )

        item_after = await marketplace_repo.get_item_by_slug("realtime-widget")
        assert item_after["download_count"] == download_count_before + 1

    async def test_purchase_with_expiration(self, marketplace_repo, test_buyer):
        """Test purchase with expiration date."""
        from datetime import datetime, timedelta

        item = await marketplace_repo.get_item_by_slug("growth-heatmap")
        expires_at = datetime.utcnow() + timedelta(days=30)

        result = await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
            expires_at=expires_at,
        )

        assert result["success"] is True

    async def test_purchase_duplicate_fails(self, marketplace_repo, test_buyer):
        """Test that duplicate purchase fails."""
        item = await marketplace_repo.get_item_by_slug("scheduler-widget")

        # First purchase
        result1 = await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        assert result1["success"] is True

        # Second purchase should fail
        result2 = await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )
        assert result2["success"] is False
        assert "already purchased" in result2["error"]

    async def test_purchase_insufficient_balance(self, marketplace_repo, test_recipient):
        """Test purchase with insufficient balance."""
        item = await marketplace_repo.get_item_by_slug("advanced-sentiment")  # 500 credits

        result = await marketplace_repo.purchase_item(
            user_id=test_recipient["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        assert result["success"] is False
        assert "Insufficient" in result["error"]

    async def test_get_user_purchases(self, marketplace_repo, test_buyer):
        """Test getting user's purchase history."""
        # Make a purchase first
        item = await marketplace_repo.get_item_by_slug("notification-widget")
        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        purchases = await marketplace_repo.get_user_purchases(test_buyer["id"])

        assert len(purchases) > 0
        assert any(p["slug"] == "notification-widget" for p in purchases)

    async def test_has_purchased_check(self, marketplace_repo, test_buyer):
        """Test checking purchase ownership."""
        item = await marketplace_repo.get_item_by_slug("revenue-tracker")

        # Before purchase
        assert await marketplace_repo.has_purchased(test_buyer["id"], item["id"]) is False

        # After purchase
        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        assert await marketplace_repo.has_purchased(test_buyer["id"], item["id"]) is True


# ============================================================================
# Reviews Tests
# ============================================================================


class TestReviewSystem:
    """Test marketplace review system."""

    async def test_add_review(self, marketplace_repo, test_buyer):
        """Test adding a review."""
        # First purchase the item
        item = await marketplace_repo.get_item_by_slug("auto-reply")
        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        # Add review
        result = await marketplace_repo.add_review(
            user_id=test_buyer["id"],
            item_id=item["id"],
            rating=5,
            review_text="Excellent AI model!",
        )

        assert result is not None
        assert result["is_verified"] is True  # Verified purchase

    async def test_review_without_purchase(self, marketplace_repo, test_recipient):
        """Test review without purchase (unverified)."""
        item = await marketplace_repo.get_item_by_slug("audience-insights")

        result = await marketplace_repo.add_review(
            user_id=test_recipient["id"],
            item_id=item["id"],
            rating=4,
            review_text="Looks good!",
        )

        # Should still work but be unverified
        assert result["is_verified"] is False

    async def test_update_review(self, marketplace_repo, test_buyer):
        """Test updating an existing review."""
        item = await marketplace_repo.get_item_by_slug("content-optimizer")
        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        # Initial review
        await marketplace_repo.add_review(
            user_id=test_buyer["id"],
            item_id=item["id"],
            rating=3,
            review_text="Okay product",
        )

        # Update review
        result = await marketplace_repo.add_review(
            user_id=test_buyer["id"],
            item_id=item["id"],
            rating=5,
            review_text="Actually great after update!",
        )

        assert result is not None

    async def test_get_item_reviews(self, marketplace_repo, test_buyer):
        """Test getting reviews for an item."""
        item = await marketplace_repo.get_item_by_slug("viral-detector")
        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        await marketplace_repo.add_review(
            user_id=test_buyer["id"],
            item_id=item["id"],
            rating=5,
            review_text="Amazing product!",
        )

        reviews = await marketplace_repo.get_item_reviews(item["id"])

        assert len(reviews) > 0


# ============================================================================
# Bundle Tests
# ============================================================================


class TestBundles:
    """Test marketplace bundle operations."""

    async def test_get_bundles(self, marketplace_repo):
        """Test getting all bundles."""
        bundles = await marketplace_repo.get_bundles()

        assert len(bundles) > 0
        # Verify seeded bundles
        slugs = [b["slug"] for b in bundles]
        assert "ultimate-bundle" in slugs
        assert "pro-analytics" in slugs

    async def test_get_bundle_by_slug(self, marketplace_repo):
        """Test getting bundle by slug."""
        bundle = await marketplace_repo.get_bundle_by_slug("starter-bundle")

        assert bundle is not None
        assert bundle["discount_percent"] == 24

    async def test_get_bundle_items(self, marketplace_repo):
        """Test getting items in a bundle."""
        bundle = await marketplace_repo.get_bundle_by_slug("theme-collection")
        items = await marketplace_repo.get_bundle_items(bundle["id"])

        assert len(items) > 0
        # All items should be themes
        assert all(i["category"] == "themes" for i in items)

    async def test_purchase_bundle(self, marketplace_repo, test_buyer):
        """Test purchasing a bundle."""
        bundle = await marketplace_repo.get_bundle_by_slug("starter-bundle")

        result = await marketplace_repo.purchase_bundle(
            user_id=test_buyer["id"],
            bundle_id=bundle["id"],
        )

        assert result["success"] is True
        # Should grant all items in bundle
        bundle_items = await marketplace_repo.get_bundle_items(bundle["id"])
        for item in bundle_items:
            assert await marketplace_repo.has_purchased(test_buyer["id"], item["id"]) is True


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestMarketplaceAPI:
    """Test marketplace API endpoints."""

    async def test_get_items_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/items."""
        response = await api_client.get("/marketplace/items")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    async def test_get_items_with_filters(self, api_client: AsyncClient):
        """Test GET /marketplace/items with query params."""
        response = await api_client.get(
            "/marketplace/items",
            params={
                "category": "themes",
                "is_featured": True,
                "limit": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert all(i["category"] == "themes" for i in data["items"])

    async def test_get_item_detail(self, api_client: AsyncClient):
        """Test GET /marketplace/items/{slug}."""
        response = await api_client.get("/marketplace/items/dark-mode-pro")

        assert response.status_code == 200
        item = response.json()
        assert item["slug"] == "dark-mode-pro"

    async def test_get_item_not_found(self, api_client: AsyncClient):
        """Test GET /marketplace/items/{slug} with invalid slug."""
        response = await api_client.get("/marketplace/items/non-existent")

        assert response.status_code == 404

    async def test_get_categories(self, api_client: AsyncClient):
        """Test GET /marketplace/categories."""
        response = await api_client.get("/marketplace/categories")

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    async def test_purchase_requires_auth(self, api_client: AsyncClient):
        """Test POST /marketplace/purchase requires authentication."""
        response = await api_client.post("/marketplace/purchase", json={"item_id": 1})

        assert response.status_code == 401

    async def test_get_bundles_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/bundles."""
        response = await api_client.get("/marketplace/bundles")

        assert response.status_code == 200
        data = response.json()
        assert "bundles" in data

    async def test_get_reviews_endpoint(self, api_client: AsyncClient):
        """Test GET /marketplace/reviews/{item_id}."""
        # First get an item ID
        items_response = await api_client.get("/marketplace/items?limit=1")
        item = items_response.json()["items"][0]

        response = await api_client.get(f"/marketplace/reviews/{item['id']}")

        assert response.status_code == 200


# ============================================================================
# Edge Cases
# ============================================================================


class TestMarketplaceEdgeCases:
    """Test edge cases and error handling."""

    async def test_empty_search_results(self, marketplace_repo):
        """Test search with no matches."""
        results = await marketplace_repo.get_items(search="xyznonexistent123")

        assert results == []

    async def test_invalid_category_filter(self, marketplace_repo):
        """Test filtering by non-existent category."""
        results = await marketplace_repo.get_items(category="invalid_category")

        assert results == []

    async def test_get_items_large_offset(self, marketplace_repo):
        """Test getting items with offset beyond total count."""
        results = await marketplace_repo.get_items(offset=99999)

        assert results == []

    async def test_review_rating_bounds(self, marketplace_repo, test_buyer, test_db_pool):
        """Test review rating validation (1-5)."""
        item = await marketplace_repo.get_item_by_slug("engagement-predictor")
        await marketplace_repo.purchase_item(
            user_id=test_buyer["id"],
            item_id=item["id"],
            price=item["price_credits"],
        )

        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            result = await marketplace_repo.add_review(
                user_id=test_buyer["id"],
                item_id=item["id"],
                rating=rating,
            )
            assert result is not None
