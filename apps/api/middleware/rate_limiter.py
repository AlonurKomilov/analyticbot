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
    """Rate limit configuration for different endpoint types"""

    # Bot creation limits (prevent spam)
    BOT_CREATION = "5/hour"  # 5 bot creations per hour per IP

    # Bot operations (normal usage)
    BOT_OPERATIONS = "100/minute"  # 100 operations per minute per IP

    # Admin endpoints (monitoring)
    ADMIN_OPERATIONS = "30/minute"  # 30 admin requests per minute per IP

    # Authentication endpoints
    AUTH_LOGIN = "10/minute"  # 10 login attempts per minute per IP
    AUTH_REGISTER = "3/hour"  # 3 registrations per hour per IP

    # Public endpoints (higher limits)
    PUBLIC_READ = "200/minute"  # 200 reads per minute per IP

    # Webhook endpoints (very high limits)
    WEBHOOK = "1000/minute"  # 1000 webhook calls per minute per IP

    # Failed authentication
    FAILED_AUTH = "5/15minute"  # 5 failed attempts per 15 minutes


# === IP WHITELIST ===

def get_ip_whitelist() -> set[str]:
    """
    Get IP addresses that should bypass rate limiting

    Returns:
        Set of whitelisted IP addresses
    """
    whitelist_env = os.getenv("RATE_LIMIT_WHITELIST", "")

    whitelist = set()

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

def create_limiter(
    storage_uri: str | None = None,
    enabled: bool = True
) -> Limiter:
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
            key_func=lambda r: None,  # Always return None = no limiting
            enabled=False
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
    retry_after = exc.detail.split("Retry after ")[1].split(" ")[0] if "Retry after" in exc.detail else "60"

    # Log rate limit violation
    ip = get_remote_address(request)
    logger.warning(
        f"Rate limit exceeded for IP {ip} on {request.url.path} - "
        f"Retry after {retry_after} seconds"
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "retry_after_seconds": int(retry_after),
            "details": exc.detail
        },
        headers={
            "Retry-After": retry_after,
            "X-RateLimit-Limit": str(getattr(exc, "limit", "unknown")),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(float(retry_after))),
        }
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
        "whitelisted": ip in get_ip_whitelist()
    }


# === EXPORTS ===

__all__ = [
    "limiter",
    "RateLimitConfig",
    "custom_rate_limit_exceeded_handler",
    "get_client_ip",
    "check_rate_limit_status",
    "get_ip_whitelist",
]
