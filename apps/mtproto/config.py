import os

from pydantic import Field
from pydantic_settings import BaseSettings


class MTProtoSettings(BaseSettings):
    """Configuration settings for MTProto application.

    This configuration is feature-flagged by default (MTPROTO_ENABLED=False)
    to ensure no behavior change to existing applications.
    """

    # Feature flags - disabled by default for safety
    MTPROTO_ENABLED: bool = Field(
        default=False,
        description="Enable MTProto functionality. Set to true to activate Telegram client features.",
    )

    MTPROTO_HISTORY_ENABLED: bool = Field(
        default=False,
        description="Enable MTProto history collection. Requires MTPROTO_ENABLED=True.",
    )

    MTPROTO_UPDATES_ENABLED: bool = Field(
        default=False,
        description="Enable MTProto real-time updates collection. Requires MTPROTO_ENABLED=True.",
    )

    MTPROTO_STATS_ENABLED: bool = Field(
        default=False,
        description="Enable MTProto official stats loading. Requires MTPROTO_ENABLED=True.",
    )

    # Phase 4.6: Scale & Hardening Features (OFF by default)
    MTPROTO_POOL_ENABLED: bool = Field(
        default=False,
        description="Enable multi-account connection pooling for horizontal scaling",
    )

    MTPROTO_PROXY_ENABLED: bool = Field(
        default=False, description="Enable proxy pool rotation for enhanced reliability"
    )

    OBS_PROMETHEUS_ENABLED: bool = Field(
        default=False, description="Enable Prometheus metrics export"
    )

    OBS_OTEL_ENABLED: bool = Field(default=False, description="Enable OpenTelemetry tracing")

    # Telegram API credentials (required when enabled)
    TELEGRAM_API_ID: int | None = Field(
        default=None, description="Telegram API ID from my.telegram.org"
    )

    TELEGRAM_API_HASH: str | None = Field(
        default=None, description="Telegram API Hash from my.telegram.org"
    )

    # Session configuration
    TELEGRAM_SESSION_NAME: str = Field(
        default="mtproto_session", description="Name for the Telegram session file"
    )

    # Optional proxy support
    TELEGRAM_PROXY: str | None = Field(
        default=None,
        description="Proxy URL for Telegram connections (e.g., socks5://user:pass@host:port)",
    )

    # Account pool configuration (Phase 4.6)
    MTPROTO_ACCOUNTS: list[str] = Field(
        default_factory=list,
        description="List of session names for multi-account pooling (e.g., ['session1', 'session2'])",
    )

    MTPROTO_RPS_PER_ACCOUNT: float = Field(
        default=0.7,
        description="Requests per second limit per account (conservative for flood protection)",
    )

    MTPROTO_MAX_CONCURRENCY_PER_ACCOUNT: int = Field(
        default=2, description="Maximum concurrent requests per account"
    )

    MTPROTO_GLOBAL_RPS: float = Field(
        default=2.5, description="Global requests per second limit across all accounts"
    )

    # Connection Pool Configuration (Auto-Close System)
    MTPROTO_MAX_CONCURRENT_USERS: int = Field(
        default=10,
        description="Maximum concurrent user sessions in MTProto connection pool (system-wide limit)",
    )

    MTPROTO_MAX_CONNECTIONS_PER_USER: int = Field(
        default=1,
        description="Maximum concurrent connections per user (prevents duplicate workers)",
    )

    MTPROTO_SESSION_TIMEOUT: int = Field(
        default=600,
        description="Maximum session duration in seconds before auto-close (10 minutes default)",
    )

    MTPROTO_CONNECTION_TIMEOUT: int = Field(
        default=300,
        description="Connection establishment timeout in seconds (5 minutes default)",
    )

    MTPROTO_IDLE_TIMEOUT: int = Field(
        default=180,
        description="Idle timeout before disconnecting inactive connection (3 minutes default)",
    )

    # Proxy pool configuration (Phase 4.6)
    MTPROTO_PROXIES: list[str] = Field(
        default_factory=list,
        description="List of proxy URLs (e.g., ['socks5://user:pass@host:port', 'http://proxy:8080'])",
    )

    MTPROTO_PROXY_ROTATION_SEC: int = Field(
        default=300,
        description="Proxy rotation interval in seconds (5 minutes default)",
    )

    MTPROTO_PROXY_FAIL_SCORE_LIMIT: int = Field(
        default=3, description="Number of failures before marking proxy as unhealthy"
    )

    # Collector scope & limits
    MTPROTO_PEERS: list[str] = Field(
        default_factory=list,
        description="List of channel usernames or IDs to monitor (e.g., ['@channel1', 'channel2'])",
    )

    MTPROTO_HISTORY_LIMIT_PER_RUN: int = Field(
        default=500,
        description="Maximum number of messages to fetch per peer per history run",
    )

    MTPROTO_CONCURRENCY: int = Field(
        default=4, description="Number of concurrent requests to Telegram API"
    )

    MTPROTO_SLEEP_THRESHOLD: float = Field(
        default=1.5, description="Sleep threshold in seconds for rate limiting"
    )

    MTPROTO_RETRY_BACKOFF: float = Field(
        default=2.0, description="Exponential backoff multiplier for retries"
    )

    MTPROTO_RETRY_MAX: int = Field(default=5, description="Maximum number of retry attempts")

    # Connection Pool Configuration (Phase 4.6+)
    MTPROTO_MAX_CONNECTIONS: int = Field(
        default=10,
        description="Maximum concurrent MTProto connections system-wide. Increase for larger servers.",
    )

    MTPROTO_MAX_CONNECTIONS_PER_USER: int = Field(
        default=1,
        description="Maximum concurrent connections per user (recommended: 1)",
    )

    MTPROTO_SESSION_TIMEOUT: int = Field(
        default=600, description="Session timeout in seconds (auto-close if exceeded)"
    )

    MTPROTO_CONNECTION_TIMEOUT: int = Field(
        default=300, description="Connection establishment timeout in seconds"
    )

    MTPROTO_IDLE_TIMEOUT: int = Field(default=180, description="Idle connection timeout in seconds")

    MTPROTO_CLEANUP_INTERVAL: int = Field(
        default=300, description="Cleanup task interval in seconds"
    )

    MTPROTO_DB_POOL_MIN_SIZE: int = Field(
        default=5, description="Minimum database connection pool size per worker"
    )

    MTPROTO_DB_POOL_MAX_SIZE: int = Field(
        default=15, description="Maximum database connection pool size per worker"
    )

    # Observability configuration (Phase 4.6)
    PROMETHEUS_PORT: int = Field(
        default=9108, description="Port for Prometheus metrics HTTP server"
    )

    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(
        default=None,
        description="OpenTelemetry OTLP exporter endpoint (e.g., http://jaeger:14268/api/traces)",
    )

    OTEL_SAMPLER_RATIO: float = Field(
        default=0.05,
        description="OpenTelemetry trace sampling ratio (0.05 = 5% of traces)",
    )

    # Health and shutdown configuration (Phase 4.6)
    GRACEFUL_SHUTDOWN_TIMEOUT_S: int = Field(
        default=25, description="Maximum time to wait for graceful shutdown in seconds"
    )

    HEALTH_BIND: str = Field(
        default="0.0.0.0:8091",
        description="Health check HTTP server bind address (host:port)",
    )

    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level for MTProto application")

    model_config = {
        # Clean Architecture: Load environment-specific files
        "env_file": (
            [".env.production", ".env.development"]
            if os.getenv("ENVIRONMENT") != "development"
            else [".env.development", ".env.production"]
        ),
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra environment variables
    }
