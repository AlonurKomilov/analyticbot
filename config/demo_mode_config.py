"""
Central Demo Mode Configuration
Unified configuration management for all demo/mock switching logic
"""

from enum import Enum
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class DemoModeStrategy(str, Enum):
    """Demo mode detection strategies"""
    DISABLED = "disabled"
    EMAIL_BASED = "email_based"
    USER_FLAG_BASED = "user_flag_based"
    ENVIRONMENT_BASED = "environment_based"


class DemoModeConfig(BaseSettings):
    """
    Central Demo Mode Configuration
    Single source of truth for all demo/mock switching logic
    """
    
    # ============================================================================
    # CORE DEMO MODE STRATEGY
    # ============================================================================
    DEMO_MODE_STRATEGY: DemoModeStrategy = DemoModeStrategy.EMAIL_BASED
    DEMO_MODE_ENABLED: bool = True
    FORCE_DEMO_MODE: bool = False  # Override for testing
    
    # ============================================================================
    # SERVICE SWITCHING CONFIGURATION
    # ============================================================================
    USE_MOCK_ANALYTICS: bool = False
    USE_MOCK_PAYMENT: bool = False
    USE_MOCK_DATABASE: bool = False
    USE_MOCK_AI_SERVICES: bool = False
    USE_MOCK_TELEGRAM_API: bool = False
    USE_MOCK_EMAIL_DELIVERY: bool = True
    USE_MOCK_AUTH: bool = True
    USE_MOCK_ADMIN: bool = True
    USE_MOCK_DEMO_DATA: bool = True
    
    # ============================================================================
    # DEMO USER DETECTION RULES
    # ============================================================================
    DEMO_EMAIL_PATTERNS: List[str] = Field(
        default=["demo@", "viewer@", "guest@", "test@"]
    )
    DEMO_USER_IDS: List[int] = Field(default=[])
    DEMO_USERNAMES: List[str] = Field(
        default=["demo_user", "test_user", "viewer"]
    )
    
    # ============================================================================
    # MOCK BEHAVIOR CONFIGURATION
    # ============================================================================
    MOCK_API_DELAY_MS: int = 300
    MOCK_SUCCESS_RATE: float = 0.95
    MOCK_REALISTIC_DELAYS: bool = True
    MOCK_ERROR_SIMULATION: bool = False
    MOCK_CACHE_ENABLED: bool = True
    MOCK_CACHE_TTL_SECONDS: int = 300
    
    # ============================================================================
    # DEMO DATA CONFIGURATION
    # ============================================================================
    DEMO_POSTS_COUNT: int = 25
    DEMO_METRICS_DAYS: int = 30
    DEMO_TOP_POSTS_LIMIT: int = 10
    DEMO_CHANNEL_COUNT: int = 5
    DEMO_USER_COUNT: int = 100
    
    # ============================================================================
    # ENVIRONMENT-SPECIFIC OVERRIDES
    # ============================================================================
    DEVELOPMENT_FORCE_DEMO: bool = False
    TESTING_FORCE_MOCK: bool = False
    PRODUCTION_DISABLE_DEMO: bool = True
    
    class Config:
        """Pydantic configuration"""
        env_prefix = "DEMO_"
        case_sensitive = True
        
    def is_demo_enabled(self) -> bool:
        """Check if demo mode is enabled"""
        if self.FORCE_DEMO_MODE:
            return True
        return self.DEMO_MODE_ENABLED and self.DEMO_MODE_STRATEGY != DemoModeStrategy.DISABLED
    
    def should_use_mock_service(self, service_name: str) -> bool:
        """Check if a specific service should use mock implementation"""
        service_flags = {
            "analytics": self.USE_MOCK_ANALYTICS,
            "payment": self.USE_MOCK_PAYMENT,
            "database": self.USE_MOCK_DATABASE,
            "ai_services": self.USE_MOCK_AI_SERVICES,
            "telegram_api": self.USE_MOCK_TELEGRAM_API,
            "email_delivery": self.USE_MOCK_EMAIL_DELIVERY,
            "auth": self.USE_MOCK_AUTH,
            "admin": self.USE_MOCK_ADMIN,
            "demo_data": self.USE_MOCK_DEMO_DATA,
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


# Global demo mode configuration instance
demo_config = DemoModeConfig()