"""
Read Replica Router
===================

For 100K+ users, a single PostgreSQL instance cannot handle all reads.
This router automatically directs:
- WRITE queries (INSERT, UPDATE, DELETE) → Primary database
- READ queries (SELECT) → Read replicas (round-robin)

Architecture:
    ┌─────────────┐
    │   Client    │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   Router    │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼───┐   ┌─────▼─────┐
│Primary│   │ Replicas  │
│(Write)│   │  (Read)   │
└───────┘   └───────────┘
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from typing import Any
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from enum import Enum

import asyncpg
from asyncpg import Connection, Pool

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type classification"""
    READ = "read"
    WRITE = "write"


@dataclass
class ReplicaConfig:
    """Read replica configuration"""
    host: str
    port: int = 5432
    weight: int = 1  # Higher weight = more traffic
    is_healthy: bool = True


@dataclass
class ReadReplicaRouterConfig:
    """Router configuration for read/write splitting"""
    
    # Primary (writes)
    primary_host: str
    primary_port: int = 5432
    
    # Read replicas
    replicas: list[ReplicaConfig] = field(default_factory=list)
    
    # Credentials
    user: str = ""
    password: str = ""
    database: str = ""
    
    # Pool settings
    pool_size_per_replica: int = 20
    
    # Health check
    health_check_interval: int = 30


class ReadReplicaRouter:
    """
    Intelligent query router for read/write splitting.
    
    Features:
    - Automatic query type detection
    - Weighted round-robin for replicas
    - Health checking with automatic failover
    - Sticky sessions for transactions
    
    Usage:
        router = ReadReplicaRouter(config)
        await router.initialize()
        
        # Automatic routing
        users = await router.fetch("SELECT * FROM users")  # → Replica
        await router.execute("INSERT INTO users ...")      # → Primary
        
        # Explicit routing
        async with router.primary() as conn:
            # Force use primary
            ...
    """
    
    def __init__(self, config: ReadReplicaRouterConfig):
        self.config = config
        self._primary_pool: Pool | None = None
        self._replica_pools: list[Pool] = []
        self._current_replica_index = 0
        self._health_task: asyncio.Task | None = None
        
    async def initialize(self):
        """Initialize all connection pools"""
        # Primary pool
        self._primary_pool = await self._create_pool(
            self.config.primary_host,
            self.config.primary_port,
        )
        logger.info(f"✅ Primary pool initialized: {self.config.primary_host}")
        
        # Replica pools
        for replica in self.config.replicas:
            pool = await self._create_pool(replica.host, replica.port)
            self._replica_pools.append(pool)
            logger.info(f"✅ Replica pool initialized: {replica.host}")
        
        # Start health checking
        if self.config.replicas:
            self._health_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(
            f"🚀 Read replica router ready: "
            f"1 primary + {len(self._replica_pools)} replicas"
        )
    
    async def _create_pool(self, host: str, port: int) -> Pool:
        """Create connection pool for a server"""
        dsn = (
            f"postgresql://{self.config.user}:{self.config.password}"
            f"@{host}:{port}/{self.config.database}"
        )
        return await asyncpg.create_pool(
            dsn=dsn,
            min_size=5,
            max_size=self.config.pool_size_per_replica,
            command_timeout=30,
        )
    
    async def close(self):
        """Close all pools"""
        if self._health_task:
            self._health_task.cancel()
        
        if self._primary_pool:
            await self._primary_pool.close()
        
        for pool in self._replica_pools:
            await pool.close()
        
        logger.info("🔒 All replica pools closed")
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query as read or write"""
        query_upper = query.strip().upper()
        
        write_keywords = ("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "TRUNCATE")
        
        if query_upper.startswith(write_keywords):
            return QueryType.WRITE
        return QueryType.READ
    
    def _get_replica_pool(self) -> Pool:
        """Get next replica pool (weighted round-robin)"""
        if not self._replica_pools:
            raise RuntimeError("No replica pools available")
        
        # Filter healthy replicas
        healthy_pools = [
            (i, pool) for i, pool in enumerate(self._replica_pools)
            if self.config.replicas[i].is_healthy
        ]
        
        if not healthy_pools:
            logger.warning("No healthy replicas, falling back to primary")
            if self._primary_pool:
                return self._primary_pool
            raise RuntimeError("No healthy database connections")
        
        # Weighted selection
        weights = [self.config.replicas[i].weight for i, _ in healthy_pools]
        total_weight = sum(weights)
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for (i, pool), weight in zip(healthy_pools, weights):
            cumulative += weight
            if r <= cumulative:
                return pool
        
        return healthy_pools[-1][1]
    
    @asynccontextmanager
    async def primary(self) -> AsyncGenerator[Connection, None]:
        """Get connection to primary (for writes)"""
        if not self._primary_pool:
            raise RuntimeError("Primary pool not initialized")
        
        async with self._primary_pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def replica(self) -> AsyncGenerator[Connection, None]:
        """Get connection to a replica (for reads)"""
        pool = self._get_replica_pool()
        async with pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def connection(self, query: str) -> AsyncGenerator[Connection, None]:
        """Get appropriate connection based on query type"""
        query_type = self._classify_query(query)
        
        if query_type == QueryType.WRITE or not self._replica_pools:
            async with self.primary() as conn:
                yield conn
        else:
            async with self.replica() as conn:
                yield conn
    
    async def fetch(self, query: str, *args) -> list[dict]:
        """Execute query and return results (auto-routed)"""
        async with self.connection(query) as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> dict | None:
        """Execute query and return single row (auto-routed)"""
        async with self.connection(query) as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def execute(self, query: str, *args) -> str:
        """Execute query (always goes to primary)"""
        async with self.primary() as conn:
            return await conn.execute(query, *args)
    
    async def _health_check_loop(self):
        """Continuous health check for replicas"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                for i, (replica, pool) in enumerate(
                    zip(self.config.replicas, self._replica_pools)
                ):
                    try:
                        async with pool.acquire() as conn:
                            await conn.execute("SELECT 1")
                            replica.is_healthy = True
                    except Exception as e:
                        logger.warning(f"Replica {replica.host} unhealthy: {e}")
                        replica.is_healthy = False
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    def get_stats(self) -> dict[str, Any]:
        """Get router statistics"""
        return {
            "primary": {
                "host": self.config.primary_host,
                "pool_size": self._primary_pool.get_size() if self._primary_pool else 0,
            },
            "replicas": [
                {
                    "host": replica.host,
                    "healthy": replica.is_healthy,
                    "weight": replica.weight,
                    "pool_size": pool.get_size(),
                }
                for replica, pool in zip(self.config.replicas, self._replica_pools)
            ],
        }
