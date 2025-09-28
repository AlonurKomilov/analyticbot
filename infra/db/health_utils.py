"""
Database Health Utilities
Database health monitoring utilities
"""

import asyncio
import logging
import time
from typing import Any, Dict

from infra.db.connection_manager import db_manager

logger = logging.getLogger(__name__)


async def is_db_healthy() -> bool:
    """Check if database is healthy"""
    try:
        health_status = await db_manager.health_check()
        return health_status.get("healthy", False)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def get_db_health_details() -> Dict[str, Any]:
    """Get detailed database health information"""
    try:
        return await db_manager.health_check()
    except Exception as e:
        logger.error(f"Failed to get database health details: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "timestamp": time.time()
        }


async def check_db_connectivity() -> Dict[str, Any]:
    """Check database connectivity with detailed metrics"""
    start_time = time.time()
    
    try:
        # Test basic connectivity
        async with db_manager.connection() as conn:
            await conn.execute("SELECT 1")
        
        connection_time = time.time() - start_time
        
        # Get performance stats
        stats = db_manager.get_stats()
        
        return {
            "connected": True,
            "connection_time_ms": round(connection_time * 1000, 2),
            "pool_stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        connection_time = time.time() - start_time
        logger.error(f"Database connectivity check failed: {e}")
        
        return {
            "connected": False,
            "error": str(e),
            "connection_time_ms": round(connection_time * 1000, 2),
            "timestamp": time.time()
        }


async def perform_db_diagnostics() -> Dict[str, Any]:
    """Perform comprehensive database diagnostics"""
    diagnostics = {
        "timestamp": time.time(),
        "connectivity": await check_db_connectivity(),
        "health": await get_db_health_details(),
    }
    
    # Add database version check
    try:
        async with db_manager.connection() as conn:
            version_result = await conn.fetchrow("SELECT version()")
            diagnostics["database_version"] = version_result["version"] if version_result else "Unknown"
    except Exception as e:
        diagnostics["database_version"] = f"Error: {e}"
    
    # Check table existence
    try:
        async with db_manager.connection() as conn:
            tables_result = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            diagnostics["tables"] = [row["table_name"] for row in tables_result]
            diagnostics["table_count"] = len(diagnostics["tables"])
    except Exception as e:
        diagnostics["tables"] = []
        diagnostics["table_count"] = 0
        diagnostics["table_error"] = str(e)
    
    return diagnostics