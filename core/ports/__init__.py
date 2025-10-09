# Core ports package - Contains abstract interfaces and protocols

# Cache ports (async)
from .cache_port import AsyncCachePort

# Repository ports (data access)
# Health ports (new)
from .health_ports import (
    CacheHealthPort,
    ComponentHealth,
    DatabaseHealthPort,
    ExternalServiceHealthPort,
    HealthMonitoringService,
    HealthStatus,
    SystemHealth,
    SystemResourcesPort,
)
from .repository_ports import (
    AdminRepository,
    ChannelDailyRepository,
    ChannelRepository,
    DeliveryRepository,
    EdgesRepository,
    PostMetricsRepository,
    PostRepository,
    ScheduleRepository,
    UserRepository,
)

# Security ports (new)
from .security_ports import (
    AuthRequest,
    CachePort,
    SecurityConfigPort,
    SecurityEventsPort,
    SecurityService,
    SessionInfo,
    TokenClaims,
    TokenGeneratorPort,
    UserRepositoryPort,
)

# Service ports (external services)
from .service_ports import (
    AnalyticsService,
    CacheService,
    FileStorageService,
    MessageQueueService,
    NotificationService,
    SchedulingService,
    TelegramService,
)

# TG Client port (existing)
from .tg_client import TGClient

__all__ = [
    # Cache ports
    "AsyncCachePort",
    # Repository ports
    "UserRepository",
    "AdminRepository",
    "ChannelRepository",
    "ScheduleRepository",
    "DeliveryRepository",
    "ChannelDailyRepository",
    "PostRepository",
    "PostMetricsRepository",
    "EdgesRepository",
    # Service ports
    "NotificationService",
    "CacheService",
    "MessageQueueService",
    "FileStorageService",
    "TelegramService",
    "AnalyticsService",
    "SchedulingService",
    # TG Client
    "TGClient",
    # Security ports
    "AuthRequest",
    "TokenClaims",
    "SessionInfo",
    "CachePort",
    "TokenGeneratorPort",
    "SecurityConfigPort",
    "UserRepositoryPort",
    "SecurityEventsPort",
    "SecurityService",
    # Health ports
    "HealthStatus",
    "ComponentHealth",
    "SystemHealth",
    "DatabaseHealthPort",
    "CacheHealthPort",
    "ExternalServiceHealthPort",
    "SystemResourcesPort",
    "HealthMonitoringService",
]
