"""
🏪 Marketplace Repository
Handles all marketplace operations - items, purchases, reviews, gifts, bundles.
"""

import json
from datetime import datetime, timedelta
from typing import Any

import asyncpg


class MarketplaceRepository:
    """Repository for marketplace operations."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize with database pool."""
        self.pool = pool

    # ==================== ITEMS ====================

    async def get_items(
        self,
        category: str | None = None,
        subcategory: str | None = None,
        is_featured: bool | None = None,
        is_premium: bool | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get marketplace items with filters."""

        conditions = ["is_active = TRUE"]
        params = []
        param_idx = 1

        if category:
            conditions.append(f"category = ${param_idx}")
            params.append(category)
            param_idx += 1

        if subcategory:
            conditions.append(f"subcategory = ${param_idx}")
            params.append(subcategory)
            param_idx += 1

        if is_featured is not None:
            conditions.append(f"is_featured = ${param_idx}")
            params.append(is_featured)
            param_idx += 1

        if is_premium is not None:
            conditions.append(f"is_premium = ${param_idx}")
            params.append(is_premium)
            param_idx += 1

        if search:
            conditions.append(f"(name ILIKE ${param_idx} OR description ILIKE ${param_idx})")
            params.append(f"%{search}%")
            param_idx += 1

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        query = f"""
            SELECT id, name, slug, description, category, subcategory,
                   price_credits, is_premium, is_featured, preview_url, icon_url,
                   metadata, download_count, rating, rating_count, created_at
            FROM marketplace_items
            WHERE {where_clause}
            ORDER BY is_featured DESC, rating DESC, download_count DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_item_by_slug(self, slug: str) -> dict[str, Any] | None:
        """Get a single marketplace item by slug."""

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, name, slug, description, category, subcategory,
                       price_credits, is_premium, is_featured, preview_url, icon_url,
                       metadata, download_count, rating, rating_count, created_at
                FROM marketplace_items
                WHERE slug = $1 AND is_active = TRUE
            """,
                slug,
            )
            return dict(row) if row else None

    async def get_item_by_id(self, item_id: int) -> dict[str, Any] | None:
        """Get a single marketplace item by ID."""

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, name, slug, description, category, subcategory,
                       price_credits, is_premium, is_featured, preview_url, icon_url,
                       metadata, download_count, rating, rating_count, created_at
                FROM marketplace_items
                WHERE id = $1 AND is_active = TRUE
            """,
                item_id,
            )
            return dict(row) if row else None

    async def get_categories(self) -> list[dict[str, Any]]:
        """Get all unique categories with item counts."""

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT category, COUNT(*) as item_count
                FROM marketplace_items
                WHERE is_active = TRUE
                GROUP BY category
                ORDER BY item_count DESC
            """
            )
            return [dict(row) for row in rows]

    # ==================== PURCHASES ====================

    async def purchase_item(
        self, user_id: int, item_id: int, price: int, expires_at: datetime | None = None
    ) -> dict[str, Any]:
        """Purchase a marketplace item."""

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Check if already purchased
                existing = await conn.fetchrow(
                    """
                    SELECT id FROM user_purchases
                    WHERE user_id = $1 AND item_id = $2 AND is_active = TRUE
                """,
                    user_id,
                    item_id,
                )

                if existing:
                    return {"success": False, "error": "Item already purchased"}

                # Check user balance
                balance = await conn.fetchval(
                    """
                    SELECT credit_balance FROM users WHERE id = $1
                """,
                    user_id,
                )

                if balance is None or balance < price:
                    return {"success": False, "error": "Insufficient credits"}

                # Deduct credits
                await conn.execute(
                    """
                    UPDATE users SET credit_balance = credit_balance - $1
                    WHERE id = $2
                """,
                    price,
                    user_id,
                )

                # Record transaction
                await conn.execute(
                    """
                    INSERT INTO credit_transactions (user_id, amount, transaction_type, description)
                    VALUES ($1, $2, 'spend', $3)
                """,
                    user_id,
                    -price,
                    f"Marketplace purchase: item #{item_id}",
                )

                # Create purchase record
                purchase_id = await conn.fetchval(
                    """
                    INSERT INTO user_purchases (user_id, item_id, price_paid, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """,
                    user_id,
                    item_id,
                    price,
                    expires_at,
                )

                # Increment download count
                await conn.execute(
                    """
                    UPDATE marketplace_items SET download_count = download_count + 1
                    WHERE id = $1
                """,
                    item_id,
                )

                return {
                    "success": True,
                    "purchase_id": purchase_id,
                    "credits_spent": price,
                }

    async def get_user_purchases(self, user_id: int) -> list[dict[str, Any]]:
        """Get all purchases for a user."""

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT up.id, up.price_paid, up.purchased_at, up.expires_at, up.is_active,
                       mi.id as item_id, mi.name, mi.slug, mi.category, mi.subcategory,
                       mi.icon_url, mi.metadata
                FROM user_purchases up
                JOIN marketplace_items mi ON up.item_id = mi.id
                WHERE up.user_id = $1
                ORDER BY up.purchased_at DESC
            """,
                user_id,
            )
            return [dict(row) for row in rows]

    async def has_purchased(self, user_id: int, item_id: int) -> bool:
        """Check if user has purchased an item."""

        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1 FROM user_purchases
                    WHERE user_id = $1 AND item_id = $2 AND is_active = TRUE
                    AND (expires_at IS NULL OR expires_at > NOW())
                )
            """,
                user_id,
                item_id,
            )
            return result

    # ==================== REVIEWS ====================

    async def add_review(
        self, user_id: int, item_id: int, rating: int, review_text: str | None = None
    ) -> dict[str, Any]:
        """Add or update a review for an item."""

        async with self.pool.acquire() as conn:
            # Check if verified purchase
            is_verified = await self.has_purchased(user_id, item_id)

            # Upsert review
            await conn.execute(
                """
                INSERT INTO item_reviews (user_id, item_id, rating, review_text, is_verified_purchase)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id, item_id)
                DO UPDATE SET rating = $3, review_text = $4, updated_at = NOW()
            """,
                user_id,
                item_id,
                rating,
                review_text,
                is_verified,
            )

            # Update item rating
            await conn.execute(
                """
                UPDATE marketplace_items
                SET rating = (
                    SELECT AVG(rating)::DECIMAL(3,2) FROM item_reviews WHERE item_id = $1
                ),
                rating_count = (
                    SELECT COUNT(*) FROM item_reviews WHERE item_id = $1
                )
                WHERE id = $1
            """,
                item_id,
            )

            return {"success": True, "is_verified": is_verified}

    async def get_item_reviews(
        self, item_id: int, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get reviews for an item."""

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT ir.id, ir.rating, ir.review_text, ir.is_verified_purchase,
                       ir.created_at, u.username, u.full_name
                FROM item_reviews ir
                JOIN users u ON ir.user_id = u.id
                WHERE ir.item_id = $1
                ORDER BY ir.is_verified_purchase DESC, ir.created_at DESC
                LIMIT $2 OFFSET $3
            """,
                item_id,
                limit,
                offset,
            )
            return [dict(row) for row in rows]

    # ==================== CREDIT GIFTING ====================

    async def send_gift(
        self,
        sender_id: int,
        recipient_username: str,
        amount: int,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Send credits as a gift to another user."""

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Find recipient
                recipient = await conn.fetchrow(
                    """
                    SELECT id, username FROM users WHERE username = $1
                """,
                    recipient_username,
                )

                if not recipient:
                    return {"success": False, "error": "User not found"}

                if recipient["id"] == sender_id:
                    return {
                        "success": False,
                        "error": "Cannot send credits to yourself",
                    }

                # Check sender balance
                balance = await conn.fetchval(
                    """
                    SELECT credit_balance FROM users WHERE id = $1
                """,
                    sender_id,
                )

                if balance is None or balance < amount:
                    return {"success": False, "error": "Insufficient credits"}

                # Deduct from sender
                await conn.execute(
                    """
                    UPDATE users SET credit_balance = credit_balance - $1
                    WHERE id = $2
                """,
                    amount,
                    sender_id,
                )

                # Add to recipient
                await conn.execute(
                    """
                    UPDATE users SET credit_balance = credit_balance + $1
                    WHERE id = $2
                """,
                    amount,
                    recipient["id"],
                )

                # Record gift
                gift_id = await conn.fetchval(
                    """
                    INSERT INTO credit_gifts (sender_id, recipient_id, amount, message)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """,
                    sender_id,
                    recipient["id"],
                    amount,
                    message,
                )

                # Record transactions
                await conn.execute(
                    """
                    INSERT INTO credit_transactions (user_id, amount, transaction_type, description)
                    VALUES ($1, $2, 'gift_sent', $3)
                """,
                    sender_id,
                    -amount,
                    f"Gift to @{recipient_username}",
                )

                await conn.execute(
                    """
                    INSERT INTO credit_transactions (user_id, amount, transaction_type, description)
                    VALUES ($1, $2, 'gift_received', $3)
                """,
                    recipient["id"],
                    amount,
                    f"Gift from user #{sender_id}",
                )

                return {
                    "success": True,
                    "gift_id": gift_id,
                    "recipient": recipient_username,
                    "amount": amount,
                }

    async def get_gift_history(self, user_id: int, direction: str = "all") -> list[dict[str, Any]]:
        """Get gift history for a user."""

        async with self.pool.acquire() as conn:
            if direction == "sent":
                condition = "cg.sender_id = $1"
            elif direction == "received":
                condition = "cg.recipient_id = $1"
            else:
                condition = "(cg.sender_id = $1 OR cg.recipient_id = $1)"

            rows = await conn.fetch(
                f"""
                SELECT cg.id, cg.amount, cg.message, cg.created_at,
                       cg.sender_id, cg.recipient_id,
                       s.username as sender_username,
                       r.username as recipient_username,
                       CASE WHEN cg.sender_id = $1 THEN 'sent' ELSE 'received' END as direction
                FROM credit_gifts cg
                JOIN users s ON cg.sender_id = s.id
                JOIN users r ON cg.recipient_id = r.id
                WHERE {condition}
                ORDER BY cg.created_at DESC
                LIMIT 50
            """,
                user_id,
            )
            return [dict(row) for row in rows]

    # ==================== BUNDLES ====================

    async def get_bundles(self, featured_only: bool = False) -> list[dict[str, Any]]:
        """Get available service bundles."""

        async with self.pool.acquire() as conn:
            condition = "is_active = TRUE"
            if featured_only:
                condition += " AND is_featured = TRUE"

            rows = await conn.fetch(
                f"""
                SELECT id, name, slug, description, price_credits, original_price,
                       discount_percent, is_featured, valid_days
                FROM service_bundles
                WHERE {condition}
                ORDER BY is_featured DESC, discount_percent DESC
            """
            )
            return [dict(row) for row in rows]

    async def get_bundle_items(self, bundle_id: int) -> list[dict[str, Any]]:
        """Get services included in a bundle."""

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT bi.quantity, cs.id as service_id, cs.name, cs.description,
                       cs.credit_cost, cs.category
                FROM bundle_items bi
                JOIN credit_services cs ON bi.service_id = cs.id
                WHERE bi.bundle_id = $1
            """,
                bundle_id,
            )
            return [dict(row) for row in rows]

    async def purchase_bundle(self, user_id: int, bundle_id: int) -> dict[str, Any]:
        """Purchase a service bundle."""

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Get bundle details
                bundle = await conn.fetchrow(
                    """
                    SELECT id, name, price_credits, valid_days
                    FROM service_bundles
                    WHERE id = $1 AND is_active = TRUE
                """,
                    bundle_id,
                )

                if not bundle:
                    return {"success": False, "error": "Bundle not found"}

                # Check balance
                balance = await conn.fetchval(
                    """
                    SELECT credit_balance FROM users WHERE id = $1
                """,
                    user_id,
                )

                if balance is None or balance < bundle["price_credits"]:
                    return {"success": False, "error": "Insufficient credits"}

                # Deduct credits
                await conn.execute(
                    """
                    UPDATE users SET credit_balance = credit_balance - $1
                    WHERE id = $2
                """,
                    bundle["price_credits"],
                    user_id,
                )

                # Record transaction
                await conn.execute(
                    """
                    INSERT INTO credit_transactions (user_id, amount, transaction_type, description)
                    VALUES ($1, $2, 'spend', $3)
                """,
                    user_id,
                    -bundle["price_credits"],
                    f"Bundle purchase: {bundle['name']}",
                )

                # Get bundle items for remaining uses
                items = await conn.fetch(
                    """
                    SELECT service_id, quantity FROM bundle_items WHERE bundle_id = $1
                """,
                    bundle_id,
                )

                remaining_uses = {str(row["service_id"]): row["quantity"] for row in items}

                # Create user bundle
                expires_at = datetime.now() + timedelta(days=bundle["valid_days"])
                user_bundle_id = await conn.fetchval(
                    """
                    INSERT INTO user_bundles (user_id, bundle_id, price_paid, expires_at, remaining_uses)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """,
                    user_id,
                    bundle_id,
                    bundle["price_credits"],
                    expires_at,
                    json.dumps(remaining_uses),
                )

                return {
                    "success": True,
                    "user_bundle_id": user_bundle_id,
                    "bundle_name": bundle["name"],
                    "expires_at": expires_at.isoformat(),
                    "credits_spent": bundle["price_credits"],
                }

    async def get_user_bundles(self, user_id: int) -> list[dict[str, Any]]:
        """Get user's purchased bundles."""

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT ub.id, ub.price_paid, ub.purchased_at, ub.expires_at,
                       ub.remaining_uses, ub.is_active,
                       sb.name, sb.slug, sb.description
                FROM user_bundles ub
                JOIN service_bundles sb ON ub.bundle_id = sb.id
                WHERE ub.user_id = $1
                ORDER BY ub.purchased_at DESC
            """,
                user_id,
            )
            return [dict(row) for row in rows]
