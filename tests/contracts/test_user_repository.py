"""
Repository Contract Tests
Tests that ensure all repository implementations follow the same contract
"""

from typing import Protocol, runtime_checkable

import pytest

from core.repositories.interfaces import UserRepository


@runtime_checkable  
class UserRepositoryContract(Protocol):
    """Contract that all UserRepository implementations must follow"""
    
    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID"""
        ...
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID"""  
        ...
    
    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        ...
    
    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        ...
    
    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        ...
    
    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        ...


class UserRepositoryContractTests:
    """
    Base test class for UserRepository implementations
    All concrete implementations should inherit and run these tests
    """
    
    @pytest.fixture
    def repository(self) -> UserRepository:
        """Override this in concrete test classes"""
        raise NotImplementedError("Must provide repository fixture")
    
    async def test_user_lifecycle(self, repository: UserRepository):
        """Test complete user lifecycle: create -> read -> update -> exists -> delete"""
        
        # Test user creation
        user_data = {
            "id": 123456,
            "username": "test_user",
            "plan_id": 1
        }
        created_user = await repository.create_user(user_data)
        assert created_user is not None
        assert created_user["id"] == 123456
        assert created_user["username"] == "test_user"
        
        # Test user exists
        exists = await repository.user_exists(123456)
        assert exists is True
        
        # Test get user by ID
        retrieved_user = await repository.get_user_by_id(123456)
        assert retrieved_user is not None
        assert retrieved_user["id"] == 123456
        assert retrieved_user["username"] == "test_user"
        
        # Test get user by Telegram ID (should be same as ID for bot)
        telegram_user = await repository.get_user_by_telegram_id(123456)
        assert telegram_user is not None
        assert telegram_user["id"] == 123456
        
        # Test user update
        updated = await repository.update_user(123456, username="updated_user")
        assert updated is True
        
        # Verify update
        updated_user = await repository.get_user_by_id(123456)
        assert updated_user["username"] == "updated_user"
        
        # Test subscription tier
        tier = await repository.get_user_subscription_tier(123456)
        assert isinstance(tier, str)
    
    async def test_nonexistent_user(self, repository: UserRepository):
        """Test behavior with non-existent users"""
        
        # Test get non-existent user
        user = await repository.get_user_by_id(999999)
        assert user is None
        
        # Test exists for non-existent user
        exists = await repository.user_exists(999999)
        assert exists is False
        
        # Test update non-existent user
        updated = await repository.update_user(999999, username="nonexistent")
        assert updated is False
    
    async def test_subscription_tier_fallback(self, repository: UserRepository):
        """Test subscription tier fallback for unknown users"""
        tier = await repository.get_user_subscription_tier(999999)
        # Should return default tier for non-existent users
        assert tier in ["free", "pro", "enterprise"]  # Valid tier values
    
    def test_repository_implements_protocol(self, repository: UserRepository):
        """Test that repository implements the protocol correctly"""
        assert isinstance(repository, UserRepositoryContract)


# Example of how to use this for a concrete implementation:
# 
# class TestAsyncpgUserRepository(UserRepositoryContractTests):
#     
#     @pytest.fixture
#     async def repository(self, asyncpg_pool):
#         return AsyncpgUserRepository(asyncpg_pool)
#     
#     # Inherit all contract tests automatically
#     # Add implementation-specific tests here if needed
