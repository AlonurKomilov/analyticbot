"""
Database Performance Monitoring Utility
Tracks and analyzes database query performance.
"""
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

logger = logging.getLogger(__name__)


class DatabasePerformanceMonitor:
    """Monitor database query performance."""
    
    @staticmethod
    @asynccontextmanager
    async def monitor_query(query_name: str, query: Optional[str] = None):
        """
        Context manager to monitor database query performance.
        
        Usage:
            async with DatabasePerformanceMonitor.monitor_query("get_user", "SELECT..."):
                result = await conn.fetch(query)
        """
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            try:
                from apps.api.middleware.performance_monitoring import performance_metrics
                if query:
                    performance_metrics.record_db_query(query, duration)
            except Exception as e:
                logger.warning(f"Failed to record DB metrics: {e}")
            
            # Log slow queries
            if duration > 0.1:  # >100ms
                logger.warning(
                    f"Slow query [{query_name}]: {duration:.3f}s - "
                    f"{query[:200] if query else 'N/A'}"
                )
            elif duration > 0.05:  # >50ms
                logger.info(
                    f"Moderate query [{query_name}]: {duration:.3f}s"
                )


# Convenience function
def monitor_query(query_name: str, query: Optional[str] = None):
    """Shorthand for DatabasePerformanceMonitor.monitor_query"""
    return DatabasePerformanceMonitor.monitor_query(query_name, query)
