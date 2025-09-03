"""
Payment Repository Implementation
Concrete implementation for payment-related data operations
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import asyncpg


class AsyncpgPaymentRepository:
    """Payment repository implementation using asyncpg"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_payment_method(
        self,
        user_id: int,
        provider: str,
        provider_method_id: str,
        method_type: str,
        last_four: str | None = None,
        brand: str | None = None,
        expires_at: datetime | None = None,
        is_default: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new payment method"""
        method_id = str(uuid4())
        async with self.pool.acquire() as conn:
            if is_default:
                await conn.execute(
                    "UPDATE payment_methods SET is_default = false WHERE user_id = $1", user_id
                )
            await conn.execute(
                """
                INSERT INTO payment_methods
                (id, user_id, provider, provider_method_id, method_type,
                 last_four, brand, expires_at, is_default, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                method_id,
                user_id,
                provider,
                provider_method_id,
                method_type,
                last_four,
                brand,
                expires_at,
                is_default,
                metadata,
            )
        return method_id

    async def get_user_payment_methods(self, user_id: int) -> list[dict[str, Any]]:
        """Get all active payment methods for a user"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM payment_methods
                WHERE user_id = $1 AND is_active = true
                ORDER BY is_default DESC, created_at DESC
                """,
                user_id,
            )
            return [dict(row) for row in rows]

    async def get_payment_method(self, method_id: str) -> dict[str, Any] | None:
        """Get payment method by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM payment_methods WHERE id = $1", method_id)
            return dict(row) if row else None

    async def delete_payment_method(self, method_id: str) -> bool:
        """Soft delete payment method"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE payment_methods SET is_active = false WHERE id = $1", method_id
            )
            return result != "UPDATE 0"

    async def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        payment_method_id: str | None,
        provider_subscription_id: str | None,
        billing_cycle: str,
        amount: Decimal,
        currency: str,
        current_period_start: datetime,
        current_period_end: datetime,
        trial_ends_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new subscription"""
        subscription_id = str(uuid4())
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE subscriptions
                SET status = 'canceled', canceled_at = now()
                WHERE user_id = $1 AND status = 'active'
                """,
                user_id,
            )
            await conn.execute(
                """
                INSERT INTO subscriptions
                (id, user_id, plan_id, payment_method_id, provider_subscription_id,
                 status, billing_cycle, amount, currency, current_period_start,
                 current_period_end, trial_ends_at, metadata)
                VALUES ($1, $2, $3, $4, $5, 'active', $6, $7, $8, $9, $10, $11, $12)
                """,
                subscription_id,
                user_id,
                plan_id,
                payment_method_id,
                provider_subscription_id,
                billing_cycle,
                amount,
                currency,
                current_period_start,
                current_period_end,
                trial_ends_at,
                metadata,
            )
        return subscription_id

    async def get_user_active_subscription(self, user_id: int) -> dict[str, Any] | None:
        """Get user's active subscription with plan details"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT s.*, p.name as plan_name, p.max_channels, p.max_posts_per_month
                FROM subscriptions s
                JOIN plans p ON s.plan_id = p.id
                WHERE s.user_id = $1 AND s.status = 'active'
                ORDER BY s.created_at DESC
                LIMIT 1
                """,
                user_id,
            )
            return dict(row) if row else None

    async def update_subscription_status(
        self, subscription_id: str, status: str, canceled_at: datetime | None = None
    ) -> bool:
        """Update subscription status"""
        async with self.pool.acquire() as conn:
            if canceled_at:
                result = await conn.execute(
                    """
                    UPDATE subscriptions
                    SET status = $1, canceled_at = $2, updated_at = now()
                    WHERE id = $3
                    """,
                    status,
                    canceled_at,
                    subscription_id,
                )
            else:
                result = await conn.execute(
                    """
                    UPDATE subscriptions
                    SET status = $1, updated_at = now()
                    WHERE id = $2
                    """,
                    status,
                    subscription_id,
                )
            return result != "UPDATE 0"

    async def extend_subscription(self, subscription_id: str, new_period_end: datetime) -> bool:
        """Extend subscription period"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE subscriptions
                SET current_period_end = $1, updated_at = now()
                WHERE id = $2
                """,
                new_period_end,
                subscription_id,
            )
            return result != "UPDATE 0"

    async def create_payment(
        self,
        user_id: int,
        subscription_id: str | None,
        payment_method_id: str | None,
        provider: str,
        provider_payment_id: str | None,
        idempotency_key: str,
        amount: Decimal,
        currency: str,
        status: str = "pending",
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new payment record"""
        payment_id = str(uuid4())
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO payments
                (id, user_id, subscription_id, payment_method_id, provider,
                 provider_payment_id, idempotency_key, amount, currency,
                 status, description, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                payment_id,
                user_id,
                subscription_id,
                payment_method_id,
                provider,
                provider_payment_id,
                idempotency_key,
                amount,
                currency,
                status,
                description,
                metadata,
            )
        return payment_id

    async def update_payment_status(
        self,
        payment_id: str,
        status: str,
        provider_payment_id: str | None = None,
        failure_code: str | None = None,
        failure_message: str | None = None,
        webhook_verified: bool = False,
    ) -> bool:
        """Update payment status and details"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE payments
                SET status = $1, provider_payment_id = COALESCE($2, provider_payment_id),
                    failure_code = $3, failure_message = $4, webhook_verified = $5,
                    processed_at = CASE WHEN $1 IN ('succeeded', 'failed')
                                   THEN now() ELSE processed_at END,
                    updated_at = now()
                WHERE id = $6
                """,
                status,
                provider_payment_id,
                failure_code,
                failure_message,
                webhook_verified,
                payment_id,
            )
            return result != "UPDATE 0"

    async def get_payment_by_idempotency_key(self, idempotency_key: str) -> dict[str, Any] | None:
        """Get payment by idempotency key to prevent duplicates"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments WHERE idempotency_key = $1", idempotency_key
            )
            return dict(row) if row else None

    async def get_user_payments(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get user's payment history"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT p.*, s.plan_id, pl.name as plan_name
                FROM payments p
                LEFT JOIN subscriptions s ON p.subscription_id = s.id
                LEFT JOIN plans pl ON s.plan_id = pl.id
                WHERE p.user_id = $1
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset,
            )
            return [dict(row) for row in rows]

    async def get_payment(self, payment_id: str) -> dict[str, Any] | None:
        """Get payment by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM payments WHERE id = $1", payment_id)
            return dict(row) if row else None

    async def create_webhook_event(
        self,
        provider: str,
        event_type: str,
        provider_event_id: str | None,
        object_id: str | None,
        payload: dict[str, Any],
        signature: str | None = None,
    ) -> str:
        """Create webhook event record"""
        event_id = str(uuid4())
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO webhook_events
                (id, provider, event_type, provider_event_id, object_id, payload, signature)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                event_id,
                provider,
                event_type,
                provider_event_id,
                object_id,
                payload,
                signature,
            )
        return event_id

    async def mark_webhook_processed(
        self, event_id: str, processed: bool = True, error_message: str | None = None
    ) -> bool:
        """Mark webhook event as processed"""
        async with self.pool.acquire() as conn:
            if error_message:
                result = await conn.execute(
                    """
                    UPDATE webhook_events
                    SET processed = $1, last_error = $2, retry_count = retry_count + 1,
                        processed_at = CASE WHEN $1 THEN now() ELSE processed_at END
                    WHERE id = $3
                    """,
                    processed,
                    error_message,
                    event_id,
                )
            else:
                result = await conn.execute(
                    """
                    UPDATE webhook_events
                    SET processed = $1, processed_at = now()
                    WHERE id = $2
                    """,
                    processed,
                    event_id,
                )
            return result != "UPDATE 0"

    async def get_revenue_stats(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get revenue statistics for a date range"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as payment_count,
                    SUM(CASE WHEN status = 'succeeded' THEN amount ELSE 0 END) as total_revenue,
                    SUM(CASE WHEN status = 'failed' THEN amount ELSE 0 END) as failed_amount,
                    COUNT(CASE WHEN status = 'succeeded' THEN 1 END) as successful_payments,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_payments
                FROM payments
                WHERE created_at BETWEEN $1 AND $2
                """,
                start_date,
                end_date,
            )
            return dict(row) if row else {}

    async def get_subscription_stats(self) -> dict[str, Any]:
        """Get subscription statistics"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total_subscriptions,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_subscriptions,
                    COUNT(CASE WHEN status = 'canceled' THEN 1 END) as canceled_subscriptions,
                    COUNT(CASE WHEN status = 'past_due' THEN 1 END) as past_due_subscriptions,
                    AVG(CASE WHEN status = 'active' THEN amount END) as avg_subscription_amount
                FROM subscriptions
                """
            )
            return dict(row) if row else {}

    async def get_plan_with_pricing(self, plan_id: int) -> dict[str, Any] | None:
        """Get plan with pricing information"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM plans WHERE id = $1 AND is_active = true", plan_id
            )
            return dict(row) if row else None

    async def get_all_active_plans(self) -> list[dict[str, Any]]:
        """Get all active subscription plans"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, name, max_channels, max_posts_per_month, created_at
                FROM plans
                WHERE is_active = true
                ORDER BY id
                """,
            )
            return [dict(row) for row in rows]

    # 🚀 NEW GENERATOR-BASED MEMORY OPTIMIZATIONS

    async def iter_user_payments(self, user_id: int, batch_size: int = 1000):
        """
        🧠 MEMORY-OPTIMIZED: Generator-based iteration for user payments
        Useful for processing payment history without loading all records into memory
        """
        offset = 0
        while True:
            query = """
                SELECT p.id, p.amount, p.currency, p.status, p.created_at,
                       s.plan_id, pl.name as plan_name
                FROM payments p
                LEFT JOIN subscriptions s ON p.subscription_id = s.id
                LEFT JOIN plans pl ON s.plan_id = pl.id
                WHERE p.user_id = $1
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
            """

            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, user_id, batch_size, offset)

            if not rows:
                break

            yield [dict(row) for row in rows]

            if len(rows) < batch_size:
                break

            offset += batch_size

    async def stream_payments_by_status(self, status: str = "completed"):
        """
        🧠 ADVANCED MEMORY OPTIMIZATION: Stream payments by status
        Yields individual payment records for efficient processing of large datasets
        """
        query = """
            SELECT p.id, p.user_id, p.amount, p.currency, p.status,
                   p.created_at, p.metadata,
                   s.plan_id, pl.name as plan_name
            FROM payments p
            LEFT JOIN subscriptions s ON p.subscription_id = s.id
            LEFT JOIN plans pl ON s.plan_id = pl.id
            WHERE p.status = $1
            ORDER BY p.created_at DESC
        """

        async with self.pool.acquire() as conn:
            async for record in conn.cursor(query, status):
                yield dict(record)

    async def iter_subscriptions_expiring_soon(self, days_ahead: int = 7, batch_size: int = 500):
        """
        🧠 MEMORY-OPTIMIZED: Generator for subscriptions expiring soon
        Useful for renewal notifications and batch processing
        """
        offset = 0
        while True:
            query = f"""
                SELECT s.id, s.user_id, s.current_period_end, s.status,
                       u.username, p.name as plan_name, p.max_channels
                FROM subscriptions s
                JOIN users u ON s.user_id = u.id
                JOIN plans p ON s.plan_id = p.id
                WHERE s.status = 'active'
                AND s.current_period_end <= NOW() + INTERVAL '{days_ahead} days'
                ORDER BY s.current_period_end
                LIMIT $1 OFFSET $2
            """

            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, batch_size, offset)

            if not rows:
                break

            yield [dict(row) for row in rows]

            if len(rows) < batch_size:
                break

            offset += batch_size
