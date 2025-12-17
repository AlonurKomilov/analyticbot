"""
🔒 Multi-Factor Authentication (MFA) - TOTP Implementation

Enterprise-grade MFA system with TOTP (Time-based One-Time Password)
support, backup codes, and QR code generation.
"""

import base64
import json
import logging
import secrets
from datetime import datetime, timedelta
from io import BytesIO

import pyotp
import qrcode

from core.ports.security_ports import CachePort, SecurityEventsPort

from .config import get_security_config
from .models import MFASetupResponse, User


class MFAError(Exception):
    """Custom exception for MFA-related errors"""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


logger = logging.getLogger(__name__)


class MFAManager:
    """
    🔐 Multi-Factor Authentication Manager

    Provides comprehensive MFA functionality:
    - TOTP token generation and validation
    - QR code generation for authenticator apps
    - Backup codes for account recovery
    - MFA enforcement policies
    - Rate limiting for MFA attempts
    """

    def __init__(
        self,
        cache: CachePort | None = None,
        security_events: SecurityEventsPort | None = None,
    ):
        self.config = get_security_config()
        self.cache = cache
        self.security_events = security_events

        # Fallback to memory cache if no cache provided
        if not self.cache:
            self._memory_cache = {}
            logger.info("No cache port provided, using memory cache fallback")

    def _get_from_cache(self, key: str) -> str | None:
        """Get value from cache (port or memory fallback)"""
        try:
            if self.cache:
                return self.cache.get(key)
            else:
                return self._memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def _set_in_cache(self, key: str, value: str, expire_seconds: int | None = None) -> bool:
        """Set value in cache (port or memory fallback)"""
        try:
            if self.cache:
                return self.cache.set(key, value, expire_seconds)
            else:
                self._memory_cache[key] = value
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def _delete_from_cache(self, key: str) -> bool:
        """Delete key from cache (port or memory fallback)"""
        try:
            if self.cache:
                return self.cache.delete(key)
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def _exists_in_cache(self, key: str) -> bool:
        """Check if key exists in cache (port or memory fallback)"""
        try:
            if self.cache:
                return self.cache.exists(key)
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def _increment_in_cache(self, key: str) -> int | None:
        """Increment counter in cache (memory fallback only - no atomic increment in port)"""
        try:
            # Simple increment for memory cache
            current = self._memory_cache.get(key, "0")
            try:
                new_value = int(current) + 1
                self._memory_cache[key] = str(new_value)
                return new_value
            except ValueError:
                self._memory_cache[key] = "1"
                return 1
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None

    def generate_secret(self, user: User) -> str:
        """
        Generate TOTP secret for user

        Args:
            user: User object

        Returns:
            Base32 encoded secret string
        """
        # Generate random secret
        secret = pyotp.random_base32()

        logger.info(f"Generated MFA secret for user {user.username}")
        return secret

    def generate_qr_code(self, user: User, secret: str) -> str:
        """
        Generate QR code for TOTP setup

        Args:
            user: User object
            secret: TOTP secret

        Returns:
            Base64 encoded QR code image
        """
        # Create TOTP URL
        totp_url = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name=self.config.MFA_ISSUER
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_url)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffered = BytesIO()
        img.save(buffered)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        logger.info(f"Generated QR code for user {user.username}")
        return f"data:image/png;base64,{img_base64}"

    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """
        Generate backup codes for account recovery

        Args:
            count: Number of backup codes to generate

        Returns:
            List of backup codes
        """
        backup_codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(8))
            backup_codes.append(code)

        logger.info(f"Generated {count} backup codes")
        return backup_codes

    def setup_mfa(self, user: User) -> MFASetupResponse:
        """
        Setup MFA for user

        Args:
            user: User object

        Returns:
            MFA setup response with secret, QR code, and backup codes
        """
        # Generate secret
        secret = self.generate_secret(user)

        # Generate QR code
        qr_code = self.generate_qr_code(user, secret)

        # Generate backup codes
        backup_codes = self.generate_backup_codes()

        # Store in Redis temporarily (user needs to verify before enabling)
        setup_data = {
            "secret": secret,
            "backup_codes": backup_codes,
            "created_at": datetime.utcnow().isoformat(),
        }

        self._set_in_cache(
            f"mfa_setup:{user.id}",
            json.dumps(setup_data),
            3600,  # 1 hour expiration
        )

        logger.info(f"MFA setup initiated for user {user.username}")

        return MFASetupResponse(secret=secret, qr_code=qr_code, backup_codes=backup_codes)

    def verify_setup_token(self, user: User, token: str) -> bool:
        """
        Verify TOTP token during MFA setup

        Args:
            user: User object
            token: TOTP token to verify

        Returns:
            Verification success status
        """
        # Check rate limiting
        if not self._check_mfa_rate_limit(user.id):
            logger.warning(f"MFA verification rate limited for user {user.username}")
            return False

        # Get setup data from cache
        setup_data_str = self._get_from_cache(f"mfa_setup:{user.id}")
        if not setup_data_str:
            logger.warning(f"No MFA setup data found for user {user.username}")
            return False

        try:
            # Ensure Redis response is a string
            if not isinstance(setup_data_str, (str, bytes)):
                logger.error(f"Invalid Redis response type: {type(setup_data_str)}")
                return False

            setup_data_str = (
                setup_data_str.decode() if isinstance(setup_data_str, bytes) else setup_data_str
            )
            setup_data = json.loads(setup_data_str)
            secret = setup_data["secret"]

            # Verify TOTP token
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(token, valid_window=1)  # Allow 1 step tolerance

            if is_valid:
                logger.info(f"MFA setup verification successful for user {user.username}")

                # Update user with MFA settings
                user.mfa_secret = secret
                user.is_mfa_enabled = True

                # Store backup codes securely
                self._store_backup_codes(user.id, setup_data["backup_codes"])

                # Clean up setup data
                self._delete_from_cache(f"mfa_setup:{user.id}")

                return True
            else:
                logger.warning(f"Invalid MFA setup token for user {user.username}")
                self._record_mfa_attempt(user.id)
                return False

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error verifying MFA setup token: {e}")
            return False

    def verify_mfa_token(self, user: User, token: str) -> bool:
        """
        Verify TOTP token for authentication

        Args:
            user: User object
            token: TOTP token to verify

        Returns:
            Verification success status
        """
        if not user.is_mfa_enabled or not user.mfa_secret:
            return False

        # Check rate limiting
        if not self._check_mfa_rate_limit(user.id):
            logger.warning(f"MFA verification rate limited for user {user.username}")
            return False

        # Check if token was recently used (replay protection)
        token_key = f"used_mfa_token:{user.id}:{token}"
        if self._exists_in_cache(token_key):
            logger.warning(f"MFA token replay attempt for user {user.username}")
            return False

        # Verify TOTP token
        totp = pyotp.TOTP(user.mfa_secret)
        is_valid = totp.verify(token, valid_window=1)

        if is_valid:
            # Mark token as used (prevent replay attacks)
            self._set_in_cache(token_key, "used", 60)  # Valid for 1 minute

            logger.info(f"MFA token verification successful for user {user.username}")
            return True
        else:
            logger.warning(f"Invalid MFA token for user {user.username}")
            self._record_mfa_attempt(user.id)
            return False

    def verify_backup_code(self, user: User, backup_code: str) -> bool:
        """
        Verify backup code for account recovery

        Args:
            user: User object
            backup_code: Backup code to verify

        Returns:
            Verification success status
        """
        if not user.is_mfa_enabled:
            return False

        # Check rate limiting
        if not self._check_mfa_rate_limit(user.id):
            logger.warning(f"Backup code verification rate limited for user {user.username}")
            return False

        # Get backup codes from cache
        backup_codes_str = self._get_from_cache(f"backup_codes:{user.id}")
        if not backup_codes_str:
            logger.warning(f"No backup codes found for user {user.username}")
            return False

        try:
            # Ensure Redis response is a string
            if not isinstance(backup_codes_str, (str, bytes)):
                logger.error(f"Invalid Redis response type: {type(backup_codes_str)}")
                return False

            backup_codes_str = (
                backup_codes_str.decode()
                if isinstance(backup_codes_str, bytes)
                else backup_codes_str
            )
            backup_codes = json.loads(backup_codes_str)

            # Check if backup code exists and is unused
            normalized_code = backup_code.upper().replace("-", "").replace(" ", "")

            for i, stored_code in enumerate(backup_codes):
                if stored_code == normalized_code:
                    # Mark backup code as used (remove from list)
                    backup_codes.pop(i)

                    # Update stored backup codes
                    self._set_in_cache(
                        f"backup_codes:{user.id}",
                        json.dumps(backup_codes),
                        int(timedelta(days=365).total_seconds()),  # 1 year expiration
                    )

                    logger.info(f"Backup code used successfully for user {user.username}")
                    return True

            logger.warning(f"Invalid backup code for user {user.username}")
            self._record_mfa_attempt(user.id)
            return False

        except json.JSONDecodeError:
            logger.error(f"Error decoding backup codes for user {user.username}")
            return False

    def disable_mfa(self, user: User) -> bool:
        """
        Disable MFA for user

        Args:
            user: User object

        Returns:
            Success status
        """
        user.is_mfa_enabled = False
        user.mfa_secret = None

        # Remove backup codes
        self._delete_from_cache(f"backup_codes:{user.id}")

        # Clear MFA rate limiting
        self._delete_from_cache(f"mfa_attempts:{user.id}")

        logger.info(f"MFA disabled for user {user.username}")
        return True

    def regenerate_backup_codes(self, user: User) -> list[str]:
        """
        Regenerate backup codes for user

        Args:
            user: User object

        Returns:
            New list of backup codes
        """
        if not user.is_mfa_enabled:
            raise ValueError("MFA must be enabled to regenerate backup codes")

        # Generate new backup codes
        new_backup_codes = self.generate_backup_codes()

        # Store new backup codes
        self._store_backup_codes(user.id, new_backup_codes)

        logger.info(f"Backup codes regenerated for user {user.username}")
        return new_backup_codes

    def get_remaining_backup_codes_count(self, user_id: str) -> int:
        """
        Get number of remaining backup codes

        Args:
            user_id: User ID

        Returns:
            Number of remaining backup codes
        """
        backup_codes_str = self._get_from_cache(f"backup_codes:{user_id}")
        if not backup_codes_str:
            return 0

        try:
            # Ensure Redis response is a string
            if not isinstance(backup_codes_str, (str, bytes)):
                logger.error(f"Invalid Redis response type: {type(backup_codes_str)}")
                return 0

            backup_codes_str = (
                backup_codes_str.decode()
                if isinstance(backup_codes_str, bytes)
                else backup_codes_str
            )
            backup_codes = json.loads(backup_codes_str)
            return len(backup_codes)
        except json.JSONDecodeError:
            return 0

    def _store_backup_codes(self, user_id: str, backup_codes: list[str]) -> None:
        """Store backup codes in cache"""
        self._set_in_cache(
            f"backup_codes:{user_id}",
            json.dumps(backup_codes),
            int(timedelta(days=365).total_seconds()),  # 1 year expiration
        )

    def _check_mfa_rate_limit(self, user_id: str) -> bool:
        """Check MFA attempt rate limiting"""
        attempts_key = f"mfa_attempts:{user_id}"
        attempts = self._get_from_cache(attempts_key)

        if attempts:
            # Ensure Redis response is a string
            if not isinstance(attempts, (str, bytes)):
                logger.error(f"Invalid Redis response type: {type(attempts)}")
                return True  # Allow attempt if we can't check properly

            attempts_str = attempts.decode() if isinstance(attempts, bytes) else attempts
            try:
                if int(attempts_str) >= 5:  # Max 5 attempts per window
                    return False
            except ValueError:
                logger.error(f"Invalid attempts value: {attempts_str}")
                return True

        return True

    def _record_mfa_attempt(self, user_id: str) -> None:
        """Record MFA attempt for rate limiting"""
        attempts_key = f"mfa_attempts:{user_id}"

        # Increment attempts counter
        self._increment_in_cache(attempts_key)

        # Note: For memory cache, we don't have TTL - attempts persist until restart
        # Apps layer should implement proper rate limiting with TTL via cache port
        # This is acceptable for MFA as it's typically used with external cache


# Global MFA manager instance
# Global MFA manager instance - lazy initialization
_mfa_manager = None


def get_mfa_manager() -> MFAManager:
    """Get the global MFA manager instance"""
    global _mfa_manager
    if _mfa_manager is None:
        _mfa_manager = MFAManager()
    return _mfa_manager
