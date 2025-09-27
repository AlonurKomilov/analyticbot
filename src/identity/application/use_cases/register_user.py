"""
Register User Use Case
"""

from dataclasses import dataclass

from ....shared_kernel.domain.exceptions import (
    EntityAlreadyExistsError,
    ValidationError,
)
from ....shared_kernel.domain.value_objects import EmailAddress, UserId, Username
from ...domain.entities.user import AuthProvider, User
from ...domain.repositories.user_repository import UserRepository


@dataclass
class RegisterUserCommand:
    """Command to register a new user"""

    email: str
    username: str
    password: str | None = None
    full_name: str | None = None
    auth_provider: str = AuthProvider.LOCAL.value


@dataclass
class RegisterUserResult:
    """Result of user registration"""

    user_id: int
    email: str
    username: str
    verification_token: str | None = None
    requires_verification: bool = True


class RegisterUserUseCase:
    """
    Use case for registering a new user.

    Business Rules:
    - Email must be unique
    - Username must be unique
    - Local auth users must provide a password
    - External auth users don't need passwords
    """

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        """Execute user registration"""
        # Validate input
        email = EmailAddress(command.email)
        username = Username(command.username)
        auth_provider = AuthProvider(command.auth_provider)

        # Check business rules
        await self._validate_unique_email(email)
        await self._validate_unique_username(username)

        if auth_provider == AuthProvider.LOCAL and not command.password:
            raise ValidationError("Password is required for local authentication")

        # Generate user ID (in a real system, this might come from a sequence)
        user_id = UserId(hash(command.email) % (10**9))  # Simple ID generation

        # Create user
        user = User.create_new_user(
            user_id=user_id,
            email=email,
            username=username,
            password=command.password,
            full_name=command.full_name,
            auth_provider=auth_provider,
        )

        # Generate verification token for local auth
        verification_token = None
        requires_verification = False

        if auth_provider == AuthProvider.LOCAL:
            verification_token = user.generate_verification_token()
            requires_verification = True

        # Save user
        await self._user_repository.save(user)

        return RegisterUserResult(
            user_id=user_id.value,
            email=str(email),
            username=str(username),
            verification_token=verification_token,
            requires_verification=requires_verification,
        )

    async def _validate_unique_email(self, email: EmailAddress) -> None:
        """Validate that email is not already registered"""
        if await self._user_repository.email_exists(email):
            raise EntityAlreadyExistsError("User", "email", str(email))

    async def _validate_unique_username(self, username: Username) -> None:
        """Validate that username is not already taken"""
        if await self._user_repository.username_exists(username):
            raise EntityAlreadyExistsError("User", "username", str(username))
