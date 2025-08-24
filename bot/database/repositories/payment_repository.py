"""
Payment system database repository
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import uuid4

import asyncpg

from bot.models.payment import (
    PaymentStatus, 
    SubscriptionStatus, 
    BillingCycle,
    PaymentProvider
)


class PaymentRepository:
    """Repository for payment-related database operations"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    # Payment Methods
    async def create_payment_method(
        self,
        user_id: int,
        provider: str,
        provider_method_id: str,
        method_type: str,
        last_four: Optional[str] = None,
        brand: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        is_default: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new payment method"""
        method_id = str(uuid4())
        
        async with self.pool.acquire() as conn:
            # If this is set as default, unset others
            if is_default:
                await conn.execute(
                    "UPDATE payment_methods SET is_default = false WHERE user_id = $1",
                    user_id
                )
            
            await conn.execute(
                """
                INSERT INTO payment_methods 
                (id, user_id, provider, provider_method_id, method_type, 
                 last_four, brand, expires_at, is_default, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                method_id, user_id, provider, provider_method_id, method_type,
                last_four, brand, expires_at, is_default, metadata
            )
            
        return method_id

    async def get_user_payment_methods(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active payment methods for a user"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM payment_methods 
                WHERE user_id = $1 AND is_active = true
                ORDER BY is_default DESC, created_at DESC
                """,
                user_id
            )
            return [dict(row) for row in rows]

    async def get_payment_method(self, method_id: str) -> Optional[Dict[str, Any]]:
        """Get payment method by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payment_methods WHERE id = $1",
                method_id
            )
            return dict(row) if row else None

    async def delete_payment_method(self, method_id: str) -> bool:
        """Soft delete payment method"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE payment_methods SET is_active = false WHERE id = $1",
                method_id
            )
            return result != "UPDATE 0"

    # Subscriptions
    async def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        payment_method_id: Optional[str],
        provider_subscription_id: Optional[str],
        billing_cycle: str,
        amount: Decimal,
        currency: str,
        current_period_start: datetime,
        current_period_end: datetime,
        trial_ends_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new subscription"""
        subscription_id = str(uuid4())
        
        async with self.pool.acquire() as conn:
            # Cancel any existing active subscriptions
            await conn.execute(
                """
                UPDATE subscriptions 
                SET status = 'canceled', canceled_at = now()
                WHERE user_id = $1 AND status = 'active'
                """,
                user_id
            )
            
            await conn.execute(
                """
                INSERT INTO subscriptions 
                (id, user_id, plan_id, payment_method_id, provider_subscription_id,
                 status, billing_cycle, amount, currency, current_period_start,
                 current_period_end, trial_ends_at, metadata)
                VALUES ($1, $2, $3, $4, $5, 'active', $6, $7, $8, $9, $10, $11, $12)
                """,
                subscription_id, user_id, plan_id, payment_method_id,
                provider_subscription_id, billing_cycle, amount, currency,
                current_period_start, current_period_end, trial_ends_at, metadata
            )
            
        return subscription_id

    async def get_user_active_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
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
                user_id
            )
            return dict(row) if row else None

    async def update_subscription_status(
        self, 
        subscription_id: str, 
        status: str,
        canceled_at: Optional[datetime] = None
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
                    status, canceled_at, subscription_id
                )
            else:
                result = await conn.execute(
                    """
                    UPDATE subscriptions 
                    SET status = $1, updated_at = now()
                    WHERE id = $2
                    """,
                    status, subscription_id
                )
            return result != "UPDATE 0"

    async def extend_subscription(
        self,
        subscription_id: str,
        new_period_end: datetime
    ) -> bool:
        """Extend subscription period"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE subscriptions 
                SET current_period_end = $1, updated_at = now()
                WHERE id = $2
                """,
                new_period_end, subscription_id
            )
            return result != "UPDATE 0"

    # Payments
    async def create_payment(
        self,
        user_id: int,
        subscription_id: Optional[str],
        payment_method_id: Optional[str],
        provider: str,
        provider_payment_id: Optional[str],
        idempotency_key: str,
        amount: Decimal,
        currency: str,
        status: str = "pending",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
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
                payment_id, user_id, subscription_id, payment_method_id,
                provider, provider_payment_id, idempotency_key, amount,
                currency, status, description, metadata
            )
            
        return payment_id

    async def update_payment_status(
        self,
        payment_id: str,
        status: str,
        provider_payment_id: Optional[str] = None,
        failure_code: Optional[str] = None,
        failure_message: Optional[str] = None,
        webhook_verified: bool = False
    ) -> bool:
        """Update payment status and details"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE payments 
                SET status = $1, provider_payment_id = COALESCE($2, provider_payment_id),
                    failure_code = $3, failure_message = $4, webhook_verified = $5,
                    processed_at = CASE WHEN $1 IN ('succeeded', 'failed') THEN now() ELSE processed_at END,
                    updated_at = now()
                WHERE id = $6
                """,
                status, provider_payment_id, failure_code, failure_message,
                webhook_verified, payment_id
            )
            return result != "UPDATE 0"

    async def get_payment_by_idempotency_key(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Get payment by idempotency key to prevent duplicates"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments WHERE idempotency_key = $1",
                idempotency_key
            )
            return dict(row) if row else None

    async def get_user_payments(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
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
                user_id, limit, offset
            )
            return [dict(row) for row in rows]

    async def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments WHERE id = $1",
                payment_id
            )
            return dict(row) if row else None

    # Webhook Events
    async def create_webhook_event(
        self,
        provider: str,
        event_type: str,
        provider_event_id: Optional[str],
        object_id: Optional[str],
        payload: Dict[str, Any],
        signature: Optional[str] = None
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
                event_id, provider, event_type, provider_event_id, object_id, payload, signature
            )
            
        return event_id

    async def mark_webhook_processed(
        self,
        event_id: str,
        processed: bool = True,
        error_message: Optional[str] = None
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
                    processed, error_message, event_id
                )
            else:
                result = await conn.execute(
                    """
                    UPDATE webhook_events 
                    SET processed = $1, processed_at = now()
                    WHERE id = $2
                    """,
                    processed, event_id
                )
            return result != "UPDATE 0"

    # Analytics and Reports
    async def get_revenue_stats(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
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
                start_date, end_date
            )
            return dict(row) if row else {}

    async def get_subscription_stats(self) -> Dict[str, Any]:
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
                """,
            )
            return dict(row) if row else {}

    # Plan pricing management
    async def get_plan_with_pricing(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Get plan with pricing information"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM plans WHERE id = $1 AND is_active = true",
                plan_id
            )
            return dict(row) if row else None

    async def get_all_active_plans(self) -> List[Dict[str, Any]]:
        """Get all active plans with pricing"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM plans WHERE is_active = true ORDER BY price_monthly ASC"
            )
            return [dict(row) for row in rows]
