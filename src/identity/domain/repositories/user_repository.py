"""
User Repository Interface - Port for data access
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.identity.domain.entities.user import User
from src.shared_kernel.domain.value_objects import UserId, EmailAddress, Username
from src.shared_kernel.infrastructure.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserId], ABC):
    """
    Repository interface for User aggregate.
    
    This defines the contract for user data access operations
    without specifying the implementation details.
    """
    
    @abstractmethod
    async def get_by_email(self, email: EmailAddress) -> Optional[User]:
        """Find user by email address"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: Username) -> Optional[User]:
        """Find user by username"""
        pass
    
    @abstractmethod
    async def get_by_provider_id(self, provider: str, provider_id: str) -> Optional[User]:
        """Find user by external provider ID"""
        pass
    
    @abstractmethod
    async def email_exists(self, email: EmailAddress) -> bool:
        """Check if email is already registered"""
        pass
    
    @abstractmethod
    async def username_exists(self, username: Username) -> bool:
        """Check if username is already taken"""
        pass
    
    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Find user by email verification token"""
        pass
    
    @abstractmethod
    async def get_by_reset_token(self, token: str) -> Optional[User]:
        """Find user by password reset token"""
        pass
    
    @abstractmethod
    async def get_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get active users with pagination"""
        pass
