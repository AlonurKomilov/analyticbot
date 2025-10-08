"""
Real Analytics Adapter for Telegram API integration
Handles actual data fetching from Telegram with rate limiting and error handling
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp

from apps.bot.services.adapters.mock_analytics_adapter import AnalyticsAdapter
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for API rate limiting"""

    calls_per_second: float = 1.0
    calls_per_minute: int = 20
    calls_per_hour: int = 500
    burst_allowance: int = 5


class RateLimiter:
    """
    Advanced rate limiter with multiple time windows
    """

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.call_times: list[float] = []
        self.last_call_time = 0.0

    async def acquire(self):
        """Acquire permission to make an API call"""
        current_time = time.time()

        # Clean old calls outside time windows
        self._clean_old_calls(current_time)

        # Check rate limits
        await self._enforce_limits(current_time)

        # Record this call
        self.call_times.append(current_time)
        self.last_call_time = current_time

    def _clean_old_calls(self, current_time: float):
        """Remove calls outside the tracking windows"""
        # Keep calls from last hour for hour-based rate limiting
        hour_ago = current_time - 3600
        self.call_times = [t for t in self.call_times if t >= hour_ago]

    async def _enforce_limits(self, current_time: float):
        """Enforce various rate limits"""
        # Per-second rate limiting
        time_since_last = current_time - self.last_call_time
        min_interval = 1.0 / self.config.calls_per_second
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)

        # Per-minute rate limiting
        minute_ago = current_time - 60
        calls_this_minute = len([t for t in self.call_times if t >= minute_ago])
        if calls_this_minute >= self.config.calls_per_minute:
            sleep_until = min([t for t in self.call_times if t >= minute_ago]) + 60
            sleep_time = sleep_until - current_time
            if sleep_time > 0:
                logger.warning(f"Rate limit hit (minute), sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

        # Per-hour rate limiting
        calls_this_hour = len(self.call_times)
        if calls_this_hour >= self.config.calls_per_hour:
            sleep_until = self.call_times[0] + 3600
            sleep_time = sleep_until - current_time
            if sleep_time > 0:
                logger.warning(f"Rate limit hit (hour), sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)


class TelegramAnalyticsAdapter(AnalyticsAdapter):
    """
    Real analytics adapter using Telegram Bot API and MTProto
    """

    def __init__(
        self, bot_token: str | None = None, rate_limit_config: RateLimitConfig | None = None
    ):
        self.bot_token = bot_token or getattr(settings, "TELEGRAM_BOT_TOKEN", "") or ""
        self.rate_limiter = RateLimiter(rate_limit_config or RateLimitConfig())
        self.session: aiohttp.ClientSession | None = None
        self.base_url = "https://api.telegram.org/bot"

        # Cache for API responses to reduce calls
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info("TelegramAnalyticsAdapter initialized")

    def get_adapter_name(self) -> str:
        return "telegram_analytics"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def _make_api_call(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make rate-limited API call to Telegram
        """
        if not self.bot_token:
            raise ValueError("Telegram bot token not configured")

        # Check cache first
        params_dict = params or {}
        cache_key = f"{method}:{hash(str(sorted(params_dict.items())))}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                logger.debug(f"Using cached data for {method}")
                return cached_data

        # Rate limiting
        await self.rate_limiter.acquire()

        session = await self._get_session()
        url = f"{self.base_url}{self.bot_token}/{method}"

        try:
            async with session.get(url, params=params or {}) as response:
                if response.status == 429:
                    # Handle rate limit from Telegram
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Telegram rate limit hit, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    # Retry once
                    async with session.get(url, params=params or {}) as retry_response:
                        retry_response.raise_for_status()
                        data = await retry_response.json()
                elif response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Telegram API error {response.status}: {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text,
                    )
                else:
                    data = await response.json()

                if not data.get("ok"):
                    raise Exception(
                        f"Telegram API error: {data.get('description', 'Unknown error')}"
                    )

                # Cache successful response
                self.cache[cache_key] = (data, time.time())

                logger.debug(f"Successful API call to {method}")
                return data

        except TimeoutError:
            logger.error(f"Timeout calling Telegram API method {method}")
            raise
        except Exception as e:
            logger.error(f"Error calling Telegram API method {method}: {e}")
            raise

    async def _get_channel_info(self, channel_id: str) -> dict[str, Any]:
        """Get basic channel information"""
        try:
            response = await self._make_api_call("getChat", {"chat_id": channel_id})
            return response.get("result", {})
        except Exception as e:
            logger.error(f"Failed to get channel info for {channel_id}: {e}")
            return {}

    async def _get_channel_member_count(self, channel_id: str) -> int:
        """Get channel member count"""
        try:
            response = await self._make_api_call("getChatMemberCount", {"chat_id": channel_id})
            return response.get("result", 0)
        except Exception as e:
            logger.error(f"Failed to get member count for {channel_id}: {e}")
            return 0

    async def get_channel_analytics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get real channel analytics from Telegram"""

        try:
            # Get basic channel info
            channel_info = await self._get_channel_info(channel_id)
            member_count = await self._get_channel_member_count(channel_id)

            # Note: Telegram Bot API has limited analytics capabilities
            # For full analytics, you'd need MTProto client or Telegram Analytics API

            analytics = {
                "channel_id": channel_id,
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": (end_date - start_date).days + 1,
                },
                "channel_info": {
                    "title": channel_info.get("title", "Unknown Channel"),
                    "type": channel_info.get("type", "channel"),
                    "description": channel_info.get("description", ""),
                    "username": channel_info.get("username"),
                    "member_count": member_count,
                },
                "overview": {
                    "total_subscribers": member_count,
                    "subscriber_change": 0,  # Would need historical data
                    "total_views": 0,  # Not available via Bot API
                    "total_posts": 0,  # Would need to count messages
                    "avg_engagement_rate": 0.0,  # Not available via Bot API
                    "avg_views_per_post": 0,
                },
                "limitations": {
                    "note": "Telegram Bot API has limited analytics capabilities",
                    "available_data": ["basic_channel_info", "member_count"],
                    "unavailable_data": [
                        "view_counts",
                        "engagement_metrics",
                        "historical_subscriber_data",
                        "detailed_post_analytics",
                    ],
                    "recommendation": "Use MTProto client or Telegram Analytics API for full analytics",
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "api_version": "bot_api_6.0",
                    "real_data": True,
                },
            }

            logger.info(f"Retrieved Telegram channel analytics for {channel_id}")
            return analytics

        except Exception as e:
            logger.error(f"Error getting channel analytics for {channel_id}: {e}")
            # Return error response with structure similar to successful response
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": (end_date - start_date).days + 1,
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "error": True,
                },
            }

    async def get_post_analytics(self, post_id: str, channel_id: str) -> dict[str, Any]:
        """Get real post analytics from Telegram"""

        try:
            # Note: Getting individual post analytics requires message_id
            # Bot API doesn't provide view counts for individual messages

            analytics = {
                "post_id": post_id,
                "channel_id": channel_id,
                "limitations": {
                    "note": "Individual post analytics not available via Telegram Bot API",
                    "available_via": ["MTProto client", "Telegram Analytics API"],
                    "bot_api_limitations": [
                        "No view counts for messages",
                        "No engagement metrics per message",
                        "Limited message history access",
                    ],
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "limited_data": True,
                },
            }

            logger.info(f"Retrieved limited Telegram post analytics for {post_id}")
            return analytics

        except Exception as e:
            logger.error(f"Error getting post analytics for {post_id}: {e}")
            return {
                "post_id": post_id,
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "error": True,
                },
            }

    async def get_audience_demographics(self, channel_id: str) -> dict[str, Any]:
        """Get audience demographics (limited via Bot API)"""

        try:
            channel_info = await self._get_channel_info(channel_id)
            member_count = await self._get_channel_member_count(channel_id)

            demographics = {
                "channel_id": channel_id,
                "total_audience": member_count,
                "channel_info": {
                    "title": channel_info.get("title", "Unknown Channel"),
                    "type": channel_info.get("type", "channel"),
                    "username": channel_info.get("username"),
                },
                "limitations": {
                    "note": "Demographic data not available via Telegram Bot API",
                    "available_data": ["total_member_count", "basic_channel_info"],
                    "unavailable_data": [
                        "age_distribution",
                        "gender_distribution",
                        "geographic_distribution",
                        "device_usage",
                        "activity_patterns",
                    ],
                    "recommendation": "Use Telegram Analytics API for detailed demographics",
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "limited_data": True,
                },
            }

            logger.info(f"Retrieved limited Telegram demographics for {channel_id}")
            return demographics

        except Exception as e:
            logger.error(f"Error getting audience demographics for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "error": True,
                },
            }

    async def get_engagement_metrics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get engagement metrics (limited via Bot API)"""

        return {
            "channel_id": channel_id,
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": (end_date - start_date).days + 1,
            },
            "limitations": {
                "note": "Engagement metrics not available via Telegram Bot API",
                "available_via": ["MTProto client", "Telegram Analytics API"],
                "required_for_engagement": [
                    "Message view counts",
                    "Reaction data",
                    "Forward counts",
                    "Comment counts",
                ],
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "telegram_analytics",
                "real_data": True,
                "limited_data": True,
            },
        }

    async def get_growth_metrics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get growth metrics (limited via Bot API)"""

        try:
            current_member_count = await self._get_channel_member_count(channel_id)

            return {
                "channel_id": channel_id,
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": (end_date - start_date).days + 1,
                },
                "current_data": {"current_member_count": current_member_count},
                "limitations": {
                    "note": "Historical growth data not available via Telegram Bot API",
                    "available_data": ["current_member_count"],
                    "unavailable_data": [
                        "historical_member_counts",
                        "growth_rates",
                        "acquisition_channels",
                        "retention_metrics",
                    ],
                    "recommendation": "Store periodic snapshots to track growth over time",
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "limited_data": True,
                },
            }

        except Exception as e:
            logger.error(f"Error getting growth metrics for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "adapter": "telegram_analytics",
                    "real_data": True,
                    "error": True,
                },
            }

    async def health_check(self) -> dict[str, Any]:
        """Check Telegram API connectivity"""

        try:
            # Simple API call to check connectivity
            response = await self._make_api_call("getMe")
            bot_info = response.get("result", {})

            return {
                "status": "healthy",
                "adapter": "telegram_analytics",
                "timestamp": int(datetime.now().timestamp()),
                "bot_info": {
                    "id": bot_info.get("id"),
                    "username": bot_info.get("username"),
                    "first_name": bot_info.get("first_name"),
                    "can_join_groups": bot_info.get("can_join_groups"),
                    "can_read_all_group_messages": bot_info.get("can_read_all_group_messages"),
                },
                "api_features": {
                    "available": ["basic_channel_info", "member_counts", "bot_management"],
                    "limited": ["message_analytics", "engagement_metrics", "demographic_data"],
                },
                "rate_limiting": {
                    "calls_per_second": self.rate_limiter.config.calls_per_second,
                    "calls_per_minute": self.rate_limiter.config.calls_per_minute,
                    "calls_per_hour": self.rate_limiter.config.calls_per_hour,
                },
            }

        except Exception as e:
            logger.error(f"Telegram API health check failed: {e}")
            return {
                "status": "unhealthy",
                "adapter": "telegram_analytics",
                "timestamp": int(datetime.now().timestamp()),
                "error": str(e),
                "bot_token_configured": bool(self.bot_token),
            }

    async def close(self):
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        self.cache.clear()
        logger.info("TelegramAnalyticsAdapter closed")
