"""
User Bot Credentials Repository Interface
"""

from abc import ABC, abstractmethod

from core.models.user_bot_domain import AdminBotAction, UserBotCredentials


class IUserBotRepository(ABC):
    """Repository interface for user bot credentials"""

    @abstractmethod
    async def create(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Create new user bot credentials"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> UserBotCredentials | None:
        """Get credentials by user ID"""
        pass

    @abstractmethod
    async def get_by_id(self, credentials_id: int) -> UserBotCredentials | None:
        """Get credentials by ID"""
        pass

    @abstractmethod
    async def update(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Update credentials"""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user's bot credentials"""
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[UserBotCredentials]:
        """List all user bot credentials (admin function)"""
        pass

    @abstractmethod
    async def count(self, status: str | None = None) -> int:
        """Count total user bots"""
        pass

    @abstractmethod
    async def log_admin_action(self, action: AdminBotAction) -> None:
        """Log admin action"""
        pass
