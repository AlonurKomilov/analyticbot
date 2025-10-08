# apps/jobs/di.py
from dependency_injector import containers, providers

from apps.jobs.services.analytics_job_service import AnalyticsJobService
from apps.jobs.services.delivery_job_service import DeliveryJobService
from apps.shared.factory import RepositoryFactory


class JobsContainer(containers.DeclarativeContainer):
    """Dependency injection container for background jobs."""

    # Configuration
    config = providers.Configuration()

    # Repository factory - no direct infra imports
    repository_factory = providers.Singleton(RepositoryFactory)

    # Repository providers using factory pattern
    channel_repo = providers.Factory(
        lambda factory: factory.create_channel_repository(), factory=repository_factory
    )
    analytics_repo = providers.Factory(
        lambda factory: factory.create_analytics_repository(), factory=repository_factory
    )
    payment_repo = providers.Factory(
        lambda factory: factory.create_payment_repository(), factory=repository_factory
    )
    plan_repo = providers.Factory(
        lambda factory: factory.create_plan_repository(), factory=repository_factory
    )

    # Application Service providers
    analytics_job_service = providers.Factory(AnalyticsJobService)
    delivery_job_service = providers.Factory(DeliveryJobService)


# Container instance
container = JobsContainer()


def configure_jobs_container() -> JobsContainer:
    """Configure and return the Jobs container"""
    return container
