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
        """Create new user with upsert (handles both Telegram and regular users)"""
        query = """
            INSERT INTO users (id, username, email, full_name, hashed_password, role, status, plan_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                hashed_password = EXCLUDED.hashed_password,
                role = EXCLUDED.role,
                status = EXCLUDED.status
            RETURNING id, username, email, full_name, role, status, created_at
        """
        user_id = user_data.get("id") or user_data.get("telegram_id")
        username = user_data.get("username")
        email = user_data.get("email")
        full_name = user_data.get("full_name")
        hashed_password = user_data.get("hashed_password")
        role = user_data.get("role", "user")
        status = user_data.get("status", "pending_verification")
        plan_id = user_data.get("plan_id", 1)  # Default plan

        row = await self._pool.fetchrow(
            query,
            user_id,
            username,
            email,
            full_name,
            hashed_password,
            role,
            status,
            plan_id,
        )
        return dict(row) if row else {}

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        set_clauses = []
        values = []
        param_count = 1

        for key, value in updates.items():
            if key in ["username", "plan_id"]:
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

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID"""

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
