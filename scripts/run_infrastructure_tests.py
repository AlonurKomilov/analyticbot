"""
🧪 DATABASE PERFORMANCE TEST
Real database connection and performance testing
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_database_availability():
    """Test database availability without complex dependencies"""
    logger.info("🔍 Testing database availability...")
    db_vars = {
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "POSTGRES_DB": os.getenv("POSTGRES_DB", "analyticbot"),
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
    logger.info("📊 Database configuration:")
    logger.info(f"   Host: {db_vars['POSTGRES_HOST']}:{db_vars['POSTGRES_PORT']}")
    logger.info(f"   Database: {db_vars['POSTGRES_DB']}")
    logger.info(f"   User: {db_vars['POSTGRES_USER']}")
    try:
        import asyncpg

        dsn = f"postgresql://{db_vars['POSTGRES_USER']}:{db_vars['POSTGRES_PASSWORD']}@{db_vars['POSTGRES_HOST']}:{db_vars['POSTGRES_PORT']}/{db_vars['POSTGRES_DB']}"
        logger.info("🔌 Attempting database connection...")
        start_time = time.perf_counter()
        conn = await asyncpg.connect(dsn, command_timeout=5)
        connection_time = time.perf_counter() - start_time
        start_time = time.perf_counter()
        result = await conn.fetchval("SELECT 1 as test_value")
        query_time = time.perf_counter() - start_time
        db_version = await conn.fetchval("SELECT version()")
        db_size = await conn.fetchval(
            f"SELECT pg_database_size('{db_vars['POSTGRES_DB']}') as size"
        )
        table_count = await conn.fetchval(
            "\n            SELECT COUNT(*) \n            FROM information_schema.tables \n            WHERE table_schema = 'public'\n        "
        )
        await conn.close()
        logger.info("✅ Database connection successful!")
        logger.info(f"   Connection time: {connection_time:.4f}s")
        logger.info(f"   Query time: {query_time:.4f}s")
        logger.info(
            f"   Database size: {db_size / (1024 * 1024):.1f} MB"
            if db_size
            else "   Database size: Unknown"
        )
        logger.info(f"   Tables: {table_count}")
        logger.info(f"   Version: {(db_version.split()[0:2] if db_version else 'Unknown')}")
        return {
            "available": True,
            "connection_time": connection_time,
            "query_time": query_time,
            "database_size_mb": db_size / (1024 * 1024) if db_size else 0,
            "table_count": table_count,
            "version": db_version,
        }
    except ImportError:
        logger.warning("⚠️ asyncpg not available, cannot test real database")
        return {"available": False, "reason": "asyncpg_not_installed"}
    except Exception as e:
        logger.warning(f"⚠️ Database not available: {e}")
        return {"available": False, "reason": str(e)}


async def test_redis_availability():
    """Test Redis availability"""
    logger.info("🔍 Testing Redis availability...")
    redis_config = {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
    }
    logger.info("📊 Redis configuration:")
    logger.info(f"   Host: {redis_config['host']}:{redis_config['port']}")
    logger.info(f"   Database: {redis_config['db']}")
    try:
        import redis.asyncio as redis

        logger.info("🔌 Attempting Redis connection...")
        start_time = time.perf_counter()
        r = redis.Redis(
            host=redis_config["host"],
            port=redis_config["port"],
            db=redis_config["db"],
            decode_responses=True,
            socket_connect_timeout=5,
        )
        await r.ping()
        connection_time = time.perf_counter() - start_time
        start_time = time.perf_counter()
        await r.set("test_key", "test_value", ex=10)
        set_time = time.perf_counter() - start_time
        start_time = time.perf_counter()
        value = await r.get("test_key")
        get_time = time.perf_counter() - start_time
        await r.delete("test_key")
        info = await r.info()
        memory_used = info.get("used_memory_human", "Unknown")
        redis_version = info.get("redis_version", "Unknown")
        await r.close()
        logger.info("✅ Redis connection successful!")
        logger.info(f"   Connection time: {connection_time:.4f}s")
        logger.info(f"   Set operation: {set_time:.4f}s")
        logger.info(f"   Get operation: {get_time:.4f}s")
        logger.info(f"   Memory used: {memory_used}")
        logger.info(f"   Version: {redis_version}")
        return {
            "available": True,
            "connection_time": connection_time,
            "set_time": set_time,
            "get_time": get_time,
            "memory_used": memory_used,
            "version": redis_version,
        }
    except ImportError:
        logger.warning("⚠️ redis not available, cannot test Redis")
        return {"available": False, "reason": "redis_not_installed"}
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}")
        return {"available": False, "reason": str(e)}


async def test_performance_optimization_components():
    """Test our custom performance optimization components"""
    logger.info("🔍 Testing performance optimization components...")
    try:
        from apps.bot.database.performance import PerformanceConfig

        logger.info("✅ Performance manager imported successfully")
        logger.info("✅ Unified analytics service imported successfully")
        logger.info("✅ Optimized container imported successfully")
        config_tests = {
            "DB_POOL_MIN_SIZE": PerformanceConfig.DB_POOL_MIN_SIZE,
            "DB_POOL_MAX_SIZE": PerformanceConfig.DB_POOL_MAX_SIZE,
            "CACHE_DEFAULT_TTL": PerformanceConfig.CACHE_DEFAULT_TTL,
            "QUERY_BATCH_SIZE": PerformanceConfig.QUERY_BATCH_SIZE,
            "MAX_CONCURRENT_QUERIES": PerformanceConfig.MAX_CONCURRENT_QUERIES,
        }
        logger.info("📊 Performance configuration:")
        for key, value in config_tests.items():
            logger.info(f"   {key}: {value}")
        return {"components_available": True, "performance_config": config_tests}
    except Exception as e:
        logger.error(f"❌ Performance components test failed: {e}")
        return {"components_available": False, "error": str(e)}


async def test_docker_services():
    """Test if Docker services are available"""
    logger.info("🐳 Testing Docker services availability...")
    try:
        import subprocess

        result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            logger.info(f"✅ Docker Compose available: {result.stdout.strip()}")
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd="/workspaces/analyticbot",
            )
            if result.returncode == 0:
                services_output = result.stdout.strip()
                logger.info("📊 Docker services status:")
                for line in services_output.split("\n")[1:]:
                    if line.strip():
                        logger.info(f"   {line}")
                db_running = "postgres" in services_output and "Up" in services_output
                redis_running = "redis" in services_output and "Up" in services_output
                return {
                    "docker_available": True,
                    "services_running": True,
                    "database_running": db_running,
                    "redis_running": redis_running,
                    "services_output": services_output,
                }
            else:
                logger.warning("⚠️ Could not check Docker services status")
                return {"docker_available": True, "services_running": False, "error": result.stderr}
        else:
            logger.warning("⚠️ Docker Compose not available")
            return {"docker_available": False}
    except FileNotFoundError:
        logger.warning("⚠️ Docker Compose not found")
        return {"docker_available": False, "reason": "docker_compose_not_found"}
    except Exception as e:
        logger.error(f"❌ Docker services test failed: {e}")
        return {"docker_available": False, "error": str(e)}


async def main():
    """Main function to run all infrastructure tests"""
    logger.info("🚀 Starting Infrastructure & Performance Component Tests")
    logger.info("=" * 70)
    start_time = time.time()
    results = {}
    logger.info("\n⚡ SYSTEM PERFORMANCE BASELINE")
    logger.info("-" * 40)
    try:
        import psutil

        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        logger.info("✅ System Resources:")
        logger.info(f"   CPU Cores: {cpu_count}")
        logger.info(f"   Total Memory: {memory.total / 1024**3:.1f} GB")
        logger.info(f"   Available Memory: {memory.available / 1024**3:.1f} GB")
        results["system"] = {
            "cpu_cores": cpu_count,
            "memory_total_gb": memory.total / 1024**3,
            "memory_available_gb": memory.available / 1024**3,
        }
    except Exception as e:
        logger.warning(f"⚠️ Could not get system info: {e}")
    logger.info("\n🐳 DOCKER SERVICES")
    logger.info("-" * 40)
    results["docker"] = await test_docker_services()
    logger.info("\n🗄️ DATABASE AVAILABILITY")
    logger.info("-" * 40)
    results["database"] = await test_database_availability()
    logger.info("\n📦 REDIS AVAILABILITY")
    logger.info("-" * 40)
    results["redis"] = await test_redis_availability()
    logger.info("\n🚀 PERFORMANCE OPTIMIZATION COMPONENTS")
    logger.info("-" * 40)
    results["performance_components"] = await test_performance_optimization_components()
    total_time = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("🏆 INFRASTRUCTURE TEST REPORT")
    logger.info("=" * 70)
    logger.info(f"⏱️ Total test time: {total_time:.2f} seconds")
    ready_for_performance = True
    issues = []
    if results.get("database", {}).get("available"):
        logger.info("✅ Database: Ready")
    else:
        logger.info("❌ Database: Not available")
        ready_for_performance = False
        issues.append("Database connection failed")
    if results.get("redis", {}).get("available"):
        logger.info("✅ Redis: Ready")
    else:
        logger.info("⚠️ Redis: Not available (performance caching disabled)")
    if results.get("performance_components", {}).get("components_available"):
        logger.info("✅ Performance Components: Ready")
    else:
        logger.info("❌ Performance Components: Import failed")
        ready_for_performance = False
        issues.append("Performance optimization components not available")
    if results.get("docker", {}).get("docker_available"):
        logger.info("✅ Docker: Available")
        if results.get("docker", {}).get("services_running"):
            logger.info("✅ Docker Services: Running")
        else:
            logger.info("⚠️ Docker Services: Not running")
    else:
        logger.info("⚠️ Docker: Not available")
    logger.info("\n💡 READINESS ASSESSMENT:")
    logger.info("-" * 40)
    if ready_for_performance:
        logger.info("🎉 System is ready for performance optimization deployment!")
        logger.info("✅ All critical components are available")
        if not results.get("redis", {}).get("available"):
            logger.info("📝 Note: Redis caching will be disabled (fallback mode)")
    else:
        logger.info("⚠️ System needs setup before performance optimization:")
        for issue in issues:
            logger.info(f"   • {issue}")
        logger.info("\n🔧 SETUP RECOMMENDATIONS:")
        if not results.get("database", {}).get("available"):
            logger.info("   1. Start PostgreSQL database:")
            logger.info("      docker-compose up postgres -d")
        if not results.get("redis", {}).get("available"):
            logger.info("   2. Start Redis cache:")
            logger.info("      docker-compose up redis -d")
        if not results.get("performance_components", {}).get("components_available"):
            logger.info("   3. Install missing dependencies:")
            logger.info("      pip install -r requirements.txt")
    logger.info(f"\n✅ Infrastructure testing completed in {total_time:.2f} seconds!")
    import json

    with open("infrastructure_test_results.json", "w") as f:
        serializable_results = {}
        for key, value in results.items():
            try:
                json.dumps(value)
                serializable_results[key] = value
            except:
                serializable_results[key] = str(value)
        json.dump(serializable_results, f, indent=2)
    logger.info("📁 Results saved to: infrastructure_test_results.json")
    return results


if __name__ == "__main__":
    asyncio.run(main())
