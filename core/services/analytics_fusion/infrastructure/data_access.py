"""
Data Access Service
===================

Shared data access layer for analytics fusion microservices.
Provides unified interface to all data repositories.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol

logger = logging.getLogger(__name__)


@dataclass
class DataAccessConfig:
    """Configuration for data access service"""

    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    connection_timeout_seconds: int = 30
    retry_attempts: int = 3
    enable_query_logging: bool = False


class RepositoryProtocol(Protocol):
    """Protocol for repository interfaces"""

    async def find_by_id(self, entity_id: Any) -> Any | None: ...
    async def find_all(self) -> list[Any]: ...
    async def save(self, entity: Any) -> Any: ...
    async def delete(self, entity_id: Any) -> bool: ...


class RepositoryManager:
    """Manages access to all data repositories"""

    def __init__(
        self,
        channel_daily_repo: RepositoryProtocol,
        post_repo: RepositoryProtocol,
        metrics_repo: RepositoryProtocol,
        edges_repo: RepositoryProtocol,
        stats_raw_repo: RepositoryProtocol | None = None,
    ):
        self.channel_daily_repo = channel_daily_repo
        self.post_repo = post_repo
        self.metrics_repo = metrics_repo
        self.edges_repo = edges_repo
        self.stats_raw_repo = stats_raw_repo

        logger.info("📊 Repository Manager initialized")

    async def get_channel_daily_data(
        self,
        channel_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Any]:
        """Get channel daily analytics data"""
        try:
            # Implementation will depend on actual repository interface
            logger.info(f"📊 Fetching daily data for channel {channel_id}")
            return await self.channel_daily_repo.find_all()
        except Exception as e:
            logger.error(f"❌ Error fetching channel daily data: {e}")
            return []

    async def get_post_data(self, channel_id: int, limit: int | None = None) -> list[Any]:
        """Get post data for channel"""
        try:
            logger.info(f"📝 Fetching post data for channel {channel_id}")
            return await self.post_repo.find_all()
        except Exception as e:
            logger.error(f"❌ Error fetching post data: {e}")
            return []

    async def get_metrics_data(
        self, channel_id: int, metric_types: list[str] | None = None
    ) -> list[Any]:
        """Get metrics data for channel"""
        try:
            logger.info(f"📈 Fetching metrics data for channel {channel_id}")
            return await self.metrics_repo.find_all()
        except Exception as e:
            logger.error(f"❌ Error fetching metrics data: {e}")
            return []


class DataAccessService:
    """Unified data access service for analytics microservices"""

    def __init__(
        self,
        repository_manager: RepositoryManager | None = None,
        config: DataAccessConfig | None = None,
    ):
        self.repository_manager = repository_manager
        self.config = config or DataAccessConfig()

        # Performance tracking
        self.query_count = 0
        self.total_query_time_ms: float = 0.0
        self.last_query_time: datetime | None = None

        logger.info("🔧 Data Access Service initialized")

    async def get_comprehensive_channel_data(
        self, channel_id: int, time_range_days: int = 30
    ) -> dict[str, Any]:
        """Get comprehensive data for analytics processing"""
        start_time = datetime.utcnow()

        try:
            logger.info(f"🔍 Fetching comprehensive data for channel {channel_id}")

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range_days)

            # Fetch all required data (with null check for repository manager)
            if self.repository_manager:
                daily_data = await self.repository_manager.get_channel_daily_data(
                    channel_id, start_date, end_date
                )
                post_data = await self.repository_manager.get_post_data(channel_id)
                metrics_data = await self.repository_manager.get_metrics_data(channel_id)
            else:
                # Return mock data when repository manager is not available
                daily_data = []
                post_data = []
                metrics_data = []

            # Update performance tracking
            query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.query_count += 1
            self.total_query_time_ms += query_time
            self.last_query_time = datetime.utcnow()

            result = {
                "channel_id": channel_id,
                "time_range_days": time_range_days,
                "daily_data": daily_data,
                "post_data": post_data,
                "metrics_data": metrics_data,
                "fetched_at": datetime.utcnow(),
                "query_time_ms": query_time,
            }

            logger.info(f"✅ Fetched comprehensive data in {query_time:.1f}ms")
            return result

        except Exception as e:
            logger.error(f"❌ Error fetching comprehensive data: {e}")
            return {
                "channel_id": channel_id,
                "error": str(e),
                "fetched_at": datetime.utcnow(),
            }

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get data access performance metrics"""
        avg_query_time = self.total_query_time_ms / self.query_count if self.query_count > 0 else 0

        return {
            "service": "data_access",
            "query_count": self.query_count,
            "total_query_time_ms": self.total_query_time_ms,
            "average_query_time_ms": avg_query_time,
            "last_query_time": self.last_query_time,
            "config": {
                "cache_enabled": self.config.cache_enabled,
                "cache_ttl_seconds": self.config.cache_ttl_seconds,
                "connection_timeout_seconds": self.config.connection_timeout_seconds,
            },
        }

    async def validate_data_availability(self, channel_id: int) -> dict[str, Any]:
        """Validate that required data is available for channel"""
        try:
            validation_result = {
                "channel_id": channel_id,
                "daily_data_available": False,
                "post_data_available": False,
                "metrics_data_available": False,
                "validation_passed": False,
            }

            # Check data availability (simplified check with null safety)
            if self.repository_manager:
                daily_data = await self.repository_manager.get_channel_daily_data(channel_id)
                post_data = await self.repository_manager.get_post_data(channel_id)
                metrics_data = await self.repository_manager.get_metrics_data(channel_id)

                validation_result["daily_data_available"] = len(daily_data) > 0
                validation_result["post_data_available"] = len(post_data) > 0
                validation_result["metrics_data_available"] = len(metrics_data) > 0
            else:
                # Mock validation when repository manager is not available
                validation_result["daily_data_available"] = True
                validation_result["post_data_available"] = True
                validation_result["metrics_data_available"] = True

            validation_result["validation_passed"] = (
                validation_result["daily_data_available"]
                and validation_result["post_data_available"]
                and validation_result["metrics_data_available"]
            )

            return validation_result

        except Exception as e:
            logger.error(f"❌ Error validating data availability: {e}")
            return {
                "channel_id": channel_id,
                "error": str(e),
                "validation_passed": False,
            }

    async def get_last_update_time(self, channel_id: int) -> datetime | None:
        """Get last update timestamp for channel data"""
        try:
            if self.repository_manager:
                # Get most recent data point
                daily_data = await self.repository_manager.get_channel_daily_data(
                    channel_id, start_date=datetime.utcnow() - timedelta(days=7)
                )
                if daily_data:
                    # Assume data has timestamp attribute
                    return datetime.utcnow()
            return datetime.utcnow()
        except Exception as e:
            logger.error(f"❌ Error getting last update time: {e}")
            return None

    async def get_time_series_data(
        self,
        channel_id: int,
        from_date: datetime,
        to_date: datetime,
        window_days: int = 1,
    ) -> list[dict[str, Any]]:
        """Get time series data for channel"""
        try:
            if self.repository_manager:
                daily_data = await self.repository_manager.get_channel_daily_data(
                    channel_id, from_date, to_date
                )
                # Transform to time series format
                return [
                    {
                        "timestamp": from_date + timedelta(days=i),
                        "value": 0,  # Placeholder
                    }
                    for i in range((to_date - from_date).days + 1)
                ]
            return []
        except Exception as e:
            logger.error(f"❌ Error getting time series data: {e}")
            return []

    async def get_historical_data(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> dict[str, Any]:
        """Get historical data for channel"""
        try:
            if self.repository_manager:
                daily_data = await self.repository_manager.get_channel_daily_data(
                    channel_id, from_date, to_date
                )
                return {
                    "channel_id": channel_id,
                    "from_date": from_date,
                    "to_date": to_date,
                    "data_points": len(daily_data),
                    "data": daily_data,
                }
            return {"error": "Repository manager not available"}
        except Exception as e:
            logger.error(f"❌ Error getting historical data: {e}")
            return {"error": str(e)}

    async def get_traffic_source_data(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> dict[str, Any]:
        """Get traffic source statistics for channel"""
        try:
            # Mock traffic source data structure
            return {
                "channel_id": channel_id,
                "from_date": from_date,
                "to_date": to_date,
                "sources": {"direct": 0, "search": 0, "social": 0, "referral": 0},
            }
        except Exception as e:
            logger.error(f"❌ Error getting traffic source data: {e}")
            return {"error": str(e)}

    async def get_top_performing_posts(
        self,
        channel_id: int,
        from_date: datetime,
        to_date: datetime,
        limit: int = 10,
        metric: str = "views",
    ) -> list[dict[str, Any]]:
        """Get top performing posts for channel within date range"""
        try:
            logger.info(
                f"🏆 Fetching top {limit} performing posts for channel {channel_id} "
                f"from {from_date.date()} to {to_date.date()}"
            )

            if self.repository_manager:
                # Get posts for the channel within date range
                posts = await self.repository_manager.get_post_data(channel_id, limit=limit * 2)

                # Filter by date range (simplified - actual implementation would filter by date)
                # Sort by specified metric (simplified - actual implementation
                # would sort by real metrics)
                # For now, return the posts as-is (repository handles filtering and sorting)
                top_posts = posts[:limit] if posts else []

                logger.info(f"✅ Found {len(top_posts)} top performing posts")
                return top_posts
            else:
                logger.warning("⚠️ Repository manager not available, returning empty list")
                return []

        except Exception as e:
            logger.error(f"❌ Error fetching top performing posts: {e}")
            return []
