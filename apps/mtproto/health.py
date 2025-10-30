"""Enhanced Health Check System for MTProto Service."""

import logging
from datetime import datetime
from typing import Any

from apps.mtproto.di import get_settings, get_tg_client
# Note: HealthChecker moved to apps layer, using stub for compatibility
# from core.common.health.checker import HealthChecker
from core.common.health.models import DependencyType
from core.ports.tg_client import TGClient


class HealthCheck:
    """Health check service for MTProto application.

    Provides health status information for monitoring and deployment purposes.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._start_time = datetime.now()
        self._tg_client: TGClient | None = None

    async def initialize(self) -> None:
        """Initialize the health check service."""
        settings = get_settings()

        if not settings.MTPROTO_ENABLED:
            self.logger.info("HealthCheck service disabled (MTPROTO_ENABLED=False)")
            return

        self._tg_client = get_tg_client()
        self.logger.info("HealthCheck service initialized")

    async def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status with enhanced dependency checking.

        Returns:
            Dictionary containing detailed health status information
        """
        settings = get_settings()
        uptime = datetime.now() - self._start_time

        # Simplified health check (enhanced health checker deprecated)
        try:
            config_status = self._check_configuration_health(settings)
            tg_client_status = (
                await self._check_tg_client_health()
                if settings.MTPROTO_ENABLED and self._tg_client
                else "disabled"
            )

            enhanced_status = {
                "status": "healthy" if config_status == "healthy" else "degraded",
                "uptime_seconds": int(uptime.total_seconds()),
                "mtproto_enabled": settings.MTPROTO_ENABLED,
                "version": "2.1.0",
                "phase": "Simplified Health Check",
                "components": {
                    "mtproto_app": "healthy",
                    "tg_client": tg_client_status,
                    "configuration": config_status,
                },
                "metadata": {
                    "telegram_api_layer": 164,
                    "supported_features": [
                        "real_time_updates",
                        "history_collection",
                        "metrics_monitoring",
                        "health_monitoring",
                    ],
                    "feature_flags": {
                        "mtproto_enabled": settings.MTPROTO_ENABLED,
                        "updates_enabled": getattr(settings, "MTPROTO_UPDATES_ENABLED", False),
                        "history_enabled": getattr(settings, "MTPROTO_HISTORY_ENABLED", False),
                    },
                },
            }

            return enhanced_status

        except Exception as e:
            self.logger.error(f"Enhanced health check failed: {e}")
            # Fallback to legacy health check
            return await self._legacy_health_check(settings, uptime)

    async def _legacy_health_check(self, settings, uptime) -> dict[str, Any]:
        """Legacy health check implementation as fallback"""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "mtproto_enabled": settings.MTPROTO_ENABLED,
            "components": {
                "mtproto_app": "healthy",
                "tg_client": "unknown",
                "configuration": "healthy",
            },
            "version": "2.1.0",
            "phase": "Enhanced Health Monitoring (Legacy Mode)",
        }

        # Check TGClient health if enabled
        if settings.MTPROTO_ENABLED and self._tg_client:
            try:
                client_status = await self._check_tg_client_health()
                status["components"]["tg_client"] = client_status
            except Exception as e:
                status["components"]["tg_client"] = "unhealthy"
                status["status"] = "degraded"
                self.logger.error(f"TGClient health check failed: {e}")
        elif not settings.MTPROTO_ENABLED:
            status["components"]["tg_client"] = "disabled"

        # Check configuration health
        config_status = self._check_configuration_health(settings)
        status["components"]["configuration"] = config_status

        if config_status == "unhealthy":
            status["status"] = "unhealthy"

        return status

    async def _check_tg_client_health(self) -> str:
        """Check TGClient health status.

        Returns:
            Health status string
        """
        if not self._tg_client:
            return "not_initialized"

        try:
            # This is a stub implementation
            # In future phases, this would perform actual connectivity checks
            if hasattr(self._tg_client, "is_connected"):
                # Hypothetical method for checking connection
                is_connected = getattr(self._tg_client, "is_connected", lambda: False)()
                return "healthy" if is_connected else "disconnected"
            else:
                return "healthy"  # Stub client is always "healthy"

        except Exception as e:
            self.logger.error(f"TGClient health check error: {e}")
            return "unhealthy"

    def _check_configuration_health(self, settings) -> str:
        """Check configuration health status.

        Args:
            settings: MTProtoSettings instance

        Returns:
            Health status string
        """
        if not settings.MTPROTO_ENABLED:
            return "disabled"

        # Check required settings when MTProto is enabled
        if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_API_HASH:
            return "unhealthy"

        return "healthy"

    async def get_readiness_status(self) -> dict[str, Any]:
        """Get readiness status for deployment health checks.

        Returns:
            Dictionary containing readiness information
        """
        settings = get_settings()

        ready = True
        components = {}

        # Check if MTProto is properly configured when enabled
        if settings.MTPROTO_ENABLED:
            if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_API_HASH:
                ready = False
                components["configuration"] = "missing_credentials"
            else:
                components["configuration"] = "ready"

            # Check TGClient readiness
            if self._tg_client:
                components["tg_client"] = "ready"
            else:
                components["tg_client"] = "not_initialized"
        else:
            components["configuration"] = "disabled"
            components["tg_client"] = "disabled"

        return {"ready": ready, "timestamp": datetime.now().isoformat(), "components": components}

    async def get_liveness_status(self) -> dict[str, Any]:
        """Get liveness status for deployment health checks.

        Returns:
            Dictionary containing liveness information
        """
        return {
            "alive": True,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int((datetime.now() - self._start_time).total_seconds()),
        }
