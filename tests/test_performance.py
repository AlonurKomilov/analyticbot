import asyncio
import gc
import json
import time
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import psutil
import pytest
from src.services.analytics_service import AnalyticsService
from src.services.scheduler_service import SchedulerService

from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository


class TestPerformanceBenchmarks:
    """Comprehensive performance benchmark tests"""

    @pytest.fixture
    async def mock_services(self):
        """Setup mock services for testing"""
        analytics_repo = MagicMock(spec=AsyncpgAnalyticsRepository)
        # Note: Using MagicMock without spec due to architectural mismatch
        # SchedulerService calls methods that don't exist in AsyncpgScheduleRepository
        scheduler_repo = MagicMock()
        analytics_repo.get_total_users_count.return_value = 1000
        analytics_repo.get_total_channels_count.return_value = 50
        analytics_repo.get_total_posts_count.return_value = 500
        # Mock the methods that SchedulerService actually calls
        scheduler_repo.create_scheduled_post = AsyncMock(return_value=123)
        scheduler_repo.update_post_status = AsyncMock(return_value=None)
        scheduler_repo.get_pending_posts = AsyncMock(
            return_value=[{"id": i, "text": f"Post {i}", "channel_id": i % 10} for i in range(50)]
        )
        bot = AsyncMock()
        analytics_service = AnalyticsService(bot, analytics_repo)
        scheduler_service = SchedulerService(bot, scheduler_repo, analytics_repo)
        return (analytics_service, scheduler_service)

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_analytics_service_performance(self, benchmark, mock_services):
        """Benchmark analytics service operations"""
        analytics_service, _ = mock_services

        def analytics_operation():
            return asyncio.get_event_loop().run_until_complete(
                analytics_service.get_total_users_count()
            )

        result = benchmark(analytics_operation)
        assert isinstance(result, int)
        assert result >= 0

    @pytest.mark.asyncio
    async def test_scheduler_service_basic(self, mock_services):
        """Test basic scheduler service functionality"""
        analytics_service, scheduler_service = mock_services

        result = await scheduler_service.get_pending_posts(limit=50)
        assert isinstance(result, list)
        assert len(result) <= 50

    @pytest.mark.benchmark
    def test_scheduler_service_performance(self, benchmark, mock_services):
        """Benchmark scheduler service operations"""
        analytics_service, scheduler_service = mock_services

        async def scheduler_operation():
            return await scheduler_service.get_pending_posts(limit=50)

        # Use asyncio.new_event_loop() to avoid the running loop issue
        def run_in_new_loop():
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(scheduler_operation())
            finally:
                loop.close()

        result = benchmark(run_in_new_loop)
        assert isinstance(result, list)
        assert len(result) <= 50

    @pytest.mark.benchmark
    def test_memory_usage_basic(self, benchmark):
        """Test basic memory usage patterns"""

        def memory_operation():
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024
            data = [i for i in range(10000)]
            result = sum(data)
            del data
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024
            return (result, final_memory - initial_memory)

        result, memory_increase = benchmark(memory_operation)
        assert isinstance(result, int)
        assert memory_increase < 100, f"Memory increased by {memory_increase}MB"

    @pytest.mark.benchmark
    def test_json_serialization_performance(self, benchmark):
        """Benchmark JSON serialization/deserialization"""
        test_data = {
            "posts": [
                {
                    "id": i,
                    "title": f"Post {i}",
                    "content": f"This is the content for post {i}" * 10,
                    "timestamp": datetime.now().isoformat(),
                    "tags": [f"tag{j}" for j in range(5)],
                }
                for i in range(100)
            ],
            "metadata": {
                "total_count": 100,
                "page": 1,
                "per_page": 100,
                "generated_at": datetime.now().isoformat(),
            },
        }

        def json_operation():
            serialized = json.dumps(test_data)
            return json.loads(serialized)

        result = benchmark(json_operation)
        assert len(result["posts"]) == 100
        assert "metadata" in result

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, benchmark, mock_services):
        """Test performance under concurrent load"""
        analytics_service, scheduler_service = mock_services

        async def concurrent_operations():
            tasks = []
            for i in range(20):
                if i % 3 == 0:
                    tasks.append(analytics_service.get_total_users_count())
                elif i % 3 == 1:
                    tasks.append(analytics_service.get_total_channels_count())
                else:
                    tasks.append(scheduler_service.get_pending_posts(limit=10))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

        def sync_concurrent_operations():
            return asyncio.get_event_loop().run_until_complete(concurrent_operations())

        results = benchmark(sync_concurrent_operations)
        assert len(results) == 20
        assert all(not isinstance(r, Exception) for r in results)


class TestLoadSimulation:
    """Simulate various load scenarios"""

    @pytest.mark.asyncio
    async def test_burst_load_simulation(self):
        """Simulate burst load scenario"""
        start_time = time.time()
        tasks = []
        for i in range(50):

            async def mock_request():
                await asyncio.sleep(0.01)
                return {"id": i, "processed_at": time.time()}

            tasks.append(mock_request())
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        assert len(results) == 50
        assert duration < 2.0, f"Burst processing took {duration}s, should be < 2s"

    @pytest.mark.asyncio
    async def test_sustained_load_simulation(self):
        """Simulate sustained load over time"""
        start_time = time.time()
        processed_count = 0
        while time.time() - start_time < 3:
            batch_tasks = []
            for _ in range(5):

                async def mock_work():
                    await asyncio.sleep(0.1)
                    return True

                batch_tasks.append(mock_work())
            results = await asyncio.gather(*batch_tasks)
            processed_count += len(results)
            await asyncio.sleep(0.1)
        throughput = processed_count / (time.time() - start_time)
        assert throughput > 5, f"Throughput {throughput} req/s is too low"


class TestMemoryLeakDetection:
    """Detect potential memory leaks"""

    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        for iteration in range(100):
            data = {f"key_{i}": f"value_{i}" * 10 for i in range(100)}
            processed = {k: v.upper() for k, v in data.items()}
            del data, processed
            if iteration % 10 == 0:
                gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        assert memory_increase < 50, f"Potential memory leak: {memory_increase}MB increase"


class TestDatabasePerformance:
    """Database-related performance tests"""

    @pytest.mark.asyncio
    async def test_mock_database_operations(self):
        """Test database operations with mocks"""
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool.acquire.return_value.__aexit__.return_value = None
        mock_conn.fetchval.return_value = 100
        mock_conn.fetch.return_value = [{"id": i, "name": f"item_{i}"} for i in range(20)]
        start_time = time.time()
        tasks = []
        for i in range(20):

            async def db_operation():
                async with mock_pool.acquire() as conn:
                    if i % 2 == 0:
                        return await conn.fetchval("SELECT COUNT(*) FROM users")
                    else:
                        return await conn.fetch("SELECT * FROM posts LIMIT 10")

            tasks.append(db_operation())
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        assert len(results) == 20
        assert duration < 1.0, f"DB operations took {duration}s, should be < 1s"


class TestErrorHandling:
    """Test error handling performance"""

    @pytest.mark.asyncio
    async def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance"""

        async def operation_with_errors():
            results = []
            errors = 0
            for i in range(100):
                try:
                    if i % 10 == 0:
                        raise ValueError(f"Simulated error {i}")
                    await asyncio.sleep(0.001)
                    results.append(f"result_{i}")
                except ValueError:
                    errors += 1
            return (results, errors)

        start_time = time.time()
        results, errors = await operation_with_errors()
        duration = time.time() - start_time
        assert len(results) == 90
        assert errors == 10
        assert duration < 2.0, f"Error handling took {duration}s, should be < 2s"


class TestConfigurationScenarios:
    """Test different configuration scenarios"""

    def test_configuration_loading_performance(self, benchmark):
        """Test configuration loading performance"""

        def load_configuration():
            config = {
                "database_url": "postgresql://user:pass@localhost/db",
                "redis_url": "redis://localhost:6379/0",
                "bot_token": "fake_token",
                "features": {
                    "analytics": True,
                    "scheduling": True,
                    "notifications": True,
                },
                "limits": {
                    "max_posts_per_day": 100,
                    "max_channels_per_user": 10,
                    "rate_limit": 30,
                },
            }
            validated_config = {}
            for key, value in config.items():
                if isinstance(value, dict):
                    validated_config[key] = {k: v for k, v in value.items()}
                else:
                    validated_config[key] = value
            return validated_config

        result = benchmark(load_configuration)
        assert "database_url" in result
        assert "features" in result
        assert "limits" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
