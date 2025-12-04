"""
Credit Repository Implementation

Handles all credit-related database operations including:
- Balance management
- Credit transactions
- Packages and services
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import asyncpg

logger = logging.getLogger(__name__)


class CreditRepository:
    """Repository for credit system operations"""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    # ============================================
    # BALANCE OPERATIONS
    # ============================================

    async def get_balance(self, user_id: int) -> dict:
        """Get user's credit balance and stats"""
        query = """
            SELECT
                COALESCE(uc.balance, u.credit_balance, 0) as balance,
                COALESCE(uc.lifetime_earned, 0) as lifetime_earned,
                COALESCE(uc.lifetime_spent, 0) as lifetime_spent,
                COALESCE(uc.daily_streak, 0) as daily_streak,
                uc.last_daily_reward_at
            FROM users u
            LEFT JOIN user_credits uc ON u.id = uc.user_id
            WHERE u.id = $1
        """
        row = await self._pool.fetchrow(query, user_id)
        if row:
            return dict(row)
        return {
            "balance": Decimal("0.00"),
            "lifetime_earned": Decimal("0.00"),
            "lifetime_spent": Decimal("0.00"),
            "daily_streak": 0,
            "last_daily_reward_at": None,
        }

    async def ensure_user_credits_exists(self, user_id: int) -> None:
        """Ensure user_credits record exists for user"""
        query = """
            INSERT INTO user_credits (user_id, balance)
            VALUES ($1, 0)
            ON CONFLICT (user_id) DO NOTHING
        """
        await self._pool.execute(query, user_id)

    async def add_credits(
        self,
        user_id: int,
        amount: Decimal,
        transaction_type: str,
        category: str | None = None,
        description: str | None = None,
        reference_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """
        Add credits to user's balance.

        Args:
            user_id: User ID
            amount: Amount of credits to add (positive number)
            transaction_type: Type of transaction ('purchase', 'reward', 'bonus', 'referral', 'subscription')
            category: Category ('signup', 'daily', 'referral', 'purchase')
            description: Human-readable description
            reference_id: Reference to payment ID, etc.
            metadata: Additional JSON data

        Returns:
            Transaction record with new balance
        """
        if amount <= 0:
            raise ValueError("Amount must be positive for adding credits")

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Ensure user_credits record exists
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, balance, lifetime_earned)
                    VALUES ($1, 0, 0)
                    ON CONFLICT (user_id) DO NOTHING
                """,
                    user_id,
                )

                # Update balance and get new balance
                result = await conn.fetchrow(
                    """
                    UPDATE user_credits
                    SET balance = balance + $2,
                        lifetime_earned = lifetime_earned + $2,
                        updated_at = NOW()
                    WHERE user_id = $1
                    RETURNING balance
                """,
                    user_id,
                    amount,
                )

                new_balance = result["balance"]

                # Also update users.credit_balance for quick access
                await conn.execute(
                    """
                    UPDATE users SET credit_balance = $2 WHERE id = $1
                """,
                    user_id,
                    new_balance,
                )

                # Create transaction record
                transaction = await conn.fetchrow(
                    """
                    INSERT INTO credit_transactions
                        (user_id, amount, balance_after, type, category, description, reference_id, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id, user_id, amount, balance_after, type, category, description, created_at
                """,
                    user_id,
                    amount,
                    new_balance,
                    transaction_type,
                    category,
                    description,
                    reference_id,
                    metadata,
                )

                logger.info(f"Added {amount} credits to user {user_id}. New balance: {new_balance}")
                return dict(transaction)

    async def spend_credits(
        self,
        user_id: int,
        amount: Decimal,
        service_key: str,
        description: str | None = None,
        reference_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """
        Spend credits from user's balance.

        Args:
            user_id: User ID
            amount: Amount of credits to spend (positive number)
            service_key: Service being purchased
            description: Human-readable description
            reference_id: Reference to action ID
            metadata: Additional JSON data

        Returns:
            Transaction record with new balance

        Raises:
            ValueError: If insufficient balance
        """
        if amount <= 0:
            raise ValueError("Amount must be positive for spending credits")

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Get current balance
                current = await conn.fetchval(
                    """
                    SELECT COALESCE(balance, 0) FROM user_credits WHERE user_id = $1
                """,
                    user_id,
                )

                if current is None or current < amount:
                    raise ValueError(f"Insufficient credits. Have: {current or 0}, Need: {amount}")

                # Update balance
                result = await conn.fetchrow(
                    """
                    UPDATE user_credits
                    SET balance = balance - $2,
                        lifetime_spent = lifetime_spent + $2,
                        updated_at = NOW()
                    WHERE user_id = $1
                    RETURNING balance
                """,
                    user_id,
                    amount,
                )

                new_balance = result["balance"]

                # Also update users.credit_balance
                await conn.execute(
                    """
                    UPDATE users SET credit_balance = $2 WHERE id = $1
                """,
                    user_id,
                    new_balance,
                )

                # Get service info for category
                service = await conn.fetchrow(
                    """
                    SELECT category, name FROM credit_services WHERE service_key = $1
                """,
                    service_key,
                )

                category = service["category"] if service else "other"
                if not description and service:
                    description = f"Used: {service['name']}"

                # Create transaction record (negative amount for spending)
                transaction = await conn.fetchrow(
                    """
                    INSERT INTO credit_transactions
                        (user_id, amount, balance_after, type, category, description, reference_id, metadata)
                    VALUES ($1, $2, $3, 'spend', $4, $5, $6, $7)
                    RETURNING id, user_id, amount, balance_after, type, category, description, created_at
                """,
                    user_id,
                    -amount,
                    new_balance,
                    category,
                    description,
                    reference_id,
                    metadata,
                )

                logger.info(
                    f"Spent {amount} credits from user {user_id} on {service_key}. New balance: {new_balance}"
                )
                return dict(transaction)

    async def can_afford(self, user_id: int, amount: Decimal) -> bool:
        """Check if user can afford a purchase"""
        balance = await self._pool.fetchval(
            """
            SELECT COALESCE(balance, 0) FROM user_credits WHERE user_id = $1
        """,
            user_id,
        )
        return (balance or Decimal("0")) >= amount

    # ============================================
    # TRANSACTION HISTORY
    # ============================================

    async def get_transactions(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        transaction_type: str | None = None,
        category: str | None = None,
    ) -> list[dict]:
        """Get user's credit transaction history"""
        query = """
            SELECT id, amount, balance_after, type, category, description, reference_id, created_at
            FROM credit_transactions
            WHERE user_id = $1
        """
        params: list[Any] = [user_id]
        param_count = 1

        if transaction_type:
            param_count += 1
            query += f" AND type = ${param_count}"
            params.append(transaction_type)

        if category:
            param_count += 1
            query += f" AND category = ${param_count}"
            params.append(category)

        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])

        rows = await self._pool.fetch(query, *params)
        return [dict(row) for row in rows]

    async def get_transaction_count(self, user_id: int) -> int:
        """Get total transaction count for user"""
        return (
            await self._pool.fetchval(
                """
            SELECT COUNT(*) FROM credit_transactions WHERE user_id = $1
        """,
                user_id,
            )
            or 0
        )

    # ============================================
    # DAILY REWARDS
    # ============================================

    async def claim_daily_reward(self, user_id: int) -> dict | None:
        """
        Claim daily login reward.

        Returns:
            Reward info with credits earned, or None if already claimed today
        """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Check last claim
                result = await conn.fetchrow(
                    """
                    SELECT last_daily_reward_at, daily_streak
                    FROM user_credits
                    WHERE user_id = $1
                """,
                    user_id,
                )

                now = datetime.utcnow()
                today = now.date()

                if result and result["last_daily_reward_at"]:
                    last_claim = result["last_daily_reward_at"].date()
                    if last_claim == today:
                        return None  # Already claimed today

                    # Check if streak continues (claimed yesterday)
                    yesterday = today - timedelta(days=1)
                    if last_claim == yesterday:
                        new_streak = (result["daily_streak"] or 0) + 1
                    else:
                        new_streak = 1  # Streak broken
                else:
                    new_streak = 1

                # Calculate reward based on streak (1-5 credits, max at 7-day streak)
                base_reward = Decimal("1")
                streak_bonus = min(new_streak - 1, 6) * Decimal("0.5")
                reward_amount = base_reward + streak_bonus

                # Update streak info
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, daily_streak, last_daily_reward_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id) DO UPDATE SET
                        daily_streak = $2,
                        last_daily_reward_at = $3
                """,
                    user_id,
                    new_streak,
                    now,
                )

                # Add credits
                transaction = await self.add_credits(
                    user_id=user_id,
                    amount=reward_amount,
                    transaction_type="reward",
                    category="daily",
                    description=f"Daily login reward (Day {new_streak})",
                )

                return {
                    "credits_earned": float(reward_amount),
                    "streak": new_streak,
                    "transaction": transaction,
                }

    # ============================================
    # PACKAGES & SERVICES
    # ============================================

    async def get_packages(self, active_only: bool = True) -> list[dict]:
        """Get available credit packages for purchase"""
        query = """
            SELECT id, name, slug, credits, bonus_credits, price, currency,
                   description, is_popular, sort_order
            FROM credit_packages
        """
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY sort_order, price"

        rows = await self._pool.fetch(query)
        return [dict(row) for row in rows]

    async def get_package_by_slug(self, slug: str) -> dict | None:
        """Get a specific package by slug"""
        row = await self._pool.fetchrow(
            """
            SELECT id, name, slug, credits, bonus_credits, price, currency, description
            FROM credit_packages
            WHERE slug = $1 AND is_active = TRUE
        """,
            slug,
        )
        return dict(row) if row else None

    async def get_services(
        self, active_only: bool = True, category: str | None = None
    ) -> list[dict]:
        """Get available credit services"""
        query = """
            SELECT id, service_key, name, description, credit_cost, category, icon, usage_limit_per_day
            FROM credit_services
        """
        conditions = []
        params: list[Any] = []

        if active_only:
            conditions.append("is_active = TRUE")
        if category:
            conditions.append(f"category = ${len(params) + 1}")
            params.append(category)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY category, credit_cost"

        rows = await self._pool.fetch(query, *params)
        return [dict(row) for row in rows]

    async def get_service_by_key(self, service_key: str) -> dict | None:
        """Get a specific service by key"""
        row = await self._pool.fetchrow(
            """
            SELECT id, service_key, name, description, credit_cost, category, usage_limit_per_day
            FROM credit_services
            WHERE service_key = $1 AND is_active = TRUE
        """,
            service_key,
        )
        return dict(row) if row else None

    async def get_service_cost(self, service_key: str) -> Decimal | None:
        """Get the cost of a service"""
        cost = await self._pool.fetchval(
            """
            SELECT credit_cost FROM credit_services WHERE service_key = $1 AND is_active = TRUE
        """,
            service_key,
        )
        return Decimal(str(cost)) if cost else None

    # ============================================
    # REFERRAL SYSTEM
    # ============================================

    async def add_referral_bonus(
        self,
        referrer_user_id: int,
        referred_user_id: int,
        bonus_amount: Decimal = Decimal("100"),
    ) -> dict:
        """Add referral bonus when a referred user signs up"""
        return await self.add_credits(
            user_id=referrer_user_id,
            amount=bonus_amount,
            transaction_type="referral",
            category="referral",
            description=f"Referral bonus for inviting user #{referred_user_id}",
            reference_id=f"referral:{referred_user_id}",
        )

    # ============================================
    # ADMIN OPERATIONS
    # ============================================

    async def admin_adjust_balance(
        self,
        user_id: int,
        amount: Decimal,
        reason: str,
        admin_id: int,
    ) -> dict:
        """Admin adjustment of user balance (can be positive or negative)"""
        if amount >= 0:
            return await self.add_credits(
                user_id=user_id,
                amount=amount,
                transaction_type="bonus",
                category="admin",
                description=f"Admin adjustment: {reason}",
                reference_id=f"admin:{admin_id}",
                metadata={"admin_id": admin_id, "reason": reason},
            )
        else:
            # For negative adjustments, use spend logic but with admin type
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    result = await conn.fetchrow(
                        """
                        UPDATE user_credits
                        SET balance = balance + $2,
                            updated_at = NOW()
                        WHERE user_id = $1
                        RETURNING balance
                    """,
                        user_id,
                        amount,
                    )  # amount is negative

                    new_balance = result["balance"] if result else Decimal("0")

                    await conn.execute(
                        """
                        UPDATE users SET credit_balance = $2 WHERE id = $1
                    """,
                        user_id,
                        new_balance,
                    )

                    transaction = await conn.fetchrow(
                        """
                        INSERT INTO credit_transactions
                            (user_id, amount, balance_after, type, category, description, reference_id, metadata)
                        VALUES ($1, $2, $3, 'adjustment', 'admin', $4, $5, $6)
                        RETURNING id, user_id, amount, balance_after, type, category, description, created_at
                    """,
                        user_id,
                        amount,
                        new_balance,
                        f"Admin adjustment: {reason}",
                        f"admin:{admin_id}",
                        {"admin_id": admin_id, "reason": reason},
                    )

                    return dict(transaction)

    async def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """Get top users by credit balance"""
        rows = await self._pool.fetch(
            """
            SELECT u.id, u.username, uc.balance, uc.lifetime_earned
            FROM user_credits uc
            JOIN users u ON uc.user_id = u.id
            WHERE u.status = 'active'
            ORDER BY uc.balance DESC
            LIMIT $1
        """,
            limit,
        )
        return [dict(row) for row in rows]
