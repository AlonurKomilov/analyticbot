# apps/jobs/di.py
from dependency_injector import containers, providers

from apps.di import get_container
from apps.jobs.services.analytics_job_service import AnalyticsJobService
from apps.jobs.services.delivery_job_service import DeliveryJobService


# ✅ PHASE 3 FIX: Repository delegation helpers
# These async callables delegate to main container for repository access
async def _get_channel_repo():
    """Get channel repository from main container"""
    container = get_container()
    return await container.database.channel_repo()  # type: ignore[attr-defined]


async def _get_analytics_repo():
    """Get analytics repository from main container"""
    container = get_container()
    return await container.database.analytics_repo()  # type: ignore[attr-defined]


async def _get_payment_repo():
    """Get payment repository from main container"""
    container = get_container()
    return await container.database.payment_repo()  # type: ignore[attr-defined]


async def _get_plan_repo():
    """Get plan repository from main container"""
    container = get_container()
    return await container.database.plan_repo()  # type: ignore[attr-defined]


class JobsContainer(containers.DeclarativeContainer):
    """Dependency injection container for background jobs."""

    # Configuration
    config = providers.Configuration()

    # ✅ PHASE 3 FIX: Repository providers delegate to main container
    channel_repo = providers.Callable(_get_channel_repo)
    analytics_repo = providers.Callable(_get_analytics_repo)
    payment_repo = providers.Callable(_get_payment_repo)
    plan_repo = providers.Callable(_get_plan_repo)

    # Application Service providers
    analytics_job_service = providers.Factory(AnalyticsJobService)
    delivery_job_service = providers.Factory(DeliveryJobService)


# Container instance
container = JobsContainer()


def configure_jobs_container() -> JobsContainer:
    """Configure and return the Jobs container"""
    return container
