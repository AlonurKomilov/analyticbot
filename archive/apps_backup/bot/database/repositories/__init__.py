"""
Repository imports redirected to infrastructure layer
For backward compatibility, imports are redirected to infra/db/repositories/
"""

# Import all repository implementations from infrastructure layer
from infra.db.repositories import (
    AsyncpgAdminRepository,
    AsyncpgAnalyticsRepository,
    AsyncpgChannelRepository,
    AsyncpgDeliveryRepository,
    AsyncpgPaymentRepository,
    AsyncpgPlanRepository,
    AsyncpgScheduleRepository,
    AsyncpgUserRepository,
)

# Backward compatibility aliases
UserRepository = AsyncpgUserRepository
AnalyticsRepository = AsyncpgAnalyticsRepository
ChannelRepository = AsyncpgChannelRepository
PaymentRepository = AsyncpgPaymentRepository
PlanRepository = AsyncpgPlanRepository

__all__ = [
    "AsyncpgUserRepository",
    "AsyncpgAdminRepository",
    "AsyncpgScheduleRepository",
    "AsyncpgDeliveryRepository",
    "AsyncpgAnalyticsRepository",
    "AsyncpgChannelRepository",
    "AsyncpgPaymentRepository",
    "AsyncpgPlanRepository",
    # Backward compatibility aliases
    "UserRepository",
    "AnalyticsRepository",
    "ChannelRepository",
    "PaymentRepository",
    "PlanRepository",
]
