"""Redis caching layer for analysis results"""

from __future__ import annotations

import json
import logging

import redis.asyncio as redis

from src.config import settings

logger = logging.getLogger(__name__)

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Return a shared Redis connection (lazy-init)."""
    global _pool
    if _pool is None:
        _pool = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool


async def close_redis() -> None:
    """Close the Redis connection pool (call on shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None


def _cache_key(channel: str) -> str:
    return f"analysis:{channel.lower()}"


async def get_cached_analysis(channel: str) -> dict | None:
    """Return cached analysis result dict, or None if miss/expired."""
    try:
        r = await get_redis()
        raw = await r.get(_cache_key(channel))
        if raw:
            logger.info(f"Cache hit for @{channel}")
            return json.loads(raw)
    except Exception as e:
        logger.warning(f"Redis read error (non-fatal): {e}")
    return None


async def set_cached_analysis(
    channel: str,
    analysis_id: int,
    pdf_path: str,
    summary: dict,
) -> None:
    """Cache analysis result with configured TTL."""
    try:
        r = await get_redis()
        data = {
            "analysis_id": analysis_id,
            "pdf_path": pdf_path,
            **summary,
        }
        ttl_seconds = settings.CACHE_TTL_HOURS * 3600
        await r.setex(_cache_key(channel), ttl_seconds, json.dumps(data))
        logger.info(f"Cached analysis for @{channel} (TTL {settings.CACHE_TTL_HOURS}h)")
    except Exception as e:
        logger.warning(f"Redis write error (non-fatal): {e}")
