"""
IP-Based Rate Limiter Middleware

Prevents API abuse by limiting requests per IP address.
Uses slowapi library with configurable limits per endpoint.

Domain: API security and rate limiting
"""

import logging
import os

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


# === RATE LIMIT CONFIGURATION ===


class RateLimitConfig:
    """Rate limit configuration for different endpoint types

    Note: These are DEFAULT values that can be overridden via admin dashboard.
    The admin rate limit service stores updated values in Redis.
    """

    # Bot creation limits (prevent spam)
    BOT_CREATION = "5/hour"  # 5 bot creations per hour per IP

    # Bot operations (normal usage)
    BOT_OPERATIONS = "300/minute"  # 300 operations per minute per IP

    # Admin endpoints (monitoring)
    ADMIN_OPERATIONS = "30/minute"  # 30 admin requests per minute per IP

    # Authentication endpoints
    AUTH_LOGIN = "30/minute"  # 30 login attempts per minute per IP
    AUTH_REGISTER = "3/hour"  # 3 registrations per hour per IP

    # Public endpoints (higher limits)
    PUBLIC_READ = "500/minute"  # 500 reads per minute per IP

    # Webhook endpoints (very high limits)
    WEBHOOK = "1000/minute"  # 1000 webhook calls per minute per IP

    # Failed authentication
    FAILED_AUTH = "5/15minute"  # 5 failed attempts per 15 minutes

    @classmethod
    def get_dynamic_limit(cls, service_key: str, default: str) -> str:
        """
        Get rate limit from admin config (Redis) if available, otherwise use default.

        Args:
            service_key: Service name (e.g., "bot_operations", "auth_login")
            default: Default limit string (e.g., "100/minute")

        Returns:
            Rate limit string to apply
        """
        try:
            # Try to get from admin config service
            import asyncio

            from core.services.system import get_rate_limit_service

            service = get_rate_limit_service()

            # Run async function synchronously (only for config loading)
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            config = loop.run_until_complete(service.get_config(service_key))

            if config and config.get("enabled"):
                limit = config.get("limit")
                period = config.get("period", "minute")
                return f"{limit}/{period}"

        except Exception as e:
            logger.debug(f"Could not load dynamic limit for {service_key}: {e}")

        # Fallback to default
        return default


# === IP WHITELIST ===


def get_ip_whitelist() -> set[str]:
    """
    Get IP addresses that should bypass rate limiting

    Returns:
        Set of whitelisted IP addresses
    """
    whitelist_env = os.getenv("RATE_LIMIT_WHITELIST", "")

    whitelist: set[str] = set()

    # Add IPs from environment variable
    if whitelist_env:
        whitelist.update(ip.strip() for ip in whitelist_env.split(",") if ip.strip())

    # Add common internal IPs
    internal_ips = {
        "127.0.0.1",
        "localhost",
        "::1",  # IPv6 localhost
    }
    whitelist.update(internal_ips)

    return whitelist


# === CUSTOM KEY FUNCTION ===


def get_remote_address_with_whitelist(request: Request) -> str | None:
    """
    Get remote IP address, but return None for whitelisted IPs
    (None means no rate limiting will be applied)

    Args:
        request: FastAPI request object

    Returns:
        IP address or None if whitelisted
    """
    ip = get_remote_address(request)

    # Check if IP is whitelisted
    whitelist = get_ip_whitelist()
    if ip in whitelist:
        logger.debug(f"IP {ip} is whitelisted, skipping rate limit")
        return None

    return ip


# === LIMITER INSTANCE ===


def create_limiter(storage_uri: str | None = None, enabled: bool = True) -> Limiter:
    """
    Create rate limiter instance

    Args:
        storage_uri: Redis URI for distributed rate limiting (optional)
                    Format: redis://host:port/db
                    If None, uses in-memory storage (single instance only)
        enabled: Whether rate limiting is enabled

    Returns:
        Configured Limiter instance
    """
    # Get storage URI from environment if not provided
    if storage_uri is None:
        storage_uri = os.getenv("RATE_LIMIT_STORAGE_URI")

    # Check if rate limiting is disabled
    if not enabled or os.getenv("DISABLE_RATE_LIMITING", "").lower() == "true":
        logger.warning("Rate limiting is DISABLED - not recommended for production!")
        # Return limiter that does nothing
        return Limiter(
            key_func=lambda r: None,
            enabled=False,  # Always return None = no limiting
        )

    # Create limiter with optional Redis backend
    limiter = Limiter(
        key_func=get_remote_address_with_whitelist,
        storage_uri=storage_uri,  # None = in-memory, or redis://...
        strategy="fixed-window",  # Can also use "moving-window" (more accurate but slower)
        headers_enabled=True,  # Add rate limit headers to responses
        swallow_errors=True,  # Don't crash on rate limit errors
    )

    if storage_uri:
        logger.info(f"Rate limiter initialized with Redis backend: {storage_uri}")
    else:
        logger.info("Rate limiter initialized with in-memory storage (single instance only)")

    return limiter


# === GLOBAL LIMITER ===

# Initialize limiter (will be attached to FastAPI app)
limiter = create_limiter()


# === RATE LIMIT EXCEEDED HANDLER ===


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors

    Args:
        request: FastAPI request
        exc: RateLimitExceeded exception

    Returns:
        JSON response with error details
    """
    from fastapi.responses import JSONResponse

    # Extract retry-after from exception
    retry_after = (
        exc.detail.split("Retry after ")[1].split(" ")[0] if "Retry after" in exc.detail else "60"
    )

    # Log rate limit violation
    ip = get_remote_address(request)
    logger.warning(
        f"Rate limit exceeded for IP {ip} on {request.url.path} - Retry after {retry_after} seconds"
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "retry_after_seconds": int(retry_after),
            "details": exc.detail,
        },
        headers={
            "Retry-After": retry_after,
            "X-RateLimit-Limit": str(getattr(exc, "limit", "unknown")),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(float(retry_after))),
        },
    )


# === UTILITY FUNCTIONS ===


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    Handles X-Forwarded-For header for proxied requests

    Args:
        request: FastAPI request

    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (for proxied requests)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2, ...)
        # Take the first one (original client)
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection
    if request.client:
        return request.client.host

    return "unknown"


def check_rate_limit_status(request: Request, limit: str) -> dict:
    """
    Check rate limit status for a request without enforcing it

    Args:
        request: FastAPI request
        limit: Rate limit string (e.g., "10/minute")

    Returns:
        Dictionary with rate limit status
    """
    ip = get_client_ip(request)

    # Parse limit string
    parts = limit.split("/")
    if len(parts) != 2:
        return {"error": "Invalid limit format"}

    max_requests = int(parts[0])

    return {
        "ip": ip,
        "limit": limit,
        "max_requests": max_requests,
        "whitelisted": ip in get_ip_whitelist(),
    }


# === EXPORTS ===

# === CONFIG RELOAD SUPPORT ===


async def reload_rate_limit_configs():
    """
    Reload rate limit configurations from Redis/database.

    This should be called:
    - On application startup
    - When admin updates configs via dashboard
    - Periodically (optional background task)

    Returns:
        Number of configs updated
    """
    try:
        from core.services.system import get_rate_limit_service

        service = get_rate_limit_service()
        configs = await service.get_all_configs()

        updated = 0
        for config in configs:
            service_name = config.get("service", "")
            limit = config.get("limit")
            period = config.get("period", "minute")
            enabled = config.get("enabled", True)

            if not enabled:
                logger.info(f"Rate limit disabled for {service_name}")
                continue

            # Update class attributes dynamically
            limit_string = f"{limit}/{period}"

            # Map service names to class attributes
            attr_map = {
                "bot_creation": "BOT_CREATION",
                "bot_operations": "BOT_OPERATIONS",
                "admin_operations": "ADMIN_OPERATIONS",
                "auth_login": "AUTH_LOGIN",
                "auth_register": "AUTH_REGISTER",
                "public_read": "PUBLIC_READ",
                "webhook": "WEBHOOK",
                "analytics": "ANALYTICS",
            }

            attr_name = attr_map.get(service_name)
            if attr_name and hasattr(RateLimitConfig, attr_name):
                old_value = getattr(RateLimitConfig, attr_name)
                if old_value != limit_string:
                    setattr(RateLimitConfig, attr_name, limit_string)
                    logger.info(f"Updated rate limit {attr_name}: {old_value} -> {limit_string}")
                    updated += 1

        if updated > 0:
            logger.info(f"✅ Reloaded {updated} rate limit configurations")
        else:
            logger.debug("No rate limit config changes detected")

        return updated

    except Exception as e:
        logger.error(f"Error reloading rate limit configs: {e}")
        return 0


# === DYNAMIC RATE LIMIT DECORATOR (Phase 2) ===

from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException, status


def dynamic_rate_limit(service: str, default: str = "100/minute"):
    """
    Dynamic rate limit decorator with cache support (Phase 2)

    Checks cache at request time for current rate limit configuration.
    Changes apply within 30 seconds without restart.

    Usage:
        @router.post("/bots")
        @dynamic_rate_limit(service="bot_creation", default="5/hour")
        async def create_bot(request: Request):
            pass

    Args:
        service: Service key (e.g., "bot_operations", "auth_login")
        default: Fallback limit if config not found (e.g., "100/minute")

    Returns:
        Decorated function with dynamic rate limiting
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Import cache here to avoid circular dependency
            from apps.api.middleware.rate_limit_cache import get_cached_limit

            # Get request object from kwargs
            request: Request | None = kwargs.get("request")
            if not request:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                # No request found, skip rate limiting
                logger.warning(f"No request object found for {service}, skipping rate limit")
                return await func(*args, **kwargs)

            # Get current limit from cache (checks every 30s)
            current_limit = await get_cached_limit(service, default)

            # Get client IP
            ip = get_client_ip(request)

            # Check if whitelisted
            if ip in get_ip_whitelist():
                logger.debug(f"IP {ip} whitelisted for {service}, skipping rate limit")
                return await func(*args, **kwargs)

            # Parse limit string (e.g., "100/minute" -> 100, "minute")
            try:
                parts = current_limit.split("/")
                if len(parts) != 2:
                    raise ValueError(f"Invalid limit format: {current_limit}")

                max_requests = int(parts[0])
                window = parts[1]  # minute, hour, day, etc.

            except (ValueError, IndexError) as e:
                logger.error(f"Failed to parse rate limit '{current_limit}': {e}")
                # Fallback to default
                return await func(*args, **kwargs)

            # Check rate limit using slowapi's limiter
            # Note: We use the existing limiter's storage for consistency
            try:
                # Manually check rate limit
                key = f"ratelimit:{service}:{ip}"

                # Use limiter's internal storage
                if hasattr(limiter, "_storage") and limiter._storage:
                    storage = limiter._storage

                    # Get current count
                    current_count = await storage.get(key) or 0

                    if current_count >= max_requests:
                        logger.warning(
                            f"Rate limit exceeded for {service}: {ip} "
                            f"({current_count}/{max_requests} per {window})"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Rate limit exceeded: {max_requests} requests per {window}. Please try again later.",
                        )

                    # Increment counter
                    await storage.incr(key, window, amount=1)

            except HTTPException:
                raise
            except Exception as e:
                logger.debug(f"Rate limit check failed for {service}: {e}, allowing request")
                # If check fails, allow request (fail open)

            # Execute the actual endpoint
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# === EXPORTS ===

__all__ = [
    "limiter",
    "RateLimitConfig",
    "custom_rate_limit_exceeded_handler",
    "get_client_ip",
    "check_rate_limit_status",
    "get_ip_whitelist",
    "reload_rate_limit_configs",
    "dynamic_rate_limit",  # Phase 2
]
