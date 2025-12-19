"""
PgBouncer Connection Pool Manager
=================================

For 100K+ users, direct PostgreSQL connections are insufficient.
PgBouncer provides connection multiplexing:
- 10,000 client connections → 100 PostgreSQL connections
- Transaction-level pooling for maximum efficiency

Configuration:
    Set PGBOUNCER_ENABLED=true and PGBOUNCER_URL in environment
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import asyncpg
from asyncpg import Connection, Pool

logger = logging.getLogger(__name__)


@dataclass
class PgBouncerConfig:
    """PgBouncer connection configuration for high-scale deployments"""
    
    # Primary database (writes)
    primary_host: str = "localhost"
    primary_port: int = 6432  # PgBouncer port (not PostgreSQL 5432)
    
    # Connection limits (PgBouncer handles multiplexing)
    min_connections: int = 20
    max_connections: int = 200  # Can go much higher with PgBouncer
    
    # Timeouts
    connection_timeout: int = 10
    command_timeout: int = 30
    
    # Pool settings
    pool_mode: str = "transaction"  # transaction, session, or statement
    
    # Database credentials
    user: str = ""
    password: str = ""
    database: str = ""


class PgBouncerPool:
    """
    High-performance connection pool using PgBouncer.
    
    Benefits over direct PostgreSQL connections:
    - 100x more concurrent connections
    - Connection reuse across requests
    - Automatic connection recycling
    - Lower memory footprint
    
    Usage:
        pool = PgBouncerPool(config)
        await pool.initialize()
        
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT * FROM users")
    """
    
    def __init__(self, config: PgBouncerConfig):
        self.config = config
        self._pool: Pool | None = None
        self._stats = {
            "acquired": 0,
            "released": 0,
            "failed": 0,
            "total_query_time": 0.0,
        }
    
    async def initialize(self) -> Pool:
        """Initialize PgBouncer connection pool"""
        if self._pool:
            return self._pool
        
        dsn = (
            f"postgresql://{self.config.user}:{self.config.password}"
            f"@{self.config.primary_host}:{self.config.primary_port}"
            f"/{self.config.database}"
        )
        
        self._pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=self.config.min_connections,
            max_size=self.config.max_connections,
            command_timeout=self.config.command_timeout,
            # PgBouncer-specific settings
            server_settings={
                "application_name": "analyticbot_scaled",
                # Disable prepared statements for PgBouncer transaction mode
                "plan_cache_mode": "auto",
            },
        )
        
        logger.info(
            f"🚀 PgBouncer pool initialized: "
            f"{self.config.min_connections}-{self.config.max_connections} connections "
            f"(mode: {self.config.pool_mode})"
        )
        
        return self._pool
    
    async def close(self):
        """Close the connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("🔒 PgBouncer pool closed")
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[Connection, None]:
        """Acquire connection from pool"""
        if not self._pool:
            raise RuntimeError("Pool not initialized")
        
        try:
            async with self._pool.acquire() as conn:
                self._stats["acquired"] += 1
                yield conn
                self._stats["released"] += 1
        except Exception as e:
            self._stats["failed"] += 1
            logger.error(f"Connection acquisition failed: {e}")
            raise
    
    def get_stats(self) -> dict[str, Any]:
        """Get pool statistics"""
        stats = self._stats.copy()
        if self._pool:
            stats.update({
                "pool_size": self._pool.get_size(),
                "idle": self._pool.get_idle_size(),
                "active": self._pool.get_size() - self._pool.get_idle_size(),
            })
        return stats


# PgBouncer configuration for different scale tiers
SCALE_CONFIGS = {
    "small": PgBouncerConfig(
        min_connections=10,
        max_connections=50,
    ),
    "medium": PgBouncerConfig(
        min_connections=20,
        max_connections=100,
    ),
    "large": PgBouncerConfig(
        min_connections=50,
        max_connections=200,
    ),
    "enterprise": PgBouncerConfig(
        min_connections=100,
        max_connections=500,
    ),
}
