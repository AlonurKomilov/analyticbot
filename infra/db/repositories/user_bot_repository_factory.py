"""
User Bot Repository Factory - Creates repositories with fresh sessions
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.models.user_bot_domain import AdminBotAction, UserBotCredentials
from core.ports.user_bot_repository import IUserBotRepository

from .user_bot_repository import UserBotRepository


class UserBotRepositoryFactory(IUserBotRepository):
    """
    Repository factory that creates fresh sessions for each operation

    This is a workaround for the bot manager needing long-lived repository access
    without keeping sessions open indefinitely.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize repository factory

        Args:
            session_factory: SQLAlchemy async session factory
        """
        self.session_factory = session_factory

    async def create(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Create new user bot credentials"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            result = await repo.create(credentials)
            await session.commit()
            return result

    async def get_by_user_id(self, user_id: int) -> UserBotCredentials | None:
        """Get credentials by user ID"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            return await repo.get_by_user_id(user_id)

    async def get_by_id(self, credentials_id: int) -> UserBotCredentials | None:
        """Get credentials by ID"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            return await repo.get_by_id(credentials_id)

    async def update(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Update credentials"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            result = await repo.update(credentials)
            await session.commit()
            return result

    async def delete(self, user_id: int) -> bool:
        """Delete user's bot credentials"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            result = await repo.delete(user_id)
            await session.commit()
            return result

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[UserBotCredentials]:
        """List all user bot credentials (admin function)"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            return await repo.list_all(limit, offset, status)

    async def count(self, status: str | None = None) -> int:
        """Count total user bots"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            return await repo.count(status)

    async def log_admin_action(self, action: AdminBotAction) -> None:
        """Log admin action"""
        async with self.session_factory() as session:
            repo = UserBotRepository(session)
            await repo.log_admin_action(action)
            await session.commit()
