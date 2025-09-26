"""
Verify Email Use Case
"""

from dataclasses import dataclass

from src.identity.domain.repositories.user_repository import UserRepository
from src.shared_kernel.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)


@dataclass
class VerifyEmailCommand:
    """Command to verify user email"""

    token: str


@dataclass
class VerifyEmailResult:
    """Result of email verification"""

    user_id: int
    email: str
    verified: bool = True


class VerifyEmailUseCase:
    """
    Use case for verifying user email address.

    Business Rules:
    - Token must be valid
    - User must exist
    - Account must be pending verification
    """

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, command: VerifyEmailCommand) -> VerifyEmailResult:
        """Execute email verification"""

        # Find user by verification token
        user = await self._user_repository.get_by_verification_token(command.token)
        if not user:
            raise EntityNotFoundError("User", f"verification_token:{command.token}")

        # Verify the token
        if not user.verify_email_token(command.token):
            raise BusinessRuleViolationError("Invalid verification token")

        # Activate account
        user.activate_account()
        user.email_verification_token = None  # Clear used token

        # Save user
        await self._user_repository.save(user)

        return VerifyEmailResult(user_id=user.id.value, email=str(user.email), verified=True)
