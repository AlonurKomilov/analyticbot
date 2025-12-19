"""
Token Validator - Bot Token Validation

Validates Telegram bot tokens for format and connectivity.
Provides proactive validation to prevent runtime errors.

Domain: Bot token validation and verification
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError

logger = logging.getLogger(__name__)


class TokenValidationStatus(Enum):
    """Token validation status"""
    VALID = "valid"
    INVALID_FORMAT = "invalid_format"
    UNAUTHORIZED = "unauthorized"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    REVOKED = "revoked"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class TokenValidationResult:
    """Result of token validation"""
    is_valid: bool
    status: TokenValidationStatus
    message: str
    bot_username: str | None = None
    bot_id: int | None = None
    validated_at: datetime = None

    def __post_init__(self):
        if self.validated_at is None:
            self.validated_at = datetime.now()


class TokenValidator:
    """
    Validates Telegram bot tokens

    Features:
    - Format validation (regex check)
    - Live validation (test connection)
    - Bot info retrieval
    - Error categorization
    - Connection timeout handling
    """

    # Bot token format: numeric_id:alphanumeric_secret (35 chars)
    TOKEN_PATTERN = re.compile(r'^(\d+):([A-Za-z0-9_-]{35,})$')

    # Validation timeout
    VALIDATION_TIMEOUT_SECONDS = 10

    def __init__(self, shared_session=None):
        """
        Initialize token validator

        Args:
            shared_session: Optional shared aiohttp session for efficiency
        """
        self.shared_session = shared_session

    def validate_format(self, token: str) -> TokenValidationResult:
        """
        Validate token format without connecting to Telegram

        Format: numeric_bot_id:alphanumeric_secret
        Example: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567

        Args:
            token: Bot token to validate

        Returns:
            TokenValidationResult with format validation status
        """
        if not token or not isinstance(token, str):
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.INVALID_FORMAT,
                message="Token must be a non-empty string"
            )

        # Check format: number:string
        if ':' not in token:
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.INVALID_FORMAT,
                message="Invalid token format. Expected format: numeric_id:alphanumeric_secret"
            )

        parts = token.split(':', 1)
        if len(parts) != 2:
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.INVALID_FORMAT,
                message="Invalid token format. Expected format: numeric_id:alphanumeric_secret"
            )

        bot_id_str, secret = parts

        # Validate bot ID is numeric
        if not bot_id_str.isdigit():
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.INVALID_FORMAT,
                message="Bot ID must be numeric"
            )

        # Validate secret length and characters
        if len(secret) < 35:
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.INVALID_FORMAT,
                message=f"Token secret too short. Expected at least 35 characters, got {len(secret)}"
            )

        # Check if secret contains only valid characters (alphanumeric, underscore, hyphen)
        if not re.match(r'^[A-Za-z0-9_-]+$', secret):
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.INVALID_FORMAT,
                message="Token secret contains invalid characters. Only alphanumeric, underscore, and hyphen allowed"
            )

        # All checks passed
        return TokenValidationResult(
            is_valid=True,
            status=TokenValidationStatus.VALID,
            message="Token format is valid",
            bot_id=int(bot_id_str)
        )

    async def validate_live(
        self,
        token: str,
        timeout_seconds: int | None = None
    ) -> TokenValidationResult:
        """
        Validate token by testing connection to Telegram

        Args:
            token: Bot token string
            timeout_seconds: Optional custom timeout (default: 10 seconds)

        Returns:
            TokenValidationResult with live validation status
        """
        # First check format
        format_result = self.validate_format(token)
        if not format_result.is_valid:
            return format_result

        timeout = timeout_seconds or self.VALIDATION_TIMEOUT_SECONDS

        bot = None
        try:
            # Create bot instance
            if self.shared_session:
                session = AiohttpSession(self.shared_session)
                bot = Bot(token=token, session=session)
            else:
                bot = Bot(token=token)

            # Test connection with timeout
            bot_info = await asyncio.wait_for(
                bot.get_me(),
                timeout=timeout
            )

            return TokenValidationResult(
                is_valid=True,
                status=TokenValidationStatus.VALID,
                message=f"Token is valid for bot @{bot_info.username}",
                bot_username=bot_info.username,
                bot_id=bot_info.id
            )

        except TelegramUnauthorizedError as e:
            # Token is unauthorized or revoked
            error_msg = str(e).lower()
            if "revoked" in error_msg or "terminated" in error_msg:
                return TokenValidationResult(
                    is_valid=False,
                    status=TokenValidationStatus.REVOKED,
                    message="Token has been revoked or bot was deleted"
                )
            else:
                return TokenValidationResult(
                    is_valid=False,
                    status=TokenValidationStatus.UNAUTHORIZED,
                    message="Token is unauthorized. Please check your token from @BotFather"
                )

        except TimeoutError:
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.TIMEOUT,
                message=f"Validation timeout after {timeout} seconds. Please try again"
            )

        except TelegramNetworkError as e:
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.NETWORK_ERROR,
                message=f"Network error during validation: {str(e)}"
            )

        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}", exc_info=True)
            return TokenValidationResult(
                is_valid=False,
                status=TokenValidationStatus.UNKNOWN_ERROR,
                message=f"Validation failed: {str(e)}"
            )

        finally:
            # Clean up bot instance
            if bot:
                try:
                    await bot.session.close()
                except Exception as e:
                    logger.warning(f"Error closing bot session during validation: {e}")

    async def validate(
        self,
        token: str,
        live_check: bool = True,
        timeout_seconds: int | None = None
    ) -> TokenValidationResult:
        """
        Validate token with optional live check

        Args:
            token: Bot token string
            live_check: Whether to perform live validation (default: True)
            timeout_seconds: Optional custom timeout for live check

        Returns:
            TokenValidationResult with validation status
        """
        if not live_check:
            return self.validate_format(token)

        return await self.validate_live(token, timeout_seconds)


class PeriodicTokenValidator:
    """
    Background service for periodic token validation

    Checks token validity for existing bots to detect:
    - Revoked tokens
    - Expired tokens
    - Token ownership changes
    """

    def __init__(
        self,
        validator: TokenValidator,
        check_interval_hours: int = 24,
        max_consecutive_failures: int = 3
    ):
        """
        Initialize periodic validator

        Args:
            validator: TokenValidator instance
            check_interval_hours: How often to check tokens (default: 24 hours)
            max_consecutive_failures: Failures before marking bot as invalid
        """
        self.validator = validator
        self.check_interval = timedelta(hours=check_interval_hours)
        self.max_consecutive_failures = max_consecutive_failures

        # Track validation state
        self.last_validation: dict[int, datetime] = {}
        self.consecutive_failures: dict[int, int] = {}
        self.is_running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start periodic validation task"""
        if self.is_running:
            logger.warning("Periodic token validation already running")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._validation_loop())
        logger.info("Periodic token validation started")

    async def stop(self):
        """Stop periodic validation task"""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Periodic token validation stopped")

    async def _validation_loop(self):
        """Background loop for periodic validation"""
        while self.is_running:
            try:
                await self._validate_all_tokens()
                await asyncio.sleep(self.check_interval.total_seconds())
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic validation loop: {e}", exc_info=True)
                # Wait a bit before retrying
                await asyncio.sleep(300)  # 5 minutes

    async def _validate_all_tokens(self):
        """Validate all registered bot tokens"""
        # This will be implemented when we integrate with UserBotManager
        # For now, it's a placeholder for the architecture
        logger.debug("Periodic token validation cycle")
        # TODO: Get all active bots from UserBotManager
        # TODO: Validate each token
        # TODO: Update health status for invalid tokens
        # TODO: Notify users of invalid tokens
        pass

    async def validate_token(self, user_id: int, token: str) -> TokenValidationResult:
        """
        Validate a single token and track results

        Args:
            user_id: User ID associated with the token
            token: Bot token to validate

        Returns:
            TokenValidationResult
        """
        result = await self.validator.validate(token)

        # Update tracking
        self.last_validation[user_id] = datetime.now()

        if result.is_valid:
            # Reset failure count on success
            self.consecutive_failures[user_id] = 0
        else:
            # Increment failure count
            current_failures = self.consecutive_failures.get(user_id, 0)
            self.consecutive_failures[user_id] = current_failures + 1

            # Check if we've exceeded max failures
            if self.consecutive_failures[user_id] >= self.max_consecutive_failures:
                logger.warning(
                    f"User {user_id} has {self.consecutive_failures[user_id]} "
                    f"consecutive token validation failures"
                )

        return result

    def should_validate(self, user_id: int) -> bool:
        """
        Check if token should be validated now

        Args:
            user_id: User ID to check

        Returns:
            True if validation is due
        """
        last_check = self.last_validation.get(user_id)
        if not last_check:
            return True

        time_since_check = datetime.now() - last_check
        return time_since_check >= self.check_interval

    def get_failure_count(self, user_id: int) -> int:
        """Get consecutive failure count for user"""
        return self.consecutive_failures.get(user_id, 0)

    def reset_failures(self, user_id: int):
        """Reset failure count for user"""
        self.consecutive_failures[user_id] = 0


# Global validator instance
_token_validator: TokenValidator | None = None
_periodic_validator: PeriodicTokenValidator | None = None


def get_token_validator() -> TokenValidator:
    """Get global token validator instance"""
    global _token_validator
    if _token_validator is None:
        _token_validator = TokenValidator()
    return _token_validator


def initialize_periodic_validator(
    check_interval_hours: int = 24,
    max_consecutive_failures: int = 3
) -> PeriodicTokenValidator:
    """
    Initialize global periodic validator

    Args:
        check_interval_hours: Validation interval (default: 24 hours)
        max_consecutive_failures: Failures before flagging (default: 3)

    Returns:
        PeriodicTokenValidator instance
    """
    global _periodic_validator
    validator = get_token_validator()
    _periodic_validator = PeriodicTokenValidator(
        validator=validator,
        check_interval_hours=check_interval_hours,
        max_consecutive_failures=max_consecutive_failures
    )
    return _periodic_validator


def get_periodic_validator() -> PeriodicTokenValidator | None:
    """Get global periodic validator instance"""
    return _periodic_validator
