"""
User Bot Credentials Repository Implementation
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user_bot_domain import AdminBotAction, BotStatus, UserBotCredentials
from core.ports.user_bot_repository import IUserBotRepository
from infra.db.models.user_bot_orm import AdminBotActionORM, UserBotCredentialsORM


class UserBotRepository(IUserBotRepository):
    """SQLAlchemy implementation of user bot repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Create new user bot credentials"""
        orm = UserBotCredentialsORM(
            user_id=credentials.user_id,
            bot_token=credentials.bot_token,
            bot_username=credentials.bot_username,
            bot_id=credentials.bot_id,
            mtproto_id=credentials.mtproto_id,
            mtproto_username=credentials.mtproto_username,
            mtproto_api_id=credentials.mtproto_api_id,
            telegram_api_hash=credentials.telegram_api_hash,
            mtproto_phone=credentials.mtproto_phone,
            session_string=credentials.session_string,
            mtproto_enabled=credentials.mtproto_enabled,  # ✅ Include mtproto toggle state
            status=credentials.status.value,
            is_verified=credentials.is_verified,
            rate_limit_rps=credentials.rate_limit_rps,
            max_concurrent_requests=credentials.max_concurrent_requests,
        )

        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)

        return self._to_domain(orm)

    async def get_by_user_id(self, user_id: int) -> UserBotCredentials | None:
        """Get credentials by user ID"""
        result = await self.session.execute(
            select(UserBotCredentialsORM).where(UserBotCredentialsORM.user_id == user_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_id(self, credentials_id: int) -> UserBotCredentials | None:
        """Get credentials by ID"""
        result = await self.session.execute(
            select(UserBotCredentialsORM).where(UserBotCredentialsORM.id == credentials_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def update(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Update credentials"""
        result = await self.session.execute(
            select(UserBotCredentialsORM).where(UserBotCredentialsORM.id == credentials.id)
        )
        orm = result.scalar_one()

        # Update fields
        orm.bot_token = credentials.bot_token
        orm.bot_username = credentials.bot_username
        orm.bot_id = credentials.bot_id
        orm.mtproto_id = credentials.mtproto_id
        orm.mtproto_username = credentials.mtproto_username
        orm.mtproto_api_id = credentials.mtproto_api_id
        orm.telegram_api_hash = credentials.telegram_api_hash
        orm.mtproto_phone = credentials.mtproto_phone
        orm.session_string = credentials.session_string
        orm.mtproto_enabled = credentials.mtproto_enabled
        orm.status = credentials.status.value
        orm.is_verified = credentials.is_verified
        orm.rate_limit_rps = credentials.rate_limit_rps
        orm.max_concurrent_requests = credentials.max_concurrent_requests
        orm.last_used_at = credentials.last_used_at
        orm.updated_at = credentials.updated_at

        await self.session.flush()
        await self.session.refresh(orm)

        return self._to_domain(orm)

    async def delete(self, user_id: int) -> bool:
        """Delete user's bot credentials"""
        result = await self.session.execute(
            select(UserBotCredentialsORM).where(UserBotCredentialsORM.user_id == user_id)
        )
        orm = result.scalar_one_or_none()

        if orm:
            await self.session.delete(orm)
            await self.session.flush()
            return True
        return False

    async def list_all(
        self, limit: int = 50, offset: int = 0, status: str | None = None
    ) -> list[UserBotCredentials]:
        """List all user bot credentials"""
        query = select(UserBotCredentialsORM)

        if status:
            query = query.where(UserBotCredentialsORM.status == status)

        query = query.limit(limit).offset(offset).order_by(UserBotCredentialsORM.created_at.desc())

        result = await self.session.execute(query)
        orms = result.scalars().all()

        return [self._to_domain(orm) for orm in orms]

    async def count(self, status: str | None = None) -> int:
        """Count total user bots"""
        query = select(func.count(UserBotCredentialsORM.id))

        if status:
            query = query.where(UserBotCredentialsORM.status == status)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_all_mtproto_enabled_users(self) -> list[dict]:
        """Get all users with MTProto enabled.

        Returns:
            List of user dictionaries with basic info (id, user_id, mtproto_phone, mtproto_enabled)
        """
        query = select(UserBotCredentialsORM).where(
            UserBotCredentialsORM.mtproto_enabled == True  # noqa: E712
        )

        result = await self.session.execute(query)
        orms = result.scalars().all()

        return [
            {
                "id": orm.id,
                "user_id": orm.user_id,
                "mtproto_phone": orm.mtproto_phone,
                "mtproto_enabled": orm.mtproto_enabled,
            }
            for orm in orms
        ]

    async def get_all_mtproto_enabled_users_with_intervals(self, pool) -> list[dict]:
        """Get all users with MTProto enabled, including their collection interval.
        
        This method joins with users and plans tables to get the correct interval
        based on the user's plan (tiered intervals) or personal override.
        
        Args:
            pool: asyncpg pool for raw SQL query (needed for JOIN across tables)
        
        Returns:
            List of user dictionaries with interval info:
            - user_id: The user ID
            - mtproto_phone: MTProto phone number
            - interval_minutes: Collection interval (from plan or override)
            - min_interval_minutes: Minimum allowed interval for this user
            - plan_name: User's plan name
        """
        query = """
            SELECT 
                ubc.user_id,
                ubc.mtproto_phone,
                COALESCE(
                    u.mtproto_interval_override,
                    p.mtproto_interval_minutes,
                    60
                ) as interval_minutes,
                COALESCE(p.min_mtproto_interval_minutes, 30) as min_interval_minutes,
                COALESCE(p.name, 'free') as plan_name
            FROM user_bot_credentials ubc
            JOIN users u ON ubc.user_id = u.id
            LEFT JOIN plans p ON u.plan_id = p.id
            WHERE ubc.mtproto_enabled = TRUE
            ORDER BY interval_minutes ASC
        """
        
        rows = await pool.fetch(query)
        return [dict(row) for row in rows]

    async def log_admin_action(self, action: AdminBotAction) -> None:
        """Log admin action"""
        orm = AdminBotActionORM(
            admin_id=action.admin_user_id,
            target_user_id=action.target_user_id,
            action=action.action,
            details=action.details,
            timestamp=action.timestamp,
        )

        self.session.add(orm)
        await self.session.flush()

    async def get_by_mtproto_phone(self, phone: str) -> UserBotCredentials | None:
        """Get credentials by MTProto phone number (to check for duplicates)"""
        result = await self.session.execute(
            select(UserBotCredentialsORM).where(UserBotCredentialsORM.mtproto_phone == phone)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_bot_id(self, bot_id: int) -> UserBotCredentials | None:
        """Get credentials by bot ID (to check for duplicates)"""
        result = await self.session.execute(
            select(UserBotCredentialsORM).where(UserBotCredentialsORM.bot_id == bot_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: UserBotCredentialsORM) -> UserBotCredentials:
        """Convert ORM to domain model"""
        return UserBotCredentials(
            id=orm.id,
            user_id=orm.user_id,
            bot_token=orm.bot_token,
            mtproto_id=orm.mtproto_id,
            mtproto_username=orm.mtproto_username,
            mtproto_api_id=orm.mtproto_api_id,
            telegram_api_hash=orm.telegram_api_hash,
            bot_username=orm.bot_username,
            bot_id=orm.bot_id,
            mtproto_phone=orm.mtproto_phone,
            session_string=orm.session_string,
            mtproto_enabled=orm.mtproto_enabled,  # ✅ CRITICAL FIX: Include this field!
            status=BotStatus(orm.status),
            is_verified=orm.is_verified,
            rate_limit_rps=orm.rate_limit_rps,
            max_concurrent_requests=orm.max_concurrent_requests,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            last_used_at=orm.last_used_at,
        )
