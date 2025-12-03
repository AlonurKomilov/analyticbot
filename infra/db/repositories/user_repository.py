"""
SQLAlchemy User Repository Implementation
Concrete implementation of UserRepository interface using SQLAlchemy
"""

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.interfaces import UserRepository as IUserRepository


class AsyncpgUserRepository(IUserRepository):
    """User repository implementation using asyncpg (existing bot implementation)"""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID"""
        query = """
            SELECT u.id, u.username, u.email, u.role, u.status, u.created_at, p.name as subscription_tier
            FROM users u
            LEFT JOIN plans p ON u.plan_id = p.id
            WHERE u.id = $1
        """
        row = await self._pool.fetchrow(query, user_id)
        return dict(row) if row else None

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID - same as get_user_by_id for bot"""
        return await self.get_user_by_id(telegram_id)

    async def create_user(self, user_data: dict) -> dict:
        """Create new user with upsert (handles both Telegram and regular users)"""
        query = """
            INSERT INTO users (id, username, email, full_name, hashed_password, role, status, plan_id, telegram_id, auth_provider)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                hashed_password = EXCLUDED.hashed_password,
                role = EXCLUDED.role,
                status = EXCLUDED.status,
                telegram_id = COALESCE(EXCLUDED.telegram_id, users.telegram_id),
                auth_provider = COALESCE(EXCLUDED.auth_provider, users.auth_provider)
            RETURNING id, username, email, full_name, role, status, created_at, telegram_id, auth_provider
        """
        user_id = user_data.get("id") or user_data.get("telegram_id")
        username = user_data.get("username")
        email = user_data.get("email")
        full_name = user_data.get("full_name")
        hashed_password = user_data.get("hashed_password")
        role = user_data.get("role", "user")
        status = user_data.get("status", "pending_verification")
        plan_id = user_data.get("plan_id", 1)  # Default plan
        telegram_id = user_data.get("telegram_id")  # Store Telegram ID separately
        auth_provider = user_data.get("auth_provider", "local")  # Default to 'local'

        row = await self._pool.fetchrow(
            query, user_id, username, email, full_name, hashed_password, role, status, plan_id, telegram_id, auth_provider
        )
        return dict(row) if row else {}

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information - supports all user fields"""
        set_clauses = []
        values = []
        param_count = 1

        # Whitelist of updatable fields
        allowed_fields = [
            "username",
            "email",
            "full_name",
            "hashed_password",
            "role",
            "status",
            "plan_id",
            "last_login",
            "telegram_id",
            "telegram_username",
            "telegram_photo_url",
            "telegram_verified",
            "auth_provider",
        ]

        for key, value in updates.items():
            if key in allowed_fields and value is not None:
                set_clauses.append(f"{key} = ${param_count}")
                values.append(value)
                param_count += 1

        if not set_clauses:
            return False

        query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}
            WHERE id = ${param_count}
        """
        values.append(user_id)

        result = await self._pool.execute(query, *values)
        return result == "UPDATE 1"

    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        query = """
            SELECT p.name
            FROM users u
            JOIN plans p ON u.plan_id = p.id
            WHERE u.id = $1
        """
        tier = await self._pool.fetchval(query, user_id)
        return tier or "free"

    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)"
        return await self._pool.fetchval(query, user_id)

    async def get_feature_usage(self, user_id: int, year: int, month: int) -> dict[str, int]:
        """
        Get premium feature usage for a specific month.

        Args:
            user_id: User ID
            year: Year (e.g., 2025)
            month: Month (1-12)

        Returns:
            Dictionary with feature usage counts (e.g., {"watermarks": 5, "custom_emojis": 12})
        """
        query = """
            SELECT feature_type, usage_count
            FROM user_premium_feature_usage
            WHERE user_id = $1 AND usage_year = $2 AND usage_month = $3
        """
        rows = await self._pool.fetch(query, user_id, year, month)

        # Convert to dictionary
        usage = {}
        for row in rows:
            usage[row["feature_type"]] = row["usage_count"]

        return usage

    async def increment_feature_usage(self, user_id: int, feature_type: str, count: int = 1) -> int:
        """
        Increment premium feature usage counter for current month.

        Args:
            user_id: User ID
            feature_type: Feature type (e.g., "watermarks", "custom_emojis", "theft_scans")
            count: Number to increment by (default: 1)

        Returns:
            New usage count for this feature this month
        """
        from datetime import datetime

        now = datetime.utcnow()
        year = now.year
        month = now.month

        query = """
            INSERT INTO user_premium_feature_usage (user_id, feature_type, usage_year, usage_month, usage_count)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id, feature_type, usage_year, usage_month)
            DO UPDATE SET usage_count = user_premium_feature_usage.usage_count + $5
            RETURNING usage_count
        """
        new_count = await self._pool.fetchval(query, user_id, feature_type, year, month, count)
        return new_count or 0

    async def get_current_month_usage(self, user_id: int) -> dict[str, int]:
        """
        Get current month's premium feature usage.

        Args:
            user_id: User ID

        Returns:
            Dictionary with current month's usage counts
        """
        from datetime import datetime

        now = datetime.utcnow()
        return await self.get_feature_usage(user_id, now.year, now.month)

    async def reset_feature_usage(self, user_id: int, feature_type: str) -> bool:
        """
        Reset feature usage counter (useful for testing or manual adjustments).

        Args:
            user_id: User ID
            feature_type: Feature type to reset

        Returns:
            True if reset was successful
        """
        from datetime import datetime

        now = datetime.utcnow()
        query = """
            UPDATE user_premium_feature_usage
            SET usage_count = 0
            WHERE user_id = $1 AND feature_type = $2
              AND usage_year = $3 AND usage_month = $4
        """
        result = await self._pool.execute(query, user_id, feature_type, now.year, now.month)
        return "UPDATE" in result

    async def get_user_plan_name(self, user_id: int) -> str | None:
        """Get user's plan name"""
        query = """
            SELECT p.name
            FROM users u
            JOIN plans p ON u.plan_id = p.id
            WHERE u.id = $1
        """
        return await self._pool.fetchval(query, user_id)

    async def get_user_by_email(self, email: str) -> dict | None:
        """Get user by email address"""
        query = """
            SELECT u.id, u.username, u.created_at, u.hashed_password,
                   p.name as subscription_tier, u.email, u.full_name, u.role, u.status, u.last_login
            FROM users u
            LEFT JOIN plans p ON u.plan_id = p.id
            WHERE u.email = $1
        """
        row = await self._pool.fetchrow(query, email)
        return dict(row) if row else None

    async def get_user_by_username(self, username: str) -> dict | None:
        """Get user by username"""
        query = """
            SELECT u.id, u.username, u.created_at, u.hashed_password,
                   p.name as subscription_tier, u.email, u.full_name, u.role, u.status, u.last_login
            FROM users u
            LEFT JOIN plans p ON u.plan_id = p.id
            WHERE u.username = $1
        """
        row = await self._pool.fetchrow(query, username)
        return dict(row) if row else None


class SQLAlchemyUserRepository(IUserRepository):
    """User repository implementation using SQLAlchemy (for new implementations)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID - placeholder for SQLAlchemy implementation"""
        pass

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID"""
        pass

    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        return {}

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        return False

    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        return "pro"

    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        return True
