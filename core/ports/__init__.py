# Core ports package - Contains abstract interfaces and protocols

# Repository ports (data access)
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
]
