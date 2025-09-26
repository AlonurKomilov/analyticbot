"""
Shared Database Configuration and Utilities
"""

from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
import os
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "analyticbot"
    username: str = "postgres"
    password: str = ""
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load config from environment variables"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "analyticbot"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )


class DatabaseConnection:
    """Shared database connection utilities"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig.from_env()
        self._pool: Optional[asyncpg.Pool] = None
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool"""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=5,
                max_size=20
            )
        return self._pool
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            yield conn
    
    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None

def get_database_connection() -> DatabaseConnection:
    """Get global database connection instance"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection
