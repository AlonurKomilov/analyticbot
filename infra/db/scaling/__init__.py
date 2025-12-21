# infra/db/scaling/__init__.py
"""
Database Scaling Infrastructure
================================

Components for scaling to 100,000+ users:

1. PgBouncer Pool - Connection multiplexing (50 connections → 200-500)
2. Read Replica Router - Distribute reads across replicas  
3. Partition Manager - Table partitioning for large datasets
4. Query Cache Manager - Multi-tier caching for 70-90% DB load reduction

Usage at Scale:
    
    # 10K users (current)
    - Standard connection pool (50 connections)
    - Basic Redis caching
    
    # 50K users  
    - PgBouncer for connection multiplexing
    - Add 1 read replica
    - Enable aggressive caching
    
    # 100K+ users
    - PgBouncer with enterprise config (500 connections)
    - 2-3 read replicas with weighted routing
    - Table partitioning for post_metrics, logs
    - Multi-tier caching strategy
    
    # 500K+ users
    - Consider horizontal sharding
    - Multiple PgBouncer instances
    - 5+ read replicas
    - CDN for static analytics
"""

from .pgbouncer_pool import PgBouncerPool, PgBouncerConfig, SCALE_CONFIGS
from .read_replica_router import ReadReplicaRouter, ReadReplicaRouterConfig
from .partition_manager import PartitionManager, PARTITION_MIGRATIONS
from .cache_manager import QueryCacheManager, CacheTier, CacheKey, CACHE_PATTERNS
from .cached_queries import (
    set_cache_manager,
    get_cached_user,
    get_cached_user_by_telegram_id,
    get_cached_channel,
    get_cached_user_channels,
    get_cached_channel_stats,
    get_cached_user_subscription,
    get_cached_user_credits,
    get_cached_marketplace_services,
    get_cached_feature_flags,
    invalidate_user_cache,
    invalidate_channel_cache,
    invalidate_channel_stats_cache,
    invalidate_user_subscription_cache,
    invalidate_marketplace_cache,
    invalidate_feature_flags_cache,
    cached_query,
    get_cache_stats,
)

__all__ = [
    # Connection pooling
    "PgBouncerPool",
    "PgBouncerConfig", 
    "SCALE_CONFIGS",
    # Read replicas
    "ReadReplicaRouter",
    "ReadReplicaRouterConfig",
    # Partitioning
    "PartitionManager",
    "PARTITION_MIGRATIONS",
    # Caching
    "QueryCacheManager",
    "CacheTier",
    "CacheKey",
    "CACHE_PATTERNS",
    # Cached query wrappers
    "set_cache_manager",
    "get_cached_user",
    "get_cached_user_by_telegram_id",
    "get_cached_channel",
    "get_cached_user_channels",
    "get_cached_channel_stats",
    "get_cached_user_subscription",
    "get_cached_user_credits",
    "get_cached_marketplace_services",
    "get_cached_feature_flags",
    "invalidate_user_cache",
    "invalidate_channel_cache",
    "invalidate_channel_stats_cache",
    "invalidate_user_subscription_cache",
    "invalidate_marketplace_cache",
    "invalidate_feature_flags_cache",
    "cached_query",
    "get_cache_stats",
]
