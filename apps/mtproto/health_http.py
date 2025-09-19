"""
Health check HTTP server for MTProto services.
Provides liveness, readiness, and metrics endpoints for monitoring.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

from aiohttp import web, web_request
from aiohttp.web_response import Response

from apps.mtproto.metrics import get_metrics

logger = logging.getLogger(__name__)


class HealthCheckServer:
    """HTTP server for health checks and metrics."""

    def __init__(
        self,
        bind_address: str = "0.0.0.0:8091",
        account_pool: Any | None = None,
        proxy_pool: Any | None = None,
        rate_limiter: Any | None = None,
    ):
        self.bind_address = bind_address
        self.account_pool = account_pool
        self.proxy_pool = proxy_pool
        self.rate_limiter = rate_limiter

        self.app: web.Application | None = None
        self.runner: web.AppRunner | None = None
        self.site: web.TCPSite | None = None
        self.started = False
        self.start_time = time.time()

        # Custom health checks
        self.custom_health_checks: dict[str, Callable[[], bool]] = {}

        # Metrics reference
        self.metrics = get_metrics()

    def add_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Add a custom health check."""
        self.custom_health_checks[name] = check_func
        logger.info(f"Added health check: {name}")

    async def healthz(self, request: web_request.Request) -> Response:
        """Liveness endpoint - basic service availability."""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "uptime_seconds": time.time() - self.start_time,
                "service": "mtproto",
            }

            # Run custom health checks
            checks = {}
            overall_healthy = True

            for name, check_func in self.custom_health_checks.items():
                try:
                    is_healthy = check_func()
                    checks[name] = {"healthy": is_healthy}
                    if not is_healthy:
                        overall_healthy = False
                except Exception as e:
                    checks[name] = {"healthy": False, "error": str(e)}
                    overall_healthy = False

            if checks:
                health_status["checks"] = checks

            if not overall_healthy:
                health_status["status"] = "unhealthy"
                return web.json_response(health_status, status=503)

            return web.json_response(health_status, status=200)

        except Exception as e:
            logger.error(f"Health check error: {e}")
            return web.json_response(
                {"status": "error", "error": str(e), "timestamp": time.time()},
                status=500,
            )

    async def readyz(self, request: web_request.Request) -> Response:
        """Readiness endpoint - service ready to accept requests."""
        try:
            readiness_status = {
                "status": "ready",
                "timestamp": time.time(),
                "service": "mtproto",
            }

            components = {}
            overall_ready = True

            # Check account pool
            if self.account_pool:
                try:
                    pool_ready = self.account_pool.is_ready
                    healthy_accounts = self.account_pool.healthy_count
                    total_accounts = len(self.account_pool.accounts)

                    components["account_pool"] = {
                        "ready": pool_ready,
                        "healthy_accounts": healthy_accounts,
                        "total_accounts": total_accounts,
                    }

                    if not pool_ready or healthy_accounts == 0:
                        overall_ready = False

                except Exception as e:
                    components["account_pool"] = {"ready": False, "error": str(e)}
                    overall_ready = False

            # Check proxy pool
            if self.proxy_pool:
                try:
                    pool_ready = self.proxy_pool.is_ready
                    healthy_proxies = self.proxy_pool.healthy_count
                    total_proxies = len(self.proxy_pool.proxies)

                    components["proxy_pool"] = {
                        "ready": pool_ready,
                        "healthy_proxies": healthy_proxies,
                        "total_proxies": total_proxies,
                    }

                    # Proxy pool is optional - don't fail readiness if no proxies

                except Exception as e:
                    components["proxy_pool"] = {"ready": False, "error": str(e)}

            # Check rate limiter
            if self.rate_limiter:
                try:
                    limiter_stats = self.rate_limiter.get_all_stats()
                    components["rate_limiter"] = {
                        "ready": True,
                        "global_rps": limiter_stats["global"]["rps"],
                        "active_accounts": len(limiter_stats["accounts"]),
                    }
                except Exception as e:
                    components["rate_limiter"] = {"ready": False, "error": str(e)}
                    overall_ready = False

            readiness_status["components"] = components

            if not overall_ready:
                readiness_status["status"] = "not_ready"
                return web.json_response(readiness_status, status=503)

            return web.json_response(readiness_status, status=200)

        except Exception as e:
            logger.error(f"Readiness check error: {e}")
            return web.json_response(
                {"status": "error", "error": str(e), "timestamp": time.time()},
                status=500,
            )

    async def metrics_endpoint(self, request: web_request.Request) -> Response:
        """Metrics endpoint for monitoring."""
        try:
            metrics_data = {
                "timestamp": time.time(),
                "service": "mtproto",
                "uptime_seconds": time.time() - self.start_time,
            }

            # Prometheus metrics summary
            metrics_data["prometheus"] = self.metrics.get_metrics_summary()

            # Account pool metrics
            if self.account_pool:
                try:
                    metrics_data["account_pool"] = self.account_pool.get_stats()
                except Exception as e:
                    metrics_data["account_pool"] = {"error": str(e)}

            # Proxy pool metrics
            if self.proxy_pool:
                try:
                    metrics_data["proxy_pool"] = self.proxy_pool.get_stats()
                except Exception as e:
                    metrics_data["proxy_pool"] = {"error": str(e)}

            # Rate limiter metrics
            if self.rate_limiter:
                try:
                    metrics_data["rate_limiter"] = self.rate_limiter.get_all_stats()
                except Exception as e:
                    metrics_data["rate_limiter"] = {"error": str(e)}

            return web.json_response(metrics_data, status=200)

        except Exception as e:
            logger.error(f"Metrics endpoint error: {e}")
            return web.json_response({"error": str(e), "timestamp": time.time()}, status=500)

    async def info(self, request: web_request.Request) -> Response:
        """Service information endpoint."""
        try:
            info_data = {
                "service": "mtproto",
                "version": "4.6.0",
                "description": "MTProto Scale & Hardening",
                "started_at": self.start_time,
                "uptime_seconds": time.time() - self.start_time,
                "features": {
                    "account_pool": self.account_pool is not None,
                    "proxy_pool": self.proxy_pool is not None,
                    "rate_limiter": self.rate_limiter is not None,
                    "metrics": self.metrics.enabled,
                    "tracing": False,  # Would check tracer here
                },
            }

            return web.json_response(info_data, status=200)

        except Exception as e:
            logger.error(f"Info endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    def _create_app(self) -> web.Application:
        """Create the aiohttp application."""
        app = web.Application()

        # Add routes
        app.router.add_get("/healthz", self.healthz)
        app.router.add_get("/readyz", self.readyz)
        app.router.add_get("/metrics", self.metrics_endpoint)
        app.router.add_get("/info", self.info)

        # Add CORS headers for development
        app.middlewares.append(self._cors_middleware)

        return app

    @web.middleware
    async def _cors_middleware(self, request: web_request.Request, handler):
        """Add CORS headers."""
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    async def start(self) -> None:
        """Start the health check server."""
        if self.started:
            return

        try:
            host, port_str = self.bind_address.split(":")
            port = int(port_str)

            self.app = self._create_app()
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            self.site = web.TCPSite(self.runner, host, port)
            await self.site.start()

            self.started = True
            logger.info(f"Health check server started on {self.bind_address}")

        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise

    async def stop(self) -> None:
        """Stop the health check server."""
        if not self.started:
            return

        try:
            if self.site:
                await self.site.stop()
                self.site = None

            if self.runner:
                await self.runner.cleanup()
                self.runner = None

            self.app = None
            self.started = False
            logger.info("Health check server stopped")

        except Exception as e:
            logger.error(f"Error stopping health check server: {e}")

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.started and self.site is not None


async def run_health_server(
    bind_address: str = "0.0.0.0:8091",
    account_pool: Any | None = None,
    proxy_pool: Any | None = None,
    rate_limiter: Any | None = None,
) -> HealthCheckServer:
    """
    Run health check server.

    Args:
        bind_address: Address to bind to (host:port)
        account_pool: Optional account pool for health checks
        proxy_pool: Optional proxy pool for health checks
        rate_limiter: Optional rate limiter for health checks

    Returns:
        Running HealthCheckServer instance
    """
    server = HealthCheckServer(bind_address, account_pool, proxy_pool, rate_limiter)
    await server.start()
    return server


# Standalone function for simple usage
def serve_health_checks(
    bind_address: str = "0.0.0.0:8091",
    account_pool: Any | None = None,
    proxy_pool: Any | None = None,
    rate_limiter: Any | None = None,
) -> None:
    """
    Start health check server (blocking).

    For use in standalone scripts or simple deployments.
    """

    async def _serve():
        server = await run_health_server(bind_address, account_pool, proxy_pool, rate_limiter)

        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down health check server...")
        finally:
            await server.stop()

    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        logger.info("Health check server stopped")


if __name__ == "__main__":
    # Simple standalone server for testing
    logging.basicConfig(level=logging.INFO)
    serve_health_checks()
