"""
🔒 Security Configuration - Production Settings

Enterprise-grade security configuration with environment variables
and production-ready defaults.
"""

import os
import secrets
import warnings

from pydantic import field_validator
from pydantic_settings import BaseSettings


def generate_secure_key() -> str:
    """Generate a cryptographically secure random key"""
    return secrets.token_urlsafe(32)


class SecurityConfig(BaseSettings):
    """
    🛡️ Security Configuration

    All security-related settings with production defaults
    """

    # JWT Configuration - Generate secure defaults if not provided
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or generate_secure_key()
    REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY") or generate_secure_key()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")

    # OAuth Configuration
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID: str | None = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: str | None = os.getenv("GITHUB_CLIENT_SECRET")
    OAUTH_REDIRECT_URL: str = os.getenv("OAUTH_REDIRECT_URL", "http://localhost:8000/auth/callback")

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

    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Email Configuration (for verification)
    SMTP_SERVER: str | None = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@analyticbot.com")

    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # Audit Logging
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FILE: str = "logs/security_audit.log"

    # Encryption
    ENCRYPTION_KEY: str | None = os.getenv("ENCRYPTION_KEY")

    @field_validator("SECRET_KEY", "REFRESH_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v):
        """Validate secret keys are properly set"""
        # Only warn if using old default values, not auto-generated ones
        if v in [
            "your-super-secret-key-change-in-production",
            "your-refresh-secret-key-change-in-production",
        ]:
            warnings.warn(
                "⚠️  WARNING: Using default secret keys! Set JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY environment variables for production!",
                category=RuntimeWarning,
                stacklevel=2,
            )
        if len(v) < 32:
            raise ValueError("Secret keys must be at least 32 characters long")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Global configuration instance
security_config = SecurityConfig()
