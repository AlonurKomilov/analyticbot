"""
Marketplace Services Repository
================================

Database repository for marketplace services (subscriptions):
- Bot services (anti-spam, auto-delete, etc.)
- MTProto services (history access, bulk export, etc.)
- AI services

This repository handles CRUD operations for subscription-based services.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict

import asyncpg

logger = logging.getLogger(__name__)


class MarketplaceServiceRepository:
    """Repository for marketplace services operations"""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    # ============================================
    # SERVICE CATALOG OPERATIONS
    # ============================================

    async def get_all_services(
        self, 
        include_inactive: bool = False, 
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all marketplace services.
        
        Args:
            include_inactive: Include inactive services
            category: Filter by category
            
        Returns:
            List of service records
        """
        query = """
            SELECT 
                id, service_key, name, description, short_description,
                price_credits_monthly, price_credits_yearly,
                category, subcategory, features,
                usage_quota_daily, usage_quota_monthly, rate_limit_per_minute,
                requires_bot, requires_mtproto, min_tier,
                icon, color, is_featured, is_popular, is_new, sort_order,
                is_active, is_beta, documentation_url, demo_video_url, metadata,
                active_subscriptions, total_subscriptions,
                created_at, updated_at
            FROM marketplace_services
            WHERE 1=1
        """

        conditions = []
        params = []
        param_counter = 1

        if not include_inactive:
            conditions.append("is_active = true")

        if category:
            conditions.append(f"category = ${param_counter}")
            params.append(category)
            param_counter += 1

        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += " ORDER BY sort_order, name"

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_service_by_key(self, service_key: str) -> Optional[Dict]:
        """Get service by service_key"""
        query = """
            SELECT * FROM marketplace_services
            WHERE service_key = $1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, service_key)
            return dict(row) if row else None

    async def get_service_by_id(self, service_id: int) -> Optional[Dict]:
        """Get service by ID"""
        query = """
            SELECT * FROM marketplace_services
            WHERE id = $1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, service_id)
            return dict(row) if row else None

    async def get_featured_services(self, limit: int = 5) -> List[Dict]:
        """Get featured services"""
        query = """
            SELECT * FROM marketplace_services
            WHERE is_active = true AND is_featured = true
            ORDER BY sort_order, name
            LIMIT $1
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, limit)
            return [dict(row) for row in rows]

    # ============================================
    # USER SUBSCRIPTION OPERATIONS
    # ============================================

    async def create_subscription(
        self,
        user_id: int,
        service_id: int,
        billing_cycle: str,
        price_paid: int,
        expires_at: datetime,
        auto_renew: bool = True,
    ) -> Dict:
        """
        Create a new service subscription for a user.
        
        Args:
            user_id: User ID
            service_id: Service ID
            billing_cycle: 'monthly' or 'yearly'
            price_paid: Credits paid
            expires_at: Subscription expiration date
            auto_renew: Auto-renew on expiry
            
        Returns:
            Created subscription record
        """
        query = """
            INSERT INTO user_service_subscriptions (
                user_id, service_id, billing_cycle, price_paid,
                status, expires_at, auto_renew
            )
            VALUES ($1, $2, $3, $4, 'active', $5, $6)
            RETURNING *
        """

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Create subscription
                row = await conn.fetchrow(
                    query,
                    user_id,
                    service_id,
                    billing_cycle,
                    price_paid,
                    expires_at,
                    auto_renew,
                )

                # Increment service counters
                await conn.execute(
                    """
                    UPDATE marketplace_services
                    SET active_subscriptions = active_subscriptions + 1,
                        total_subscriptions = total_subscriptions + 1,
                        updated_at = NOW()
                    WHERE id = $1
                """,
                    service_id,
                )

                logger.info(
                    f"Created subscription: user={user_id}, service={service_id}, "
                    f"cycle={billing_cycle}, expires={expires_at}"
                )
                return dict(row)

    async def get_user_subscriptions(
        self,
        user_id: int,
        status: Optional[str] = None,
        include_expired: bool = False,
    ) -> List[Dict]:
        """
        Get user's service subscriptions.
        
        Args:
            user_id: User ID
            status: Filter by status ('active', 'paused', 'cancelled', 'expired')
            include_expired: Include expired subscriptions
            
        Returns:
            List of subscription records with service details
        """
        query = """
            SELECT 
                s.*,
                ms.service_key, ms.name as service_name,
                ms.description as service_description,
                ms.icon, ms.color, ms.category,
                ms.usage_quota_daily, ms.usage_quota_monthly,
                ms.rate_limit_per_minute
            FROM user_service_subscriptions s
            JOIN marketplace_services ms ON s.service_id = ms.id
            WHERE s.user_id = $1
        """

        conditions = []
        params = [user_id]
        param_counter = 2

        if status:
            conditions.append(f"s.status = ${param_counter}")
            params.append(status)
            param_counter += 1

        if not include_expired:
            conditions.append("s.expires_at > NOW()")

        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += " ORDER BY s.created_at DESC"

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    async def get_user_active_services(self, user_id: int) -> List[str]:
        """
        Get list of service keys user has active subscriptions to.
        Used for feature gating.
        
        Returns:
            List of service_key strings
        """
        query = """
            SELECT ms.service_key
            FROM user_service_subscriptions s
            JOIN marketplace_services ms ON s.service_id = ms.id
            WHERE s.user_id = $1
            AND s.status = 'active'
            AND s.expires_at > NOW()
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return [row["service_key"] for row in rows]

    async def check_user_has_service(
        self, user_id: int, service_key: str
    ) -> Optional[Dict]:
        """
        Check if user has an active subscription to a service.
        
        Returns:
            Subscription record if active, None otherwise
        """
        query = """
            SELECT s.*
            FROM user_service_subscriptions s
            JOIN marketplace_services ms ON s.service_id = ms.id
            WHERE s.user_id = $1
            AND ms.service_key = $2
            AND s.status = 'active'
            AND s.expires_at > NOW()
            LIMIT 1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, service_key)
            return dict(row) if row else None

    async def cancel_subscription(
        self, subscription_id: int, reason: Optional[str] = None
    ) -> Optional[Dict]:
        """Cancel a subscription"""
        query = """
            UPDATE user_service_subscriptions
            SET status = 'cancelled',
                cancelled_at = NOW(),
                cancellation_reason = $2,
                auto_renew = false,
                updated_at = NOW()
            WHERE id = $1
            RETURNING *
        """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(query, subscription_id, reason)

                if row:
                    # Decrement active subscriptions counter
                    await conn.execute(
                        """
                        UPDATE marketplace_services
                        SET active_subscriptions = GREATEST(active_subscriptions - 1, 0),
                            updated_at = NOW()
                        WHERE id = $1
                    """,
                        row["service_id"],
                    )

                    logger.info(f"Cancelled subscription: id={subscription_id}, reason={reason}")

                return dict(row) if row else None

    async def renew_subscription(
        self, subscription_id: int, new_expires_at: datetime, price_paid: int
    ) -> Optional[Dict]:
        """Renew a subscription"""
        query = """
            UPDATE user_service_subscriptions
            SET expires_at = $2,
                last_renewed_at = NOW(),
                renewal_attempts = renewal_attempts + 1,
                last_renewal_attempt = NOW(),
                status = 'active',
                updated_at = NOW()
            WHERE id = $1
            RETURNING *
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, subscription_id, new_expires_at)
            if row:
                logger.info(
                    f"Renewed subscription: id={subscription_id}, "
                    f"new_expiry={new_expires_at}, paid={price_paid}"
                )
            return dict(row) if row else None

    async def get_expiring_subscriptions(self, days_ahead: int = 3) -> List[Dict]:
        """
        Get subscriptions expiring within N days (for renewal processing).
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of subscriptions about to expire
        """
        query = """
            SELECT s.*, u.credit_balance, ms.price_credits_monthly, ms.price_credits_yearly
            FROM user_service_subscriptions s
            JOIN users u ON s.user_id = u.id
            JOIN marketplace_services ms ON s.service_id = ms.id
            WHERE s.status = 'active'
            AND s.auto_renew = true
            AND s.expires_at BETWEEN NOW() AND NOW() + INTERVAL '%s days'
            ORDER BY s.expires_at
        """ % days_ahead

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]

    # ============================================
    # USAGE TRACKING
    # ============================================

    async def log_service_usage(
        self,
        subscription_id: int,
        user_id: int,
        service_id: int,
        action: str,
        resource_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Log a service usage event"""
        query = """
            INSERT INTO service_usage_log (
                subscription_id, user_id, service_id, action,
                resource_id, success, error_message,
                response_time_ms, metadata
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, created_at
        """

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                subscription_id,
                user_id,
                service_id,
                action,
                resource_id,
                success,
                error_message,
                response_time_ms,
                metadata,
            )
            return dict(row)

    async def increment_subscription_usage(
        self, subscription_id: int, count: int = 1
    ) -> None:
        """Increment daily and monthly usage counters for a subscription"""
        query = """
            UPDATE user_service_subscriptions
            SET usage_count_daily = usage_count_daily + $2,
                usage_count_monthly = usage_count_monthly + $2,
                updated_at = NOW()
            WHERE id = $1
        """
        async with self._pool.acquire() as conn:
            await conn.execute(query, subscription_id, count)

    async def get_subscription_usage(
        self,
        subscription_id: int,
        days: int = 30,
    ) -> Dict:
        """
        Get usage statistics for a subscription.
        
        Returns:
            Dict with usage counts, success rate, etc.
        """
        query = """
            SELECT 
                COUNT(*) as total_uses,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_uses,
                COUNT(DISTINCT DATE(created_at)) as days_used,
                AVG(response_time_ms) as avg_response_time_ms
            FROM service_usage_log
            WHERE subscription_id = $1
            AND created_at >= NOW() - INTERVAL '%s days'
        """ % days

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, subscription_id)
            return dict(row) if row else {}

    async def get_user_usage_today(
        self, user_id: int, service_id: int
    ) -> int:
        """Get user's usage count for a service today"""
        query = """
            SELECT COUNT(*) as count
            FROM service_usage_log
            WHERE user_id = $1
            AND service_id = $2
            AND created_at >= CURRENT_DATE
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id, service_id)
            return row["count"] if row else 0

    async def reset_daily_usage_counters(self) -> int:
        """
        Reset daily usage counters for all subscriptions.
        Should be run once per day via scheduled job.
        
        Returns:
            Number of subscriptions reset
        """
        query = """
            UPDATE user_service_subscriptions
            SET usage_count_daily = 0,
                usage_reset_daily = NOW()
            WHERE usage_count_daily > 0
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute(query)
            count = int(result.split()[-1])
            logger.info(f"Reset daily usage counters for {count} subscriptions")
            return count

    async def reset_monthly_usage_counters(self) -> int:
        """
        Reset monthly usage counters for all subscriptions.
        Should be run once per month via scheduled job.
        
        Returns:
            Number of subscriptions reset
        """
        query = """
            UPDATE user_service_subscriptions
            SET usage_count_monthly = 0,
                usage_reset_monthly = NOW()
            WHERE usage_count_monthly > 0
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute(query)
            count = int(result.split()[-1])
            logger.info(f"Reset monthly usage counters for {count} subscriptions")
            return count

    # ============================================
    # ADMIN / STATISTICS
    # ============================================

    async def get_service_statistics(self, service_id: int) -> Dict:
        """Get detailed statistics for a service"""
        query = """
            SELECT 
                COUNT(DISTINCT s.user_id) as unique_subscribers,
                COUNT(*) as total_subscriptions,
                SUM(CASE WHEN s.status = 'active' AND s.expires_at > NOW() THEN 1 ELSE 0 END) as active_subscriptions,
                SUM(s.price_paid) as total_revenue,
                AVG(EXTRACT(EPOCH FROM (s.expires_at - s.started_at)) / 86400) as avg_subscription_days
            FROM user_service_subscriptions s
            WHERE s.service_id = $1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, service_id)
            return dict(row) if row else {}

    async def get_user_total_spending(self, user_id: int) -> int:
        """Get total credits user has spent on marketplace services"""
        query = """
            SELECT COALESCE(SUM(price_paid), 0) as total_spent
            FROM user_service_subscriptions
            WHERE user_id = $1
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            return row["total_spent"] if row else 0
