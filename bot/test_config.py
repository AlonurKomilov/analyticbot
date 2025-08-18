"""
🔧 SIMPLIFIED TEST CONFIGURATION
Test-specific configuration for performance testing
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Simplified settings for performance testing"""
    
    # Bot token (can be test token)
    BOT_TOKEN: str = "test_token_for_performance_testing"
    
    # Database settings with defaults for testing
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "analyticbot_test"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Redis settings with defaults
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Environment
    ENVIRONMENT: str = "test"
    LOG_LEVEL: str = "INFO"
    
    @property
    def DATABASE_URL(self) -> str:
        """Build database URL from components"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property  
    def REDIS_URL(self) -> str:
        """Build Redis URL from components"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create test settings instance
test_settings = TestSettings()
