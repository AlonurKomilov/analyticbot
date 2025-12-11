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
    # INTERNAL HELPER - Add credits within existing transaction
    # ============================================

    async def _add_credits_with_conn(
        self,
        conn: asyncpg.Connection,
        user_id: int,
        amount: Decimal,
        transaction_type: str,
        category: str,
        description: str,
        reference_id: str | None = None,
    ) -> dict:
        """
        Add credits using an existing connection (for use within transactions).
        This avoids deadlocks from nested pool.acquire() calls.
        """
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
                (user_id, amount, balance_after, type, category, description, reference_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, user_id, amount, balance_after, type, category, description, created_at
        """,
            user_id,
            amount,
            new_balance,
            transaction_type,
            category,
            description,
            reference_id,
        )

        logger.info(f"Added {amount} credits to user {user_id}. New balance: {new_balance}")
        return dict(transaction)

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

    async def get_user_plan_credits(self, user_id: int) -> dict:
        """Get user's plan-based credit allowances"""
        query = """
            SELECT 
                p.name as plan_name,
                p.daily_credits_base,
                p.daily_credits_max,
                p.monthly_credits,
                p.monthly_credits_cap,
                COALESCE(uc.monthly_credits_used, 0) as monthly_used,
                uc.monthly_credits_reset_at
            FROM users u
            JOIN plans p ON u.plan_id = p.id
            LEFT JOIN user_credits uc ON u.id = uc.user_id
            WHERE u.id = $1
        """
        row = await self._pool.fetchrow(query, user_id)
        if row:
            return dict(row)
        # Default to free plan values
        return {
            "plan_name": "free",
            "daily_credits_base": 5,
            "daily_credits_max": 8,
            "monthly_credits": 0,
            "monthly_credits_cap": 100,
            "monthly_used": 0,
            "monthly_credits_reset_at": None,
        }

    async def check_monthly_cap(self, user_id: int, amount: Decimal) -> tuple[bool, str | None]:
        """
        Check if user can earn credits (respects monthly cap for free users).
        Returns (can_earn, error_message)
        """
        plan_info = await self.get_user_plan_credits(user_id)
        
        # No cap for paid plans
        if plan_info["monthly_credits_cap"] is None:
            return True, None
        
        # Check if we need to reset monthly counter
        now = datetime.utcnow()
        reset_at = plan_info["monthly_credits_reset_at"]
        
        if reset_at is None or reset_at.month != now.month:
            # Reset the counter
            await self._pool.execute(
                """
                UPDATE user_credits 
                SET monthly_credits_used = 0, monthly_credits_reset_at = $2
                WHERE user_id = $1
                """,
                user_id,
                now,
            )
            plan_info["monthly_used"] = 0
        
        # Check if within cap
        new_total = plan_info["monthly_used"] + int(amount)
        if new_total > plan_info["monthly_credits_cap"]:
            remaining = plan_info["monthly_credits_cap"] - plan_info["monthly_used"]
            return False, f"Monthly credit cap reached ({plan_info['monthly_credits_cap']} credits). Upgrade to Pro for unlimited! Remaining: {remaining}"
        
        return True, None

    async def claim_daily_reward(self, user_id: int) -> dict | None:
        """
        Claim daily login reward with tier-based credits.

        Returns:
            Reward info with credits earned, or None if already claimed today
        """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Get user's plan info for tier-based rewards
                plan_info = await conn.fetchrow(
                    """
                    SELECT 
                        p.daily_credits_base,
                        p.daily_credits_max,
                        p.monthly_credits_cap,
                        COALESCE(uc.monthly_credits_used, 0) as monthly_used,
                        uc.last_daily_reward_at,
                        uc.daily_streak,
                        uc.monthly_credits_reset_at
                    FROM users u
                    JOIN plans p ON u.plan_id = p.id
                    LEFT JOIN user_credits uc ON u.id = uc.user_id
                    WHERE u.id = $1
                    """,
                    user_id,
                )

                # Default to free plan if no plan found
                if plan_info:
                    base_credits = plan_info["daily_credits_base"] or 5
                    max_credits = plan_info["daily_credits_max"] or 8
                    monthly_cap = plan_info["monthly_credits_cap"]
                    monthly_used = plan_info["monthly_used"] or 0
                    last_claim = plan_info["last_daily_reward_at"]
                    current_streak = plan_info["daily_streak"] or 0
                else:
                    base_credits = 5
                    max_credits = 8
                    monthly_cap = 100
                    monthly_used = 0
                    last_claim = None
                    current_streak = 0

                now = datetime.utcnow()
                today = now.date()

                # Check if already claimed today
                if last_claim and last_claim.date() == today:
                    return None  # Already claimed today

                # Calculate streak
                if last_claim:
                    yesterday = today - timedelta(days=1)
                    if last_claim.date() == yesterday:
                        new_streak = current_streak + 1
                    else:
                        new_streak = 1  # Streak broken
                else:
                    new_streak = 1

                # Calculate reward based on streak (tier-based)
                # Streak bonus: +0.5 per day, capped at day 7 (so max +3)
                streak_multiplier = min(new_streak - 1, 6)
                streak_bonus = streak_multiplier * Decimal("0.5")
                
                # Calculate reward: base + streak bonus, capped at max
                reward_amount = min(
                    Decimal(str(base_credits)) + streak_bonus,
                    Decimal(str(max_credits))
                )

                # Check monthly cap (for free users)
                if monthly_cap is not None:
                    # Reset monthly counter if new month
                    reset_at = plan_info["monthly_credits_reset_at"] if plan_info else None
                    if reset_at is None or reset_at.month != now.month:
                        monthly_used = 0
                        await conn.execute(
                            """
                            UPDATE user_credits 
                            SET monthly_credits_used = 0, monthly_credits_reset_at = $2
                            WHERE user_id = $1
                            """,
                            user_id,
                            now,
                        )
                    
                    # Check if would exceed cap
                    if monthly_used + int(reward_amount) > monthly_cap:
                        remaining = monthly_cap - monthly_used
                        if remaining <= 0:
                            # Return special response indicating cap reached
                            return {
                                "credits_earned": 0,
                                "streak": new_streak,
                                "monthly_cap_reached": True,
                                "message": f"Monthly cap of {monthly_cap} credits reached. Upgrade to Pro for unlimited!",
                            }
                        # Award only remaining amount
                        reward_amount = Decimal(str(remaining))

                # Ensure user_credits record exists with daily streak tracking
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, balance, lifetime_earned, daily_streak, last_daily_reward_at, monthly_credits_used, monthly_credits_reset_at)
                    VALUES ($1, 0, 0, 0, NULL, 0, NOW())
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    user_id,
                )

                # Update balance and daily streak tracking
                if monthly_cap is not None:
                    # Free tier - track monthly usage and daily streak
                    result = await conn.fetchrow(
                        """
                        UPDATE user_credits
                        SET balance = balance + $2,
                            lifetime_earned = lifetime_earned + $2,
                            monthly_credits_used = COALESCE(monthly_credits_used, 0) + $2,
                            daily_streak = $3,
                            last_daily_reward_at = $4,
                            updated_at = NOW()
                        WHERE user_id = $1
                        RETURNING balance
                        """,
                        user_id,
                        reward_amount,
                        new_streak,
                        now,
                    )
                else:
                    # Paid tier - no monthly cap tracking, but track streak
                    result = await conn.fetchrow(
                        """
                        UPDATE user_credits
                        SET balance = balance + $2,
                            lifetime_earned = lifetime_earned + $2,
                            daily_streak = $3,
                            last_daily_reward_at = $4,
                            updated_at = NOW()
                        WHERE user_id = $1
                        RETURNING balance
                        """,
                        user_id,
                        reward_amount,
                        new_streak,
                        now,
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
                        (user_id, amount, balance_after, type, category, description)
                    VALUES ($1, $2, $3, 'reward', 'daily', $4)
                    RETURNING id, user_id, amount, balance_after, type, category, description, created_at
                """,
                    user_id,
                    reward_amount,
                    new_balance,
                    f"Daily login reward (Day {new_streak})",
                )

                logger.info(f"Daily reward: Added {reward_amount} credits to user {user_id}. New balance: {new_balance}")

                return {
                    "credits_earned": float(reward_amount),
                    "streak": new_streak,
                    "transaction": dict(transaction),
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
        """Get top users by achievements earned (privacy-friendly leaderboard)"""
        rows = await self._pool.fetch(
            """
            SELECT 
                u.id, 
                u.username,
                COALESCE(ua.achievements_earned, 0) as achievements_earned,
                COALESCE(ch.total_channels, 0) as total_channels,
                COALESCE(uc.daily_streak, 0) as current_streak
            FROM users u
            LEFT JOIN (
                SELECT 
                    user_id,
                    COUNT(*) FILTER (WHERE achieved_at IS NOT NULL) as achievements_earned
                FROM user_achievements
                GROUP BY user_id
            ) ua ON ua.user_id = u.id
            LEFT JOIN user_credits uc ON uc.user_id = u.id
            LEFT JOIN (
                SELECT user_id, COUNT(*) as total_channels
                FROM channels
                WHERE is_active = true
                GROUP BY user_id
            ) ch ON ch.user_id = u.id
            WHERE u.status = 'active'
            ORDER BY ua.achievements_earned DESC NULLS LAST, uc.daily_streak DESC NULLS LAST
            LIMIT $1
        """,
            limit,
        )
        return [dict(row) for row in rows]

    # ============================================
    # REFERRAL SYSTEM (ENHANCED)
    # ============================================

    async def get_user_referral_code(self, user_id: int) -> str | None:
        """Get user's referral code"""
        return await self._pool.fetchval(
            "SELECT referral_code FROM users WHERE id = $1",
            user_id,
        )

    async def get_user_by_referral_code(self, code: str) -> dict | None:
        """Get user by referral code"""
        row = await self._pool.fetchrow(
            "SELECT id, username, email FROM users WHERE referral_code = $1",
            code.upper(),
        )
        return dict(row) if row else None

    async def apply_referral(
        self,
        referred_user_id: int,
        referral_code: str,
        referrer_bonus: Decimal = Decimal("100"),
        referred_bonus: Decimal = Decimal("50"),
    ) -> dict:
        """
        Apply referral when a new user signs up with a referral code.
        Both the referrer and referred user get bonus credits.
        """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Get referrer
                referrer = await conn.fetchrow(
                    "SELECT id, username FROM users WHERE referral_code = $1",
                    referral_code.upper(),
                )
                if not referrer:
                    raise ValueError("Invalid referral code")

                referrer_id = referrer["id"]
                
                # Check if user was already referred
                existing = await conn.fetchval(
                    "SELECT id FROM user_referrals WHERE referred_user_id = $1",
                    referred_user_id,
                )
                if existing:
                    raise ValueError("User has already been referred")

                # Can't refer yourself
                if referrer_id == referred_user_id:
                    raise ValueError("Cannot use your own referral code")

                # Update referred user's referral info
                await conn.execute(
                    "UPDATE users SET referred_by_user_id = $1 WHERE id = $2",
                    referrer_id,
                    referred_user_id,
                )

                # Create referral record
                await conn.execute(
                    """
                    INSERT INTO user_referrals 
                        (referrer_user_id, referred_user_id, referral_code, credits_awarded, status, completed_at)
                    VALUES ($1, $2, $3, $4, 'completed', NOW())
                    """,
                    referrer_id,
                    referred_user_id,
                    referral_code.upper(),
                    referrer_bonus,
                )

                # Award bonus to referrer (use inline method to avoid deadlock)
                await self._add_credits_with_conn(
                    conn=conn,
                    user_id=referrer_id,
                    amount=referrer_bonus,
                    transaction_type="referral",
                    category="referral",
                    description=f"Referral bonus - someone joined with your code!",
                    reference_id=f"referral:{referred_user_id}",
                )

                # Award bonus to referred user (use inline method to avoid deadlock)
                await self._add_credits_with_conn(
                    conn=conn,
                    user_id=referred_user_id,
                    amount=referred_bonus,
                    transaction_type="bonus",
                    category="referral",
                    description=f"Welcome bonus for using referral code!",
                    reference_id=f"referred_by:{referrer_id}",
                )

                logger.info(
                    f"Referral applied: {referrer_id} referred {referred_user_id}. "
                    f"Referrer gets {referrer_bonus}, referred gets {referred_bonus}"
                )

                return {
                    "referrer_id": referrer_id,
                    "referrer_username": referrer["username"],
                    "referrer_bonus": float(referrer_bonus),
                    "referred_bonus": float(referred_bonus),
                }

    async def get_referral_stats(self, user_id: int) -> dict:
        """Get user's referral statistics"""
        async with self._pool.acquire() as conn:
            # Get referral code
            code = await conn.fetchval(
                "SELECT referral_code FROM users WHERE id = $1",
                user_id,
            )

            # Get referral count
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_referrals,
                    COALESCE(SUM(credits_awarded), 0) as total_credits_earned
                FROM user_referrals
                WHERE referrer_user_id = $1 AND status = 'completed'
                """,
                user_id,
            )

            # Get recent referrals
            recent = await conn.fetch(
                """
                SELECT r.referred_user_id, u.username, r.credits_awarded, r.completed_at
                FROM user_referrals r
                JOIN users u ON r.referred_user_id = u.id
                WHERE r.referrer_user_id = $1 AND r.status = 'completed'
                ORDER BY r.completed_at DESC
                LIMIT 10
                """,
                user_id,
            )

            return {
                "referral_code": code,
                "total_referrals": stats["total_referrals"] if stats else 0,
                "total_credits_earned": float(stats["total_credits_earned"] or 0) if stats else 0,
                "recent_referrals": [dict(r) for r in recent],
            }

    # ============================================
    # ACHIEVEMENTS SYSTEM
    # ============================================

    async def get_all_achievements(self, active_only: bool = True) -> list[dict]:
        """Get all achievement definitions"""
        query = "SELECT * FROM achievements"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY category, sort_order"
        rows = await self._pool.fetch(query)
        return [dict(row) for row in rows]

    async def get_user_achievements(self, user_id: int) -> list[dict]:
        """Get achievements earned by user"""
        rows = await self._pool.fetch(
            """
            SELECT ua.*, a.category, a.requirement_type, a.requirement_value
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_key = a.achievement_key
            WHERE ua.user_id = $1
            ORDER BY ua.achieved_at DESC
            """,
            user_id,
        )
        return [dict(row) for row in rows]

    async def check_and_award_achievement(
        self,
        user_id: int,
        achievement_key: str,
    ) -> dict | None:
        """
        Check if user qualifies for an achievement and award it if not already earned.
        Returns the achievement info if awarded, None otherwise.
        """
        async with self._pool.acquire() as conn:
            # Check if already earned
            existing = await conn.fetchval(
                "SELECT id FROM user_achievements WHERE user_id = $1 AND achievement_key = $2",
                user_id,
                achievement_key,
            )
            if existing:
                return None  # Already earned

            # Get achievement details
            achievement = await conn.fetchrow(
                "SELECT * FROM achievements WHERE achievement_key = $1 AND is_active = TRUE",
                achievement_key,
            )
            if not achievement:
                return None  # Achievement doesn't exist

            async with conn.transaction():
                # Record achievement
                await conn.execute(
                    """
                    INSERT INTO user_achievements 
                        (user_id, achievement_key, achievement_name, description, credits_awarded, icon)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    user_id,
                    achievement_key,
                    achievement["name"],
                    achievement["description"],
                    achievement["credit_reward"],
                    achievement["icon"],
                )

                # Award credits if any (use inline method to avoid deadlock)
                if achievement["credit_reward"] > 0:
                    await self._add_credits_with_conn(
                        conn=conn,
                        user_id=user_id,
                        amount=Decimal(str(achievement["credit_reward"])),
                        transaction_type="bonus",
                        category="achievement",
                        description=f"Achievement unlocked: {achievement['name']}",
                        reference_id=f"achievement:{achievement_key}",
                    )

                logger.info(
                    f"User {user_id} earned achievement: {achievement['name']} "
                    f"(+{achievement['credit_reward']} credits)"
                )

                return {
                    "achievement_key": achievement_key,
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "credits_awarded": float(achievement["credit_reward"]),
                    "icon": achievement["icon"],
                    "category": achievement["category"],
                }

    async def check_streak_achievements(self, user_id: int, current_streak: int) -> list[dict]:
        """Check and award streak-based achievements"""
        awarded = []
        
        streak_achievements = [
            ("streak_3", 3),
            ("streak_7", 7),
            ("streak_30", 30),
            ("streak_100", 100),
        ]
        
        for ach_key, required_streak in streak_achievements:
            if current_streak >= required_streak:
                result = await self.check_and_award_achievement(user_id, ach_key)
                if result:
                    awarded.append(result)
        
        return awarded

    async def get_achievement_progress(self, user_id: int) -> dict:
        """Get user's progress towards achievements"""
        async with self._pool.acquire() as conn:
            # Get all achievements
            all_achievements = await conn.fetch(
                "SELECT * FROM achievements WHERE is_active = TRUE ORDER BY category, sort_order"
            )
            
            # Get user's earned achievements
            earned = await conn.fetch(
                "SELECT achievement_key FROM user_achievements WHERE user_id = $1",
                user_id,
            )
            earned_keys = {r["achievement_key"] for r in earned}
            
            # Get user stats for progress calculation
            user_stats = await conn.fetchrow(
                """
                SELECT 
                    COALESCE(uc.daily_streak, 0) as daily_streak,
                    COALESCE(uc.lifetime_earned, 0) as lifetime_earned,
                    COALESCE(uc.lifetime_spent, 0) as lifetime_spent,
                    (SELECT COUNT(*) FROM channels WHERE user_id = $1) as channel_count,
                    (SELECT COUNT(*) FROM user_referrals WHERE referrer_user_id = $1 AND status = 'completed') as referral_count
                FROM users u
                LEFT JOIN user_credits uc ON u.id = uc.user_id
                WHERE u.id = $1
                """,
                user_id,
            )
            
            progress = []
            for ach in all_achievements:
                is_earned = ach["achievement_key"] in earned_keys
                current_value = 0
                
                # Calculate progress based on requirement type
                if ach["requirement_type"] == "streak":
                    current_value = user_stats["daily_streak"] if user_stats else 0
                elif ach["category"] == "channels":
                    current_value = user_stats["channel_count"] if user_stats else 0
                elif ach["category"] == "referrals":
                    current_value = user_stats["referral_count"] if user_stats else 0
                elif ach["category"] == "credits" and "spend" in ach["achievement_key"]:
                    current_value = int(user_stats["lifetime_spent"] or 0) if user_stats else 0
                elif ach["category"] == "credits":
                    current_value = int(user_stats["lifetime_earned"] or 0) if user_stats else 0
                
                progress.append({
                    "achievement_key": ach["achievement_key"],
                    "name": ach["name"],
                    "description": ach["description"],
                    "credit_reward": float(ach["credit_reward"]),
                    "icon": ach["icon"],
                    "category": ach["category"],
                    "is_earned": is_earned,
                    "current_value": current_value,
                    "required_value": ach["requirement_value"],
                    "progress_percent": min(100, int(current_value / ach["requirement_value"] * 100)) if ach["requirement_value"] else (100 if is_earned else 0),
                })
            
            return {
                "total_achievements": len(all_achievements),
                "earned_count": len(earned_keys),
                "achievements": progress,
            }

    async def get_claimable_achievements(self, user_id: int) -> list[dict]:
        """
        Get achievements that user has met requirements for but hasn't claimed yet.
        This allows users to manually claim their rewards.
        """
        async with self._pool.acquire() as conn:
            # Get user's earned achievements
            earned = await conn.fetch(
                "SELECT achievement_key FROM user_achievements WHERE user_id = $1",
                user_id,
            )
            earned_keys = {r["achievement_key"] for r in earned}
            
            # Get user stats
            user_stats = await conn.fetchrow(
                """
                SELECT 
                    COALESCE(uc.daily_streak, 0) as daily_streak,
                    COALESCE(uc.lifetime_earned, 0) as lifetime_earned,
                    COALESCE(uc.lifetime_spent, 0) as lifetime_spent,
                    (SELECT COUNT(*) FROM channels WHERE user_id = $1) as channel_count,
                    (SELECT COUNT(*) FROM user_referrals WHERE referrer_user_id = $1 AND status = 'completed') as referral_count,
                    u.email IS NOT NULL as has_email,
                    u.full_name IS NOT NULL as has_full_name,
                    u.plan_id,
                    (SELECT p.name FROM plans p WHERE p.id = u.plan_id) as plan_name
                FROM users u
                LEFT JOIN user_credits uc ON u.id = uc.user_id
                WHERE u.id = $1
                """,
                user_id,
            )
            
            if not user_stats:
                return []
            
            # Get all active achievements
            all_achievements = await conn.fetch(
                "SELECT * FROM achievements WHERE is_active = TRUE ORDER BY category, sort_order"
            )
            
            # Get engagement stats (AI usage, exports, views)
            engagement_stats = await conn.fetchrow(
                """
                SELECT 
                    COALESCE(SUM(CASE WHEN category = 'ai' THEN 1 ELSE 0 END), 0) as ai_usage_count,
                    COALESCE(SUM(CASE WHEN category = 'export' THEN 1 ELSE 0 END), 0) as export_count
                FROM credit_transactions
                WHERE user_id = $1 AND type = 'spend'
                """,
                user_id,
            )
            
            # Get total views from post_metrics
            total_views = await conn.fetchval(
                """
                SELECT COALESCE(SUM(pm.views), 0) 
                FROM post_metrics pm
                JOIN posts p ON pm.channel_id = p.channel_id AND pm.msg_id = p.msg_id
                JOIN channels c ON p.channel_id = c.id
                WHERE c.user_id = $1
                """,
                user_id,
            ) or 0
            
            claimable = []
            for ach in all_achievements:
                if ach["achievement_key"] in earned_keys:
                    continue  # Already claimed
                
                # Calculate current value based on achievement type
                current_value = 0
                can_claim = False
                
                req_type = ach["requirement_type"]
                req_value = ach["requirement_value"] or 1
                ach_key = ach["achievement_key"]
                category = ach["category"]
                
                # Account achievements
                if category == "account":
                    if ach_key == "first_login":
                        can_claim = True  # Everyone can claim this
                        current_value = 1
                    elif ach_key == "verified_email":
                        # Consider email as verified if they have an email (for now)
                        can_claim = user_stats["has_email"] or False
                        current_value = 1 if can_claim else 0
                    elif ach_key == "profile_complete":
                        can_claim = user_stats["has_full_name"] or False
                        current_value = 1 if can_claim else 0
                    elif ach_key == "upgrade_pro":
                        can_claim = user_stats["plan_name"] in ("pro", "business")
                        current_value = 1 if can_claim else 0
                    elif ach_key == "upgrade_business":
                        can_claim = user_stats["plan_name"] == "business"
                        current_value = 1 if can_claim else 0
                
                # Channel achievements
                elif category == "channels":
                    current_value = user_stats["channel_count"]
                    can_claim = current_value >= req_value
                
                # Referral achievements
                elif category == "referrals":
                    current_value = user_stats["referral_count"]
                    can_claim = current_value >= req_value
                
                # Streak achievements
                elif category == "streaks" or req_type == "streak":
                    current_value = user_stats["daily_streak"]
                    can_claim = current_value >= req_value
                
                # Credit achievements
                elif category == "credits":
                    if "spend" in ach_key:
                        current_value = int(user_stats["lifetime_spent"] or 0)
                    elif "purchase" in ach_key:
                        # Check if user has made any purchase
                        has_purchase = await conn.fetchval(
                            "SELECT 1 FROM credit_transactions WHERE user_id = $1 AND type = 'purchase' LIMIT 1",
                            user_id,
                        )
                        can_claim = has_purchase is not None
                        current_value = 1 if can_claim else 0
                    else:
                        current_value = int(user_stats["lifetime_earned"] or 0)
                    
                    if req_type == "count":
                        can_claim = current_value >= req_value
                
                # Engagement achievements
                elif category == "engagement":
                    if "views" in ach_key or "view" in ach_key:
                        current_value = int(total_views)
                        can_claim = current_value >= req_value
                    elif ach_key == "first_ai_use":
                        current_value = engagement_stats["ai_usage_count"] if engagement_stats else 0
                        can_claim = current_value >= 1
                    elif ach_key == "ai_power_user":
                        current_value = engagement_stats["ai_usage_count"] if engagement_stats else 0
                        can_claim = current_value >= req_value
                    elif ach_key == "first_export":
                        current_value = engagement_stats["export_count"] if engagement_stats else 0
                        can_claim = current_value >= 1
                
                if can_claim:
                    claimable.append({
                        "achievement_key": ach["achievement_key"],
                        "name": ach["name"],
                        "description": ach["description"],
                        "credit_reward": ach["credit_reward"],
                        "icon": ach["icon"],
                        "category": ach["category"],
                        "current_value": current_value,
                        "required_value": req_value,
                    })
            
            return claimable

    async def claim_achievement(self, user_id: int, achievement_key: str) -> dict | None:
        """
        Claim a specific achievement. User must meet the requirements.
        Returns achievement info with new balance if successful, error dict if failed.
        """
        # First check if it's claimable
        claimable = await self.get_claimable_achievements(user_id)
        claimable_keys = {a["achievement_key"] for a in claimable}
        
        if achievement_key not in claimable_keys:
            # Check if already claimed
            existing = await self._pool.fetchval(
                "SELECT 1 FROM user_achievements WHERE user_id = $1 AND achievement_key = $2",
                user_id,
                achievement_key,
            )
            if existing:
                return {"error": "Achievement already claimed"}
            return {"error": "Requirements not met for this achievement"}
        
        # Award the achievement
        result = await self.check_and_award_achievement(user_id, achievement_key)
        
        if result:
            # Get new balance
            balance = await self._pool.fetchval(
                "SELECT balance FROM user_credits WHERE user_id = $1",
                user_id,
            )
            result["new_balance"] = float(balance or 0)
        
        return result
