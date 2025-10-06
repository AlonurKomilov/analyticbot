"""
Demo Configuration
==================

Central configuration for all user-facing demonstration functionality.
Controls how the project showcases its capabilities to new users.
"""

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings


class DemoStrategy(str, Enum):
    """Demo user detection strategies"""

    DISABLED = "disabled"
    EMAIL_BASED = "email_based"
    USER_FLAG_BASED = "user_flag_based"
    ENVIRONMENT_BASED = "environment_based"


class DemoConfig(BaseSettings):
    """
    Central Demo Configuration
    Single source of truth for all demonstration and showcase functionality
    """

    # ============================================================================
    # CORE DEMO STRATEGY
    # ============================================================================
    DEMO_STRATEGY: DemoStrategy = DemoStrategy.EMAIL_BASED
    DEMO_ENABLED: bool = True
    FORCE_DEMO_MODE: bool = False  # Override for testing

    # ============================================================================
    # SHOWCASE SERVICE CONFIGURATION
    # ============================================================================
    USE_SAMPLE_ANALYTICS: bool = True
    USE_SAMPLE_PAYMENT: bool = True
    USE_SAMPLE_DATABASE: bool = False
    USE_SAMPLE_AI_SERVICES: bool = True
    USE_SAMPLE_TELEGRAM_API: bool = False
    USE_SAMPLE_EMAIL_DELIVERY: bool = True
    USE_SAMPLE_AUTH: bool = True
    USE_SAMPLE_ADMIN: bool = True
    USE_SAMPLE_DATA: bool = True

    # ============================================================================
    # DEMO USER DETECTION RULES
    # ============================================================================
    DEMO_EMAIL_PATTERNS: list[str] = Field(
        default=["demo@", "viewer@", "guest@", "test@", "showcase@"]
    )
    DEMO_USER_IDS: list[int] = Field(default=[])
    DEMO_USERNAMES: list[str] = Field(default=["demo_user", "showcase_user", "viewer", "guest"])

    # ============================================================================
    # SHOWCASE BEHAVIOR CONFIGURATION
    # ============================================================================
    DEMO_API_DELAY_MS: int = 300
    DEMO_SUCCESS_RATE: float = 0.98  # High success rate for good impression
    DEMO_REALISTIC_DELAYS: bool = True
    DEMO_ERROR_SIMULATION: bool = False  # Don't show errors to demo users
    DEMO_CACHE_ENABLED: bool = True
    DEMO_CACHE_TTL_SECONDS: int = 600  # Cache demo data longer

    # ============================================================================
    # SAMPLE DATA CONFIGURATION
    # ============================================================================
    DEMO_POSTS_COUNT: int = 50
    DEMO_METRICS_DAYS: int = 30
    DEMO_TOP_POSTS_LIMIT: int = 15
    DEMO_CHANNEL_COUNT: int = 8
    DEMO_USER_COUNT: int = 250
    DEMO_ANALYTICS_RICHNESS: str = "high"  # high, medium, basic

    # ============================================================================
    # ENVIRONMENT-SPECIFIC OVERRIDES
    # ============================================================================
    DEVELOPMENT_FORCE_DEMO: bool = False
    TESTING_DISABLE_DEMO: bool = False
    PRODUCTION_DISABLE_DEMO: bool = True

    class Config:
        """Pydantic configuration"""

        env_prefix = "DEMO_"
        case_sensitive = True

    def is_demo_enabled(self) -> bool:
        """Check if demo mode is enabled"""
        if self.FORCE_DEMO_MODE:
            return True
        return self.DEMO_ENABLED and self.DEMO_STRATEGY != DemoStrategy.DISABLED

    def should_use_sample_service(self, service_name: str) -> bool:
        """Check if a specific service should use sample implementation for demo"""
        service_flags = {
            "analytics": self.USE_SAMPLE_ANALYTICS,
            "payment": self.USE_SAMPLE_PAYMENT,
            "database": self.USE_SAMPLE_DATABASE,
            "ai_services": self.USE_SAMPLE_AI_SERVICES,
            "telegram_api": self.USE_SAMPLE_TELEGRAM_API,
            "email_delivery": self.USE_SAMPLE_EMAIL_DELIVERY,
            "auth": self.USE_SAMPLE_AUTH,
            "admin": self.USE_SAMPLE_ADMIN,
            "demo_data": self.USE_SAMPLE_DATA,
        }
        return service_flags.get(service_name.lower(), False)

    def is_demo_email(self, email: str) -> bool:
        """Check if email matches demo patterns"""
        if not email:
            return False
        email_lower = email.lower()
        return any(pattern in email_lower for pattern in self.DEMO_EMAIL_PATTERNS)

    def is_demo_user_id(self, user_id: int) -> bool:
        """Check if user ID is in demo list"""
        return user_id in self.DEMO_USER_IDS

    def is_demo_username(self, username: str) -> bool:
        """Check if username is in demo list"""
        return username.lower() in [u.lower() for u in self.DEMO_USERNAMES]

    def get_demo_quality_level(self) -> str:
        """Get the quality level for demo data generation"""
        return self.DEMO_ANALYTICS_RICHNESS


# Global demo configuration instance
demo_config = DemoConfig()

# Backward compatibility - maintain old import path for transition period
DemoModeConfig = DemoConfig  # Allow old class name
DemoModeStrategy = DemoStrategy  # Allow old enum name
