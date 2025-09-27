"""
Shared Database Migration Utilities
"""

from typing import Any

from alembic import command
from alembic.config import Config

from .connection import get_database_connection


class DatabaseMigrator:
    """Handles database schema migrations"""

    def __init__(self, alembic_cfg_path: str = "alembic.ini"):
        self.alembic_cfg = Config(alembic_cfg_path)
        self.connection = get_database_connection()

    async def run_migrations(self) -> bool:
        """Run pending database migrations"""
        try:
            # Run Alembic migrations
            command.upgrade(self.alembic_cfg, "head")
            print("✅ Database migrations completed")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

    async def check_migration_status(self) -> dict[str, Any]:
        """Check current migration status"""
        try:
            async with self.connection.get_connection() as conn:
                # Check if alembic_version table exists
                result = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                    )
                """
                )

                if result:
                    current_version = await conn.fetchval(
                        "SELECT version_num FROM alembic_version LIMIT 1"
                    )
                else:
                    current_version = None

                return {
                    "has_migrations": result,
                    "current_version": current_version,
                    "status": "ready" if result else "needs_init",
                }

        except Exception as e:
            return {"error": str(e), "status": "error"}

    async def initialize_database(self) -> bool:
        """Initialize database schema"""
        try:
            # Initialize Alembic
            command.stamp(self.alembic_cfg, "head")
            print("✅ Database initialized")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False


class DatabaseHealthCheck:
    """Database health monitoring"""

    def __init__(self):
        self.connection = get_database_connection()

    async def check_connection(self) -> dict[str, Any]:
        """Check database connectivity"""
        try:
            async with self.connection.get_connection() as conn:
                # Simple connectivity test
                result = await conn.fetchval("SELECT 1")

                return {"status": "healthy", "connected": True, "test_result": result}

        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}

    async def get_database_info(self) -> dict[str, Any]:
        """Get database information"""
        try:
            async with self.connection.get_connection() as conn:
                # Get database info
                db_version = await conn.fetchval("SELECT version()")
                db_size = await conn.fetchval(
                    """
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """
                )

                return {"version": db_version, "size": db_size, "status": "available"}

        except Exception as e:
            return {"status": "error", "error": str(e)}
