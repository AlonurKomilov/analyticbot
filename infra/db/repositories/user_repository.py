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
        """Get user by Telegram ID - searches telegram_id column, NOT user id"""
        query = """
            SELECT u.id, u.username, u.email, u.full_name, u.hashed_password,
                   u.role, u.status, u.created_at, u.telegram_id, u.auth_provider,
                   u.suspension_reason, u.suspended_at, u.suspended_by,
                   p.name as subscription_tier
            FROM users u
            LEFT JOIN plans p ON u.plan_id = p.id
            WHERE u.telegram_id = $1
        """
        row = await self._pool.fetchrow(query, telegram_id)
        return dict(row) if row else None

    async def _get_next_available_id(self) -> int:
        """Get next available user ID, skipping reserved and existing IDs.

        This method ensures NO DUPLICATE IDs by checking:
        1. Reserved premium IDs table (beautiful numbers for sale)
        2. Existing users table (prevent collision with legacy IDs like 844338517)

        Premium IDs (like 111111111, 123456789) are reserved for sale.
        Regular users get normal sequential IDs.
        """
        import logging

        log = logging.getLogger(__name__)

        max_attempts = 100  # Safety limit
        for _ in range(max_attempts):
            # Get next ID from sequence
            user_id = await self._pool.fetchval("SELECT nextval('users_id_seq')")

            # Check 1: Is this ID reserved for premium sale?
            is_reserved = await self._pool.fetchval(
                "SELECT EXISTS(SELECT 1 FROM reserved_premium_ids WHERE id = $1 AND is_sold = FALSE)",
                user_id,
            )

            if is_reserved:
                log.debug(f"Skipping reserved premium ID: {user_id}")
                continue

            # Check 2: Does this ID already exist in users table? (safety check)
            id_exists = await self._pool.fetchval(
                "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)", user_id
            )

            if id_exists:
                log.warning(f"Skipping existing user ID (collision prevented): {user_id}")
                continue

            # ID is available!
            return user_id

        # Fallback - should never reach here
        raise Exception("Could not find available user ID after 100 attempts")

    async def create_user(self, user_data: dict) -> dict:
        """Create new user (handles both Telegram and regular users)

        IMPORTANT: Always uses sequence-generated ID (users_id_seq) for ALL users.
        The telegram_id is stored ONLY in the telegram_id column, never as the primary key.

        This ensures:
        1. User IDs are always system-generated (100000001+)
        2. telegram_id is kept separate from the primary key
        3. No collision risk between Telegram IDs and user IDs
        4. No accidental data leaks from ID confusion
        5. Premium IDs (111111111, 123456789, etc.) are reserved for sale

        IMPORTANT: This does NOT do ON CONFLICT upsert to prevent accidentally
        overwriting existing users. Caller must check for existing user first.
        """
        telegram_id = user_data.get("telegram_id")
        auth_provider = user_data.get("auth_provider", "local")

        # Always use sequence for generating user ID - NEVER use telegram_id as user ID
        user_id = user_data.get("id")
        if not user_id:
            # Get next available ID (skips reserved premium IDs)
            user_id = await self._get_next_available_id()

        username = user_data.get("username")
        email = user_data.get("email")
        full_name = user_data.get("full_name")
        hashed_password = user_data.get("hashed_password")
        role = user_data.get("role", "user")

        # Determine default status based on auth provider:
        # - Telegram users: "active" (already verified by Telegram)
        # - Local users with password: "active" (ready to use)
        # - Local users without password: "pending_verification" (need to complete setup)
        default_status = "active"  # Most users should be active
        if auth_provider == "local" and not hashed_password:
            default_status = "pending_verification"

        status = user_data.get("status", default_status)
        plan_id = user_data.get("plan_id", 1)  # Default plan

        # Simple INSERT - caller should check for existing user first
        query = """
            INSERT INTO users (id, username, email, full_name, hashed_password, role, status, plan_id, telegram_id, auth_provider)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id, username, email, full_name, role, status, created_at, telegram_id, auth_provider, hashed_password
        """

        try:
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
                telegram_id,
                auth_provider,
            )

            if row:
                user_dict = dict(row)

                # Award welcome credits to new users (50 credits)
                try:
                    await self._award_welcome_credits(user_id)
                except Exception as e:
                    import logging

                    logging.getLogger(__name__).warning(
                        f"Failed to award welcome credits to user {user_id}: {e}"
                    )

                return user_dict
            return {}
        except Exception as e:
            # If insert fails (e.g., duplicate key), log and return empty
            import logging

            logging.getLogger(__name__).error(f"Failed to create user: {e}")
            raise

    async def _award_welcome_credits(self, user_id: int) -> None:
        """Award welcome credits to a new user.

        Gives 50 credits as a welcome bonus for new users.
        This is called automatically after user creation.
        """
        WELCOME_CREDITS = 50

        # First, initialize user's credit balance
        await self._pool.execute(
            "UPDATE users SET credit_balance = $1 WHERE id = $2 AND (credit_balance IS NULL OR credit_balance = 0)",
            WELCOME_CREDITS,
            user_id,
        )

        # Create user_credits record if doesn't exist
        await self._pool.execute(
            """
            INSERT INTO user_credits (user_id, balance)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
        """,
            user_id,
            WELCOME_CREDITS,
        )

        # Record the transaction
        await self._pool.execute(
            """
            INSERT INTO credit_transactions (user_id, amount, transaction_type, description, balance_after)
            VALUES ($1, $2, 'welcome_bonus', 'Welcome bonus - 50 credits for new users!', $2)
        """,
            user_id,
            WELCOME_CREDITS,
        )

        import logging

        logging.getLogger(__name__).info(
            f"Awarded {WELCOME_CREDITS} welcome credits to new user {user_id}"
        )

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
