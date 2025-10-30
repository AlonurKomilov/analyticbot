"""
🔒 Security Configuration - Production Settings

Enterprise-grade security configuration with environment variables
and production-ready defaults.

Framework-free configuration class for Clean Architecture compliance.
"""

import json
import os
import secrets
import warnings
from dataclasses import dataclass, field


def generate_secure_key() -> str:
    """Generate a cryptographically secure random key"""
    return secrets.token_urlsafe(32)


@dataclass
class SecurityConfig:
    """
    🛡️ Security Configuration

    All security-related settings with production defaults.
    Framework-free configuration for Clean Architecture compliance.
    """

    # JWT Configuration - Generate secure defaults if not provided
    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY") or generate_secure_key()
    )
    REFRESH_SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("JWT_REFRESH_SECRET_KEY") or generate_secure_key()
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Normal tokens: 7 days, Remember me: 30 days

    # Redis Configuration - Production Environment 10xxx
    REDIS_HOST: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    REDIS_PORT: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "10200")))
    REDIS_DB: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    REDIS_PASSWORD: str | None = field(default_factory=lambda: os.getenv("REDIS_PASSWORD"))

    # OAuth Configuration - Production Environment 10xxx
    GOOGLE_CLIENT_ID: str | None = field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID"))
    GOOGLE_CLIENT_SECRET: str | None = field(
        default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET")
    )
    GITHUB_CLIENT_ID: str | None = field(default_factory=lambda: os.getenv("GITHUB_CLIENT_ID"))
    GITHUB_CLIENT_SECRET: str | None = field(
        default_factory=lambda: os.getenv("GITHUB_CLIENT_SECRET")
    )
    OAUTH_REDIRECT_URL: str = field(
        default_factory=lambda: os.getenv(
            "OAUTH_REDIRECT_URL", "http://localhost:10300/auth/callback"
        )
    )

    # Security Policies
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_MIXED_CASE: bool = True

    # Session Configuration
    SESSION_EXPIRE_HOURS: int = 24
    MAX_CONCURRENT_SESSIONS: int = 5
    SESSION_EXTEND_ON_ACTIVITY: bool = True

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_MINUTES: int = 15

    # MFA Configuration
    MFA_ISSUER: str = "AnalyticBot"
    MFA_TOKEN_LENGTH: int = 6
    MFA_TOKEN_INTERVAL: int = 30

    # CORS Configuration - Production Environment 10xxx
    CORS_ORIGINS: str | list[str] = field(
        default_factory=lambda: [
            "http://localhost:10400",
            "http://localhost:10300",
            "http://localhost:11400",
            "http://localhost:11300",
            "https://yourdomain.com",
        ]
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    CORS_ALLOW_HEADERS: list[str] = field(default_factory=lambda: ["*"])

    # Email Configuration (for verification)
    SMTP_SERVER: str | None = field(default_factory=lambda: os.getenv("SMTP_SERVER"))
    SMTP_PORT: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    SMTP_USERNAME: str | None = field(default_factory=lambda: os.getenv("SMTP_USERNAME"))
    SMTP_PASSWORD: str | None = field(default_factory=lambda: os.getenv("SMTP_PASSWORD"))
    EMAIL_FROM: str = field(
        default_factory=lambda: os.getenv("EMAIL_FROM", "noreply@analyticbot.com")
    )

    # Security Headers
    SECURITY_HEADERS: dict = field(
        default_factory=lambda: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
    )

    # Audit Logging
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FILE: str = "logs/security_audit.log"

    # Encryption
    ENCRYPTION_KEY: str | None = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY"))

    def __post_init__(self):
        """Post-initialization validation and processing"""
        # Parse CORS_ORIGINS if it's a string
        self.CORS_ORIGINS = self._parse_cors_origins(self.CORS_ORIGINS)

        # Validate secret keys
        self._validate_secret_keys()

    def _parse_cors_origins(self, v) -> list[str]:
        """Parse CORS_ORIGINS from string or list format"""
        # Handle None or empty values
        if not v:
            return [
                "http://localhost:10400",
                "http://localhost:10300",
                "http://localhost:11400",
                "http://localhost:11300",
                "https://yourdomain.com",
            ]

        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return [
                    "http://localhost:10400",
                    "http://localhost:10300",
                    "http://localhost:11400",
                    "http://localhost:11300",
                    "https://yourdomain.com",
                ]

            # Try to parse as JSON first (for bracket format)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass

            # Handle comma-separated string format
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            # Handle list format
            return v
        else:
            # Return default if neither
            return [
                "http://localhost:10400",
                "http://localhost:10300",
                "http://localhost:11400",
                "http://localhost:11300",
                "https://yourdomain.com",
            ]

    def _validate_secret_keys(self):
        """Validate secret keys are properly set"""
        for key_name, key_value in [
            ("SECRET_KEY", self.SECRET_KEY),
            ("REFRESH_SECRET_KEY", self.REFRESH_SECRET_KEY),
        ]:
            # Only warn if using old default values, not auto-generated ones
            if key_value in [
                "your-super-secret-key-change-in-production",
                "your-refresh-secret-key-change-in-production",
            ]:
                warnings.warn(
                    "⚠️  WARNING: Using default secret keys! Set JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY environment variables for production!",
                    category=RuntimeWarning,
                    stacklevel=3,
                )
            if len(key_value) < 32:
                raise ValueError(f"{key_name} must be at least 32 characters long")

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create configuration instance from environment variables"""
        return cls()


# Global configuration instance - lazy initialization
_security_config = None


def get_security_config() -> SecurityConfig:
    """Get the global security configuration instance"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig.from_env()
    return _security_config
