"""
🚀 PERFORMANCE MONITORING API
Real-time performance metrics and monitoring endpoints
"""

import asyncio
import time
from datetime import datetime
from typing import Any

import psutil
from bot.database.db import db_manager
from bot.database.performance import performance_manager
from fastapi import FastAPI, HTTPException

app = FastAPI(title="AnalyticBot Performance Monitor", version="1.5.0")


class PerformanceMonitor:
    """🔍 System performance monitoring"""

    @staticmethod
    async def get_system_metrics() -> dict[str, Any]:
        """Get system-level performance metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "cores": psutil.cpu_count(),
                "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "free": psutil.disk_usage("/").free,
                "percent": psutil.disk_usage("/").percent,
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
            },
        }

    @staticmethod
    async def get_database_metrics() -> dict[str, Any]:
        """Get database performance metrics"""
        try:
            stats = await db_manager.get_performance_stats()

            # Add database-specific metrics
            if db_manager.pool:
                async with db_manager.pool.acquire() as conn:
                    # Query performance stats
                    slow_queries = await conn.fetch("""
                        SELECT query, calls, mean_time, total_time 
                        FROM pg_stat_statements 
                        WHERE mean_time > 100 
                        ORDER BY mean_time DESC 
                        LIMIT 10
                    """)

                    # Connection stats
                    connections = await conn.fetchrow("""
                        SELECT 
                            count(*) as total,
                            count(*) FILTER (WHERE state = 'active') as active,
                            count(*) FILTER (WHERE state = 'idle') as idle
                        FROM pg_stat_activity
                    """)

                    stats.update(
                        {
                            "slow_queries": [dict(row) for row in slow_queries],
                            "connections": dict(connections) if connections else {},
                        }
                    )

            return stats

        except Exception as e:
            return {"error": str(e), "status": "unavailable"}

    @staticmethod
    async def get_cache_metrics() -> dict[str, Any]:
        """Get cache performance metrics"""
        try:
            if performance_manager.cache._is_connected:
                redis_info = await performance_manager.cache._redis.info()

                return {
                    "connected": True,
                    "memory_used": redis_info.get("used_memory", 0),
                    "memory_human": redis_info.get("used_memory_human", "0B"),
                    "memory_peak": redis_info.get("used_memory_peak", 0),
                    "hits": redis_info.get("keyspace_hits", 0),
                    "misses": redis_info.get("keyspace_misses", 0),
                    "hit_rate": redis_info.get("keyspace_hits", 0)
                    / (redis_info.get("keyspace_hits", 0) + redis_info.get("keyspace_misses", 1))
                    * 100,
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "total_commands": redis_info.get("total_commands_processed", 0),
                    "uptime": redis_info.get("uptime_in_seconds", 0),
                }
            else:
                return {"connected": False, "status": "disconnected"}

        except Exception as e:
            return {"connected": False, "error": str(e)}

    @staticmethod
    async def get_application_metrics() -> dict[str, Any]:
        """Get application-specific metrics"""
        try:
            # Get last analytics run stats
            analytics_stats = await performance_manager.cache.get("performance:analytics:last_run")

            return {
                "analytics": analytics_stats or {"status": "no_recent_runs"},
                "performance_mode": getattr(db_manager, "_performance_enabled", False),
                "uptime": time.time() - getattr(app.state, "start_time", time.time()),
            }

        except Exception as e:
            return {"error": str(e)}


monitor = PerformanceMonitor()


@app.on_event("startup")
async def startup_event():
    """Initialize performance monitoring"""
    app.state.start_time = time.time()


@app.get("/health")
async def health_check():
    """🩺 Basic health check endpoint"""
    try:
        db_healthy = await db_manager.health_check()
        cache_healthy = performance_manager.cache._is_connected

        status = "healthy" if db_healthy and cache_healthy else "degraded"

        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "cache": "healthy" if cache_healthy else "unhealthy",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/metrics/system")
async def get_system_metrics():
    """📊 System performance metrics"""
    try:
        return await monitor.get_system_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@app.get("/metrics/database")
async def get_database_metrics():
    """🗄️ Database performance metrics"""
    try:
        return await monitor.get_database_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database metrics: {str(e)}")


@app.get("/metrics/cache")
async def get_cache_metrics():
    """📦 Cache performance metrics"""
    try:
        return await monitor.get_cache_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache metrics: {str(e)}")


@app.get("/metrics/application")
async def get_application_metrics():
    """🚀 Application performance metrics"""
    try:
        return await monitor.get_application_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application metrics: {str(e)}")


@app.get("/metrics/all")
async def get_all_metrics():
    """📈 Complete performance dashboard"""
    try:
        results = await asyncio.gather(
            monitor.get_system_metrics(),
            monitor.get_database_metrics(),
            monitor.get_cache_metrics(),
            monitor.get_application_metrics(),
            return_exceptions=True,
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "system": results[0]
            if not isinstance(results[0], Exception)
            else {"error": str(results[0])},
            "database": results[1]
            if not isinstance(results[1], Exception)
            else {"error": str(results[1])},
            "cache": results[2]
            if not isinstance(results[2], Exception)
            else {"error": str(results[2])},
            "application": results[3]
            if not isinstance(results[3], Exception)
            else {"error": str(results[3])},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.post("/cache/flush")
async def flush_cache():
    """🗑️ Flush cache endpoint"""
    try:
        if performance_manager.cache._is_connected:
            await performance_manager.cache._redis.flushdb()
            return {"status": "success", "message": "Cache flushed successfully"}
        else:
            raise HTTPException(status_code=503, detail="Cache not connected")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flush cache: {str(e)}")


@app.post("/database/optimize")
async def optimize_database():
    """🛠️ Database optimization endpoint"""
    try:
        await db_manager.optimize_database()
        return {"status": "success", "message": "Database optimization completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database optimization failed: {str(e)}")


@app.get("/performance/report")
async def get_performance_report():
    """📋 Comprehensive performance report"""
    try:
        # Get all metrics
        all_metrics = await get_all_metrics()

        # Generate performance analysis
        analysis = {
            "overall_status": "good",
            "recommendations": [],
            "warnings": [],
            "critical_issues": [],
        }

        # Analyze system metrics
        if "system" in all_metrics and "error" not in all_metrics["system"]:
            system = all_metrics["system"]

            if system["cpu"]["usage_percent"] > 80:
                analysis["warnings"].append("High CPU usage detected")
                analysis["overall_status"] = "warning"

            if system["memory"]["percent"] > 85:
                analysis["warnings"].append("High memory usage detected")
                analysis["overall_status"] = "warning"

            if system["disk"]["percent"] > 90:
                analysis["critical_issues"].append("Disk space critically low")
                analysis["overall_status"] = "critical"

        # Analyze database metrics
        if "database" in all_metrics and "error" not in all_metrics["database"]:
            db = all_metrics["database"]

            if db.get("pool_used", 0) / max(db.get("pool_size", 1), 1) > 0.8:
                analysis["warnings"].append("Database connection pool usage high")

            if "slow_queries" in db and len(db["slow_queries"]) > 5:
                analysis["recommendations"].append("Consider optimizing slow queries")

        # Analyze cache metrics
        if "cache" in all_metrics and "error" not in all_metrics["cache"]:
            cache = all_metrics["cache"]

            if cache.get("connected", False):
                hit_rate = cache.get("hit_rate", 0)
                if hit_rate < 70:
                    analysis["recommendations"].append(f"Cache hit rate is low: {hit_rate:.1f}%")
            else:
                analysis["critical_issues"].append("Cache is not connected")
                analysis["overall_status"] = "critical"

        return {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "metrics": all_metrics,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate performance report: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
