# Core ports package - Contains abstract interfaces and protocols

# Repository ports (data access)
from .repository_ports import (
    UserRepository,
    AdminRepository, 
    ChannelRepository,
    ScheduleRepository,
    DeliveryRepository,
    ChannelDailyRepository,
    PostRepository,
    PostMetricsRepository,
    EdgesRepository,
)

# Service ports (external services)
from .service_ports import (
    NotificationService,
    CacheService,
    MessageQueueService,
    FileStorageService,
    TelegramService,
    AnalyticsService,
    SchedulingService,
)

# TG Client port (existing)
from .tg_client import TGClient

# Security ports (new)
from .security_ports import (
    AuthRequest,
    TokenClaims,
    SessionInfo,
    CachePort,
    TokenGeneratorPort,
    SecurityConfigPort,
    UserRepositoryPort,
    SecurityEventsPort,
    SecurityService,
)

# Health ports (new)
from .health_ports import (
    HealthStatus,
    ComponentHealth,
    SystemHealth,
    DatabaseHealthPort,
    CacheHealthPort,
    ExternalServiceHealthPort,
    SystemResourcesPort,
    HealthMonitoringService,
)

__all__ = [
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