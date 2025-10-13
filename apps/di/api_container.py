"""
API Services DI Container

Single Responsibility: API-specific services and dependencies
Includes FastAPI dependencies like authentication, authorization, etc.
"""

import logging

from dependency_injector import containers, providers
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


async def _create_auth_dependency():
    """Create authentication dependency for FastAPI"""
    try:
        from core.security_engine.auth_service import verify_token  # type: ignore[import]
    except ImportError:
        # Fallback if auth service not available
        async def verify_token(token: str):
            # Basic JWT verification fallback
            try:
                import jwt  # type: ignore[import]
                from config.settings import settings
                secret_key = getattr(settings, 'SECRET_KEY', getattr(settings, 'JWT_SECRET', 'default_secret'))
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                return payload
            except Exception:
                return None

    security = HTTPBearer()

    async def get_current_user(credentials: HTTPAuthorizationCredentials):
        """Verify JWT token and return user payload"""
        token = credentials.credentials
        try:
            payload = await verify_token(token)
            if not payload:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            return payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )

    return get_current_user


async def _create_channel_management_service(channel_repository=None, **kwargs):
    """Create channel management service for API"""
    try:
        from apps.bot.services.analytics_service import AnalyticsService

        if channel_repository is None:
            return None

        # AnalyticsService needs bot parameter, but for API we can pass None
        return AnalyticsService(
            analytics_repository=channel_repository,
            bot=None,  # API doesn't need bot client
        )
    except (ImportError, TypeError) as e:
        logger.warning(f"Channel management service not available: {e}")
        return None


# ============================================================================
# API CONTAINER
# ============================================================================


class APIContainer(containers.DeclarativeContainer):
    """
    API Services Container

    Single Responsibility: API-specific services and FastAPI dependencies
    Includes authentication, authorization, and API-specific business services
    """

    config = providers.Configuration()

    # Dependencies from other containers
    database = providers.DependenciesContainer()
    core_services = providers.DependenciesContainer()

    # ============================================================================
    # FASTAPI DEPENDENCIES
    # ============================================================================

    # Authentication dependency
    auth_dependency = providers.Factory(_create_auth_dependency)

    # Security scheme
    security_scheme = providers.Singleton(HTTPBearer)

    # ============================================================================
    # API-SPECIFIC SERVICES
    # ============================================================================

    channel_management_service = providers.Factory(
        _create_channel_management_service,
        channel_repository=database.channel_repo,
    )
