# apps/jobs/di.py
from dependency_injector import containers, providers
import asyncpg

from config.settings import settings
from infra.db.repositories import (
    AsyncpgChannelRepository,
    AsyncpgAnalyticsRepository,
    AsyncpgPaymentRepository,
    AsyncpgPlanRepository
)
from apps.jobs.services.analytics_job_service import AnalyticsJobService
from apps.jobs.services.delivery_job_service import DeliveryJobService


class JobsContainer(containers.DeclarativeContainer):
    """Dependency injection container for background jobs."""
    
    # Configuration
    config = providers.Configuration()
    
    # AsyncPG pool for repositories
    asyncpg_pool = providers.Resource(
        asyncpg.create_pool,
        dsn=str(settings.DATABASE_URL or "").replace("postgresql+asyncpg://", "postgresql://"),
        min_size=1,
        max_size=getattr(settings, 'DB_POOL_SIZE', 10)
    )
    
    # Repository providers
    channel_repo = providers.Factory(AsyncpgChannelRepository, pool=asyncpg_pool)
    analytics_repo = providers.Factory(AsyncpgAnalyticsRepository, pool=asyncpg_pool)
    payment_repo = providers.Factory(AsyncpgPaymentRepository, pool=asyncpg_pool)
    plan_repo = providers.Factory(AsyncpgPlanRepository, pool=asyncpg_pool)
    
    # Application Service providers
    analytics_job_service = providers.Factory(AnalyticsJobService)
    delivery_job_service = providers.Factory(DeliveryJobService)


# Container instance
container = JobsContainer()


def configure_jobs_container() -> JobsContainer:
    """Configure and return the Jobs container"""
    return container