"""
Authenticate User Use Case
"""

from dataclasses import dataclass
from typing import Optional
from src.identity.domain.entities.user import User, UserStatus
from src.identity.domain.repositories.user_repository import UserRepository
from src.shared_kernel.domain.value_objects import EmailAddress
from src.shared_kernel.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError


@dataclass
class AuthenticateUserCommand:
    """Command to authenticate a user"""
    email: str
    password: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class AuthenticateUserResult:
    """Result of user authentication"""
    user_id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    status: str
    requires_mfa: bool = False


class AuthenticateUserUseCase:
    """
    Use case for authenticating a user.
    
    Business Rules:
    - User must exist
    - Password must be correct
    - Account must not be locked
    - Account must have active or pending verification status
    - Failed attempts should be tracked
    """
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, command: AuthenticateUserCommand) -> AuthenticateUserResult:
        """Execute user authentication"""
        email = EmailAddress(command.email)
        
        # Find user
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise EntityNotFoundError("User", command.email)
        
        # Check if account is locked
        if user.is_account_locked():
            raise BusinessRuleViolationError("Account is locked due to failed login attempts")
        
        # Verify password
        if not user.verify_password(command.password):
            # Record failed attempt
            user.record_failed_login()
            await self._user_repository.save(user)
            raise BusinessRuleViolationError("Invalid password")
        
        # Check account status
        if user.status not in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION]:
            raise BusinessRuleViolationError(f"Cannot login with status: {user.status.value}")
        
        # Record successful login
        user.login(command.ip_address)
        await self._user_repository.save(user)
        
        return AuthenticateUserResult(
            user_id=user.id.value,
            email=str(user.email),
            username=str(user.username),
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            requires_mfa=user.is_mfa_enabled
        )
