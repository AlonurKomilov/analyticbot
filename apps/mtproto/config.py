from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class MTProtoSettings(BaseSettings):
    """Configuration settings for MTProto application.
    
    This configuration is feature-flagged by default (MTPROTO_ENABLED=False)
    to ensure no behavior change to existing applications.
    """
    
    # Feature flag - disabled by default for safety
    MTPROTO_ENABLED: bool = Field(
        default=False,
        description="Enable MTProto functionality. Set to true to activate Telegram client features."
    )
    
    # Telegram API credentials (required when enabled)
    TELEGRAM_API_ID: Optional[int] = Field(
        default=None,
        description="Telegram API ID from my.telegram.org"
    )
    
    TELEGRAM_API_HASH: Optional[str] = Field(
        default=None,
        description="Telegram API Hash from my.telegram.org"
    )
    
    # Session configuration
    TELEGRAM_SESSION_NAME: str = Field(
        default="mtproto_session",
        description="Name for the Telegram session file"
    )
    
    # Optional proxy support
    TELEGRAM_PROXY: Optional[str] = Field(
        default=None,
        description="Proxy URL for Telegram connections (e.g., socks5://user:pass@host:port)"
    )
    
    # Logging configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level for MTProto application"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
