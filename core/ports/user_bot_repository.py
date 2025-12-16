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

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> UserBotCredentials | None:
        """Get credentials by user ID"""

    @abstractmethod
    async def get_by_id(self, credentials_id: int) -> UserBotCredentials | None:
        """Get credentials by ID"""

    @abstractmethod
    async def update(self, credentials: UserBotCredentials) -> UserBotCredentials:
        """Update credentials"""

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user's bot credentials"""

    @abstractmethod
    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[UserBotCredentials]:
        """List all user bot credentials (admin function)"""

    @abstractmethod
    async def count(self, status: str | None = None) -> int:
        """Count total user bots"""

    @abstractmethod
    async def log_admin_action(self, action: AdminBotAction) -> None:
        """Log admin action"""

    @abstractmethod
    async def get_by_mtproto_phone(self, phone: str) -> UserBotCredentials | None:
        """Get credentials by MTProto phone number (to check for duplicates)"""

    @abstractmethod
    async def get_by_bot_id(self, bot_id: int) -> UserBotCredentials | None:
        """Get credentials by bot ID (to check for duplicates)"""
