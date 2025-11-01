"""
Cache Service
============

Microservice responsible for prediction result caching.
Handles cache storage, retrieval, key generation, and management.
"""

import hashlib
import logging
from datetime import datetime
from typing import Any

from .models import (
    MAX_CACHE_SIZE,
    CacheServiceProtocol,
    HealthMetrics,
    PredictionRequest,
    PredictionResult,
    ServiceHealth,
)

logger = logging.getLogger(__name__)


class CacheService(CacheServiceProtocol):
    """
    Prediction result caching service.

    Single responsibility: Cache management for prediction results.
    """

    def __init__(self, max_cache_size: int = MAX_CACHE_SIZE):
        self.max_cache_size = max_cache_size
        self.cache: dict[str, PredictionResult] = {}
        self.access_times: dict[str, datetime] = {}

        # Health tracking
        self.health_metrics = HealthMetrics()
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info(f"💾 Cache Service initialized with max size: {max_cache_size}")

    def get_cached_result(self, cache_key: str) -> PredictionResult | None:
        """
        Retrieve cached prediction result

        Args:
            cache_key: Unique cache key for the prediction

        Returns:
            Cached result if available, None otherwise
        """
        try:
            if cache_key in self.cache:
                # Update access time
                self.access_times[cache_key] = datetime.utcnow()
                self.cache_hits += 1

                # Mark result as cached
                result = self.cache[cache_key]
                result.cached = True

                logger.debug(f"📋 Cache hit for key: {cache_key}")
                return result
            else:
                self.cache_misses += 1
                logger.debug(f"❌ Cache miss for key: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"❌ Cache retrieval failed: {e}")
            return None

    def cache_result(self, cache_key: str, result: PredictionResult) -> None:
        """
        Store prediction result in cache

        Args:
            cache_key: Unique cache key
            result: Prediction result to cache
        """
        try:
            # Check cache size and evict if necessary
            if len(self.cache) >= self.max_cache_size:
                self._evict_oldest_entry()

            # Store result and access time
            self.cache[cache_key] = result
            self.access_times[cache_key] = datetime.utcnow()

            # Update health metrics
            self.health_metrics.successful_predictions += 1

            logger.debug(f"💾 Cached result for key: {cache_key}")

        except Exception as e:
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Cache storage failed: {e}")

    def generate_key(self, request: PredictionRequest) -> str:
        """
        Generate unique cache key for prediction request

        Args:
            request: Prediction request

        Returns:
            Unique cache key string
        """
        try:
            # Create hashable representation of request
            key_components = [
                str(request.forecast_periods),
                str(request.confidence_interval),
                str(request.include_uncertainty),
            ]

            # Add data hash
            data_str = self._serialize_data(request.data)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()
            key_components.append(data_hash)

            # Generate final key
            cache_key = f"growth_{'_'.join(key_components)}"

            logger.debug(f"🔑 Generated cache key: {cache_key}")
            return cache_key

        except Exception as e:
            logger.error(f"❌ Cache key generation failed: {e}")
            # Return fallback key
            return f"growth_fallback_{datetime.utcnow().timestamp()}"

    def clear_cache(self) -> None:
        """Clear all cached results"""
        try:
            cache_size = len(self.cache)
            self.cache.clear()
            self.access_times.clear()

            # Reset hit/miss counters
            self.cache_hits = 0
            self.cache_misses = 0

            logger.info(f"🧹 Cache cleared: {cache_size} entries removed")

        except Exception as e:
            logger.error(f"❌ Cache clearing failed: {e}")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics"""
        try:
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0

            # Update hit rate in health metrics
            self.health_metrics.cache_hit_rate = hit_rate

            return {
                "cache_size": len(self.cache),
                "max_cache_size": self.max_cache_size,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "hit_rate": hit_rate,
                "utilization": (
                    len(self.cache) / self.max_cache_size if self.max_cache_size > 0 else 0.0
                ),
            }

        except Exception as e:
            logger.error(f"❌ Cache stats calculation failed: {e}")
            return {}

    def evict_expired_entries(self, max_age_hours: int = 24) -> int:
        """
        Evict entries older than specified age

        Args:
            max_age_hours: Maximum age in hours before eviction

        Returns:
            Number of entries evicted
        """
        try:
            current_time = datetime.utcnow()
            expired_keys = []

            for key, access_time in self.access_times.items():
                age_hours = (current_time - access_time).total_seconds() / 3600
                if age_hours > max_age_hours:
                    expired_keys.append(key)

            # Remove expired entries
            for key in expired_keys:
                del self.cache[key]
                del self.access_times[key]

            if expired_keys:
                logger.info(f"🧹 Evicted {len(expired_keys)} expired cache entries")

            return len(expired_keys)

        except Exception as e:
            logger.error(f"❌ Cache expiration cleanup failed: {e}")
            return 0

    def get_health(self) -> ServiceHealth:
        """Get cache service health status"""
        try:
            stats = self.get_cache_stats()

            # Cache is healthy if hit rate is reasonable and not overloaded
            is_healthy = (
                stats.get("hit_rate", 0) >= 0.1
                or stats.get("cache_size", 0) < 10  # Low hit rate OK if cache is small
                and stats.get("utilization", 0) < 0.95  # Not overloaded
            )

            return ServiceHealth(
                service_name="cache_service",
                is_healthy=is_healthy,
                metrics=self.health_metrics,
                last_check=datetime.utcnow(),
            )

        except Exception as e:
            return ServiceHealth(
                service_name="cache_service",
                is_healthy=False,
                metrics=HealthMetrics(),
                error_message=str(e),
            )

    # Private helper methods

    def _evict_oldest_entry(self) -> None:
        """Evict the least recently accessed cache entry"""
        try:
            if not self.access_times:
                return

            # Find oldest entry
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])

            # Remove from both cache and access times
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

            logger.debug(f"🗑️ Evicted oldest cache entry: {oldest_key}")

        except Exception as e:
            logger.error(f"❌ Cache eviction failed: {e}")

    def _serialize_data(self, data: Any) -> str:
        """Serialize data for hashing"""
        try:
            import numpy as np
            import pandas as pd

            if isinstance(data, pd.DataFrame):
                return str(data.values.tobytes())
            elif isinstance(data, (list, dict)):
                return str(sorted(str(data).encode()))
            elif isinstance(data, np.ndarray):
                return str(data.tobytes())
            else:
                return str(data)

        except Exception as e:
            logger.error(f"❌ Data serialization failed: {e}")
            return str(hash(str(data)))
