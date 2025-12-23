"""
Rate Limit Monitoring and Configuration Service

Provides admin APIs for:
1. Monitoring rate limit usage across all services
2. Configuring rate limits dynamically
3. Viewing rate limit statistics

Domain: Admin system monitoring
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RateLimitService(str, Enum):
    """Available services with rate limiting"""

    BOT_CREATION = "bot_creation"
    BOT_OPERATIONS = "bot_operations"
    ADMIN_OPERATIONS = "admin_operations"
    AUTH_LOGIN = "auth_login"
    AUTH_REGISTER = "auth_register"
    PUBLIC_READ = "public_read"
    WEBHOOK = "webhook"
    ANALYTICS = "analytics"
    EXPORT = "export"
    AI_CHAT = "ai_chat"
    CHANNEL_ADD = "channel_add"
    REPORT_GENERATE = "report_generate"
    GLOBAL = "global"


@dataclass
class RateLimitStats:
    """Statistics for a rate limit"""

    service: str
    current_usage: int
    limit: int
    period: str  # e.g., "minute", "hour"
    remaining: int
    reset_at: datetime | None
    utilization_percent: float
    is_at_limit: bool


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit"""

    service: str
    limit: int
    period: str
    enabled: bool = True
    description: str = ""


# Default rate limit configurations
DEFAULT_RATE_LIMITS: dict[str, RateLimitConfig] = {
    RateLimitService.BOT_CREATION: RateLimitConfig(
        service=RateLimitService.BOT_CREATION,
        limit=5,
        period="hour",
        description="Bot creation operations",
    ),
    RateLimitService.BOT_OPERATIONS: RateLimitConfig(
        service=RateLimitService.BOT_OPERATIONS,
        limit=100,
        period="minute",
        description="General bot operations",
    ),
    RateLimitService.ADMIN_OPERATIONS: RateLimitConfig(
        service=RateLimitService.ADMIN_OPERATIONS,
        limit=30,
        period="minute",
        description="Admin panel operations",
    ),
    RateLimitService.AUTH_LOGIN: RateLimitConfig(
        service=RateLimitService.AUTH_LOGIN,
        limit=10,
        period="minute",
        description="Login attempts",
    ),
    RateLimitService.AUTH_REGISTER: RateLimitConfig(
        service=RateLimitService.AUTH_REGISTER,
        limit=3,
        period="hour",
        description="Registration attempts",
    ),
    RateLimitService.PUBLIC_READ: RateLimitConfig(
        service=RateLimitService.PUBLIC_READ,
        limit=200,
        period="minute",
        description="Public API reads",
    ),
    RateLimitService.WEBHOOK: RateLimitConfig(
        service=RateLimitService.WEBHOOK,
        limit=1000,
        period="minute",
        description="Webhook callbacks",
    ),
    RateLimitService.ANALYTICS: RateLimitConfig(
        service=RateLimitService.ANALYTICS,
        limit=60,
        period="minute",
        description="Analytics queries",
    ),
    RateLimitService.EXPORT: RateLimitConfig(
        service=RateLimitService.EXPORT,
        limit=10,
        period="minute",
        description="Data export operations",
    ),
    RateLimitService.AI_CHAT: RateLimitConfig(
        service=RateLimitService.AI_CHAT,
        limit=20,
        period="minute",
        description="AI chat requests",
    ),
    RateLimitService.CHANNEL_ADD: RateLimitConfig(
        service=RateLimitService.CHANNEL_ADD,
        limit=30,
        period="minute",
        description="Channel add operations",
    ),
    RateLimitService.REPORT_GENERATE: RateLimitConfig(
        service=RateLimitService.REPORT_GENERATE,
        limit=5,
        period="minute",
        description="Report generation",
    ),
    RateLimitService.GLOBAL: RateLimitConfig(
        service=RateLimitService.GLOBAL,
        limit=2000,
        period="minute",
        description="Global API rate limit",
    ),
}


class RateLimitMonitoringService:
    """
    Service for monitoring and configuring rate limits.

    Provides:
    - Real-time usage statistics
    - Historical usage data
    - Dynamic configuration updates
    - Per-user and global rate limit management
    """

    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._config_key = "ratelimit:config"
        self._stats_key_prefix = "ratelimit:stats"
        self._history_key_prefix = "ratelimit:history"

        # In-memory fallback for configs
        self._local_configs: dict[str, RateLimitConfig] = {}
        self._local_stats: dict[str, dict] = {}

    async def _get_redis(self):
        """Get Redis client (lazy initialization)"""
        if self._redis:
            return self._redis
        try:
            from apps.di import get_container

            container = get_container()
            self._redis = await container.cache.redis_client()
            return self._redis
        except Exception as e:
            logger.warning(f"Redis not available for rate limit monitoring: {e}")
            return None

    # =========================================================================
    # CONFIGURATION MANAGEMENT
    # =========================================================================

    async def get_all_configs(self) -> list[dict]:
        """Get all rate limit configurations"""
        redis = await self._get_redis()

        if redis:
            try:
                # Try to get from Redis
                config_data = await redis.hgetall(self._config_key)
                if config_data:
                    return [json.loads(v) for v in config_data.values()]
            except Exception as e:
                logger.warning(f"Redis error getting configs: {e}")

        # Return defaults + local overrides
        result = []
        for service, default_config in DEFAULT_RATE_LIMITS.items():
            if service in self._local_configs:
                config = self._local_configs[service]
            else:
                config = default_config

            result.append(
                {
                    "service": config.service,
                    "limit": config.limit,
                    "period": config.period,
                    "enabled": config.enabled,
                    "description": config.description,
                }
            )

        return result

    async def get_config(self, service: str) -> dict | None:
        """Get rate limit configuration for a specific service"""
        redis = await self._get_redis()

        if redis:
            try:
                config_data = await redis.hget(self._config_key, service)
                if config_data:
                    return json.loads(config_data)
            except Exception as e:
                logger.warning(f"Redis error: {e}")

        # Check local/defaults
        if service in self._local_configs:
            config = self._local_configs[service]
        elif service in DEFAULT_RATE_LIMITS:
            config = DEFAULT_RATE_LIMITS[service]
        else:
            return None

        return {
            "service": config.service,
            "limit": config.limit,
            "period": config.period,
            "enabled": config.enabled,
            "description": config.description,
        }

    async def update_config(
        self,
        service: str,
        limit: int | None = None,
        period: str | None = None,
        enabled: bool | None = None,
        description: str | None = None,
    ) -> dict:
        """
        Update rate limit configuration for a service.

        Returns the updated configuration.
        """
        # Get current config
        current = await self.get_config(service)
        if not current:
            # Create new config
            current = {
                "service": service,
                "limit": limit or 100,
                "period": period or "minute",
                "enabled": enabled if enabled is not None else True,
                "description": description or f"Rate limit for {service}",
            }
        else:
            # Update existing
            if limit is not None:
                current["limit"] = limit
            if period is not None:
                current["period"] = period
            if enabled is not None:
                current["enabled"] = enabled
            if description is not None:
                current["description"] = description

        # Save to Redis
        redis = await self._get_redis()
        if redis:
            try:
                await redis.hset(self._config_key, service, json.dumps(current))
                logger.info(f"Updated rate limit config for {service}: {current}")
            except Exception as e:
                logger.warning(f"Redis error saving config: {e}")

        # Also save locally
        self._local_configs[service] = RateLimitConfig(
            service=current["service"],
            limit=current["limit"],
            period=current["period"],
            enabled=current["enabled"],
            description=current["description"],
        )

        return current

    # =========================================================================
    # USAGE STATISTICS
    # =========================================================================

    async def record_request(
        self, service: str, user_id: int | None = None, ip: str | None = None
    ) -> None:
        """Record a request for rate limit tracking"""
        redis = await self._get_redis()
        now = datetime.utcnow()
        minute_key = now.strftime("%Y%m%d%H%M")

        if redis:
            try:
                # Increment counters
                global_key = f"{self._stats_key_prefix}:{service}:global:{minute_key}"
                await redis.incr(global_key)
                await redis.expire(global_key, 3600)  # Keep for 1 hour

                if user_id:
                    user_key = f"{self._stats_key_prefix}:{service}:user:{user_id}:{minute_key}"
                    await redis.incr(user_key)
                    await redis.expire(user_key, 3600)

                if ip:
                    ip_key = f"{self._stats_key_prefix}:{service}:ip:{ip}:{minute_key}"
                    await redis.incr(ip_key)
                    await redis.expire(ip_key, 3600)

            except Exception as e:
                logger.warning(f"Redis error recording request: {e}")
        else:
            # Local fallback
            key = f"{service}:{minute_key}"
            if key not in self._local_stats:
                self._local_stats[key] = {"count": 0, "timestamp": now}
            self._local_stats[key]["count"] += 1

    async def get_current_usage(self, service: str) -> RateLimitStats:
        """Get current usage statistics for a service"""
        config = await self.get_config(service)
        if not config:
            config = {"limit": 100, "period": "minute", "enabled": True}

        redis = await self._get_redis()
        now = datetime.utcnow()
        minute_key = now.strftime("%Y%m%d%H%M")

        current_usage = 0

        if redis:
            try:
                global_key = f"{self._stats_key_prefix}:{service}:global:{minute_key}"
                usage = await redis.get(global_key)
                current_usage = int(usage) if usage else 0
            except Exception as e:
                logger.warning(f"Redis error getting usage: {e}")
        else:
            # Local fallback
            key = f"{service}:{minute_key}"
            if key in self._local_stats:
                current_usage = self._local_stats[key]["count"]

        limit = config["limit"]
        remaining = max(0, limit - current_usage)
        utilization = (current_usage / limit * 100) if limit > 0 else 0

        # Calculate reset time based on period
        if config["period"] == "minute":
            reset_at = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        elif config["period"] == "hour":
            reset_at = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            reset_at = now + timedelta(minutes=1)

        return RateLimitStats(
            service=service,
            current_usage=current_usage,
            limit=limit,
            period=config["period"],
            remaining=remaining,
            reset_at=reset_at,
            utilization_percent=round(utilization, 2),
            is_at_limit=current_usage >= limit,
        )

    async def get_all_usage_stats(self) -> list[dict]:
        """Get usage statistics for all services"""
        stats = []
        for service in DEFAULT_RATE_LIMITS.keys():
            try:
                usage = await self.get_current_usage(service)
                stats.append(
                    {
                        "service": usage.service,
                        "current_usage": usage.current_usage,
                        "limit": usage.limit,
                        "period": usage.period,
                        "remaining": usage.remaining,
                        "reset_at": (usage.reset_at.isoformat() if usage.reset_at else None),
                        "utilization_percent": usage.utilization_percent,
                        "is_at_limit": usage.is_at_limit,
                    }
                )
            except Exception as e:
                logger.warning(f"Error getting stats for {service}: {e}")

        return stats

    async def get_usage_history(
        self,
        service: str,
        hours: int = 24,
    ) -> list[dict]:
        """Get historical usage data for a service"""
        redis = await self._get_redis()
        history = []
        now = datetime.utcnow()

        if redis:
            try:
                # Get data for each minute in the time range
                for i in range(hours * 60):
                    past_time = now - timedelta(minutes=i)
                    minute_key = past_time.strftime("%Y%m%d%H%M")
                    global_key = f"{self._stats_key_prefix}:{service}:global:{minute_key}"

                    usage = await redis.get(global_key)
                    if usage:
                        history.append(
                            {
                                "timestamp": past_time.isoformat(),
                                "usage": int(usage),
                            }
                        )
            except Exception as e:
                logger.warning(f"Redis error getting history: {e}")

        return history

    async def get_top_users(self, service: str, limit: int = 10) -> list[dict]:
        """Get top users by rate limit usage"""
        redis = await self._get_redis()
        if not redis:
            return []

        try:
            now = datetime.utcnow()
            minute_key = now.strftime("%Y%m%d%H%M")
            pattern = f"{self._stats_key_prefix}:{service}:user:*:{minute_key}"

            users = []
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                for key in keys:
                    user_id = key.split(":")[-2]
                    usage = await redis.get(key)
                    if usage:
                        users.append(
                            {
                                "user_id": int(user_id),
                                "usage": int(usage),
                            }
                        )
                if cursor == 0:
                    break

            # Sort by usage and return top N
            users.sort(key=lambda x: x["usage"], reverse=True)
            return users[:limit]

        except Exception as e:
            logger.warning(f"Redis error getting top users: {e}")
            return []

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    async def reset_limits_for_user(self, user_id: int) -> bool:
        """Reset rate limits for a specific user"""
        redis = await self._get_redis()
        if not redis:
            return False

        try:
            pattern = f"{self._stats_key_prefix}:*:user:{user_id}:*"
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await redis.delete(*keys)
                    deleted += len(keys)
                if cursor == 0:
                    break

            logger.info(f"Reset {deleted} rate limit keys for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error resetting limits for user {user_id}: {e}")
            return False

    async def reset_limits_for_ip(self, ip: str) -> bool:
        """Reset rate limits for a specific IP"""
        redis = await self._get_redis()
        if not redis:
            return False

        try:
            pattern = f"{self._stats_key_prefix}:*:ip:{ip}:*"
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await redis.delete(*keys)
                    deleted += len(keys)
                if cursor == 0:
                    break

            logger.info(f"Reset {deleted} rate limit keys for IP {ip}")
            return True

        except Exception as e:
            logger.error(f"Error resetting limits for IP {ip}: {e}")
            return False


# Global instance (singleton)
_rate_limit_service: RateLimitMonitoringService | None = None


def get_rate_limit_service() -> RateLimitMonitoringService:
    """Get the global rate limit monitoring service instance"""
    global _rate_limit_service
    if _rate_limit_service is None:
        _rate_limit_service = RateLimitMonitoringService()
    return _rate_limit_service
