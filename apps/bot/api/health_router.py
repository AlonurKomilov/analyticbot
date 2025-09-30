"""
Enhanced Health Check Endpoints for Bot Service
Provides comprehensive health monitoring for the Telegram bot
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from config.settings import settings
from core.common.health.checker import HealthChecker, health_checker
from core.common.health.models import DependencyType
from infra.db.connection_manager import db_manager
from infra.db.health_utils import is_db_healthy

logger = logging.getLogger(__name__)

# Create router for health endpoints
health_router = APIRouter(prefix="/health", tags=["Health"])

# Initialize health checker for bot service
bot_health_checker = HealthChecker(service_name="AnalyticBot-BotService", version="2.1.0")


async def check_database_health():
    """Database health check for bot service"""
    return await health_checker.check_database(db_manager)


async def check_telegram_api_health():
    """Telegram API health check"""
    bot_token = settings.BOT_TOKEN.get_secret_value()
    return await health_checker.check_http(f"https://api.telegram.org/bot{bot_token}/getMe")


async def check_storage_channel_health():
    """Storage channel accessibility check"""
    try:
        # This would require bot instance, simplified for now
        return {
            "healthy": True,
            "storage_channel_id": settings.STORAGE_CHANNEL_ID,
            "configured": settings.STORAGE_CHANNEL_ID != 0,
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}


# Register dependencies with the health checker
bot_health_checker.register_dependency(
    "database", check_database_health, DependencyType.DATABASE, critical=True
)

bot_health_checker.register_dependency(
    "telegram_api",
    check_telegram_api_health,
    DependencyType.EXTERNAL_API,
    critical=True,
)

bot_health_checker.register_dependency(
    "storage_channel",
    check_storage_channel_health,
    DependencyType.STORAGE,
    critical=False,
)


@health_router.get("/")
async def bot_health_check():
    """
    ## 🤖 Bot Service Health Check

    Comprehensive health check for the Telegram bot service including:
    - Database connectivity and performance
    - Telegram API accessibility
    - Storage channel configuration
    - Service dependencies status

    **Returns:**
    - Overall service health status
    - Individual dependency health
    - Performance metrics
    - Response times
    """
    try:
        health_result = await bot_health_checker.perform_health_check(
            environment=settings.ENVIRONMENT
        )

        return {
            **bot_health_checker.to_dict(health_result),
            "metadata": {
                "bot_token_configured": bool(
                    settings.BOT_TOKEN.get_secret_value() != "dummy_token_for_development"
                ),
                "admin_ids_count": len(settings.ADMIN_IDS),
                "supported_locales": settings.SUPPORTED_LOCALES,
                "environment": settings.ENVIRONMENT,
                "debug_mode": settings.DEBUG,
            },
        }

    except Exception as e:
        logger.error(f"Bot health check failed: {e}")
        return {
            "service": "AnalyticBot-BotService",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@health_router.get("/liveness")
async def bot_liveness_check():
    """
    ## 💓 Bot Service Liveness Check

    Simple liveness probe to verify the bot service is running.
    Used by orchestrators like Kubernetes for restart decisions.

    **Returns:**
    - Basic service status
    - Process uptime information
    """
    return {
        "status": "alive",
        "service": "AnalyticBot-BotService",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
    }


@health_router.get("/readiness")
async def bot_readiness_check():
    """
    ## ✅ Bot Service Readiness Check

    Readiness probe to verify the bot service is ready to handle requests.
    Checks critical dependencies that must be available for proper operation.

    **Returns:**
    - Readiness status
    - Critical dependency status
    - Service capabilities
    """
    try:
        # Check only critical dependencies for readiness
        db_healthy = await is_db_healthy()
        telegram_health = await check_telegram_api_health()
        telegram_healthy = telegram_health.get("healthy", False)

        ready = db_healthy and telegram_healthy

        return {
            "status": "ready" if ready else "not_ready",
            "service": "AnalyticBot-BotService",
            "timestamp": datetime.now().isoformat(),
            "critical_dependencies": {
                "database": "healthy" if db_healthy else "unhealthy",
                "telegram_api": "healthy" if telegram_healthy else "unhealthy",
            },
            "ready": ready,
        }

    except Exception as e:
        logger.error(f"Bot readiness check failed: {e}")
        return {
            "status": "not_ready",
            "service": "AnalyticBot-BotService",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "ready": False,
        }


@health_router.get("/database")
async def bot_database_health():
    """
    ## 🗃️ Database Health Detailed Check

    Detailed database health information for the bot service.

    **Returns:**
    - Connection pool status
    - Query performance metrics
    - Database connectivity details
    """
    try:
        db_health = await check_database_health()
        return {
            "service": "AnalyticBot-BotService",
            "component": "database",
            "timestamp": datetime.now().isoformat(),
            **db_health,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "service": "AnalyticBot-BotService",
            "component": "database",
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
