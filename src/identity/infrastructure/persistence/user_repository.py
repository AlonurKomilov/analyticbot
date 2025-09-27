"""
SQLAlchemy User Repository Implementation
Concrete implementation of UserRepository interface using SQLAlchemy
"""

import asyncpg
from core.repositories.interfaces import UserRepository as IUserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncpgUserRepository(IUserRepository):
    """User repository implementation using asyncpg (existing bot implementation)"""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID"""
        query = """
            SELECT u.id, u.username, u.created_at, p.name as subscription_tier
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
        """Create new user"""
        query = """
            INSERT INTO users (id, username, plan_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO UPDATE SET 
                username = EXCLUDED.username
            RETURNING id, username, created_at
        """
        user_id = user_data.get("id") or user_data.get("telegram_id")
        username = user_data.get("username")
        plan_id = user_data.get("plan_id", 1)  # Default plan

        row = await self._pool.fetchrow(query, user_id, username, plan_id)
        return dict(row) if row else {}

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        # Build dynamic update query
        set_clauses = []
        values = []
        param_count = 1

        for key, value in updates.items():
            if key in ["username", "plan_id"]:  # Only allow certain fields
                set_clauses.append(f"{key} = ${param_count}")
                values.append(value)
                param_count += 1

        if not set_clauses:
            return False

        query = f"""
            UPDATE users 
            SET {", ".join(set_clauses)}
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
        # TODO: Implement when we migrate to SQLAlchemy models

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID"""
        # TODO: Implement SQLAlchemy version

    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        # TODO: Implement SQLAlchemy version
        return {}

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        # TODO: Implement SQLAlchemy version
        return False

    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        # TODO: Implement SQLAlchemy version
        return "pro"

    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        # TODO: Implement SQLAlchemy version
        return True
