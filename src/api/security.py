"""API security — API key authentication and rate limiting middleware"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from src.config import settings

# ── API Key auth ───────────────────────────────────────────────────────────
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    """FastAPI dependency — validates X-API-Key header."""
    if not settings.API_KEY:
        # No API key configured — skip check (dev mode)
        return ""
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


# ── Simple in-memory rate limiter ──────────────────────────────────────────
_buckets: dict[str, list[float]] = defaultdict(list)


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit_check(request: Request) -> None:
    """FastAPI dependency — enforces per-IP rate limiting on mutating endpoints."""
    client_ip = _get_client_ip(request)
    now = time.monotonic()
    window = 60.0  # 1 minute window
    max_requests = settings.RATE_LIMIT_PER_MINUTE

    # Prune old entries
    _buckets[client_ip] = [t for t in _buckets[client_ip] if now - t < window]

    if len(_buckets[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {max_requests} requests per minute.",
        )
    _buckets[client_ip].append(now)
