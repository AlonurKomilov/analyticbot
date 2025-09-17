"""
Unit tests for Analytics Router functions.

Direct testing of router functions using centralized mock factory.
This achieves coverage without complex import dependencies.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import centralized mock factory
from tests.factories.mock_factory import MockFactory, TestDataFactory


class TestAnalyticsRouterFunctions:
    """Test individual functions from analytics router using mock factory."""

    @pytest.fixture(autouse=True)
    def setup_dependencies(self):
        """Setup test dependencies using centralized factory."""
        # Create consistent mocks using factory
        self.analytics_service = MockFactory.create_analytics_service()
        self.channel_repository = MockFactory.create_channel_repository()
        self.db_pool = MockFactory.create_db_pool()
        self.config = MockFactory.create_config_mock()
        
        # Create test data
        self.sample_analytics = TestDataFactory.create_analytics_data()
        self.sample_channels = [TestDataFactory.create_channel_data()]
        
        # Setup patches with factory-created mocks
        self.patches = [
            patch('apps.bot.analytics.AdvancedDataProcessor'),
            patch('apps.bot.analytics.AIInsightsGenerator'),
            patch('apps.bot.analytics.DashboardFactory'), 
            patch('apps.bot.analytics.PredictiveAnalyticsEngine'),
            patch('apps.bot.container.container'),
            patch('apps.bot.services.analytics_service.AnalyticsService', return_value=self.analytics_service),
            patch('infra.db.repositories.analytics_repository.AsyncpgAnalyticsRepository'),
            patch('infra.db.repositories.channel_repository.AsyncpgChannelRepository', return_value=self.channel_repository),
            patch('apps.bot.handlers.alerts'),
            patch('apps.bot.handlers.analytics_v2'),
            patch('apps.bot.handlers.exports'),
            patch('infra.db.repositories.alert_repository.AsyncpgAlertSubscriptionRepository'),
        ]
        
        for p in self.patches:
            p.start()
        
        yield
        
        for p in self.patches:
            p.stop()

    @pytest.mark.asyncio
    async def test_analytics_health_check(self):
        """Test the analytics health check function."""
        # Import after mocking
        from apps.api.routers.analytics_router import analytics_health_check
        
        result = await analytics_health_check()
        
        assert result["status"] == "healthy"
        assert result["service"] == "analytics"
        assert result["version"] == "2.0.0"
        assert "timestamp" in result
        assert len(result["modules"]) == 5
        assert "data_processor" in result["modules"]

    @pytest.mark.asyncio
    async def test_analytics_status_success(self):
        """Test analytics status with successful import."""
        with patch('apps.bot.analytics.__all__', ['DataProcessor', 'AIInsights']):
            from apps.api.routers.analytics_router import analytics_status
            
            result = await analytics_status()
            
            assert result["module"] == "bot.analytics"
            assert result["version"] == "2.0.0"
            assert result["components"] == 2
            assert result["status"] == "operational"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_analytics_status_failure(self):
        """Test analytics status with import failure."""
        from fastapi import HTTPException
        
        with patch('apps.bot.analytics.__all__', side_effect=ImportError("Module not found")):
            from apps.api.routers.analytics_router import analytics_status
            
            with pytest.raises(HTTPException) as exc_info:
                await analytics_status()
            
            assert exc_info.value.status_code == 500
            assert "Failed to get analytics status" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_channels(self):
        """Test get channels function."""
        from apps.api.routers.analytics_router import get_channels
        
        # Mock channel repository
        mock_repo = AsyncMock()
        mock_channel = MagicMock()
        mock_channel.id = 1
        mock_channel.name = "Test Channel"
        mock_channel.telegram_id = 12345
        mock_channel.description = "Test Description"
        mock_channel.created_at = datetime(2024, 1, 1)
        mock_channel.is_active = True
        
        mock_repo.get_channels.return_value = [mock_channel]
        
        result = await get_channels(skip=0, limit=100, channel_repo=mock_repo)
        
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Test Channel"
        assert result[0].telegram_id == 12345
        mock_repo.get_channels.assert_called_once_with(skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_create_channel(self):
        """Test create channel function."""
        from apps.api.routers.analytics_router import create_channel, ChannelCreate
        
        # Mock channel repository
        mock_repo = AsyncMock()
        mock_channel = MagicMock()
        mock_channel.id = 1
        mock_channel.name = "New Channel"
        mock_channel.telegram_id = 67890
        mock_channel.description = "New Description"
        mock_channel.created_at = datetime(2024, 1, 1)
        mock_channel.is_active = True
        
        mock_repo.create_channel.return_value = mock_channel
        
        channel_data = ChannelCreate(
            name="New Channel",
            telegram_id=67890,
            description="New Description"
        )
        
        result = await create_channel(channel=channel_data, channel_repo=mock_repo)
        
        assert result.id == 1
        assert result.name == "New Channel"
        assert result.telegram_id == 67890
        mock_repo.create_channel.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_channel_by_id_success(self):
        """Test get channel by ID when channel exists."""
        from apps.api.routers.analytics_router import get_channel_by_id
        
        mock_repo = AsyncMock()
        mock_channel = MagicMock()
        mock_channel.id = 1
        mock_channel.name = "Test Channel"
        mock_channel.telegram_id = 12345
        mock_channel.description = "Test Description"
        mock_channel.created_at = datetime(2024, 1, 1)
        mock_channel.is_active = True
        
        mock_repo.get_channel_by_id.return_value = mock_channel
        
        result = await get_channel_by_id(channel_id=1, channel_repo=mock_repo)
        
        assert result.id == 1
        assert result.name == "Test Channel"
        mock_repo.get_channel_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_channel_by_id_not_found(self):
        """Test get channel by ID when channel doesn't exist."""
        from fastapi import HTTPException
        from apps.api.routers.analytics_router import get_channel_by_id
        
        mock_repo = AsyncMock()
        mock_repo.get_channel_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_channel_by_id(channel_id=999, channel_repo=mock_repo)
        
        assert exc_info.value.status_code == 404
        assert "Channel not found" in str(exc_info.value.detail)

    def test_demo_post_dynamics(self):
        """Test demo post dynamics function."""
        from apps.api.routers.analytics_router import demo_post_dynamics
        
        result = demo_post_dynamics()
        
        assert isinstance(result, list)
        assert len(result) == 7  # One week of data
        
        for item in result:
            assert "date" in item
            assert "views" in item
            assert "engagement_rate" in item
            assert isinstance(item["views"], int)
            assert item["views"] >= 100
            assert isinstance(item["engagement_rate"], float)
            assert 0 <= item["engagement_rate"] <= 1

    def test_demo_top_posts(self):
        """Test demo top posts function."""
        from apps.api.routers.analytics_router import demo_top_posts
        
        result = demo_top_posts()
        
        assert isinstance(result, list)
        assert len(result) == 5  # Top 5 posts
        
        for item in result:
            assert "title" in item
            assert "views" in item
            assert "engagement_rate" in item
            assert "date" in item
            assert isinstance(item["views"], int)
            assert item["views"] >= 1000

    def test_demo_best_times(self):
        """Test demo best times function."""
        from apps.api.routers.analytics_router import demo_best_times
        
        result = demo_best_times()
        
        assert isinstance(result, list)
        assert len(result) == 3  # Best 3 time slots
        
        for item in result:
            assert "hour" in item
            assert "engagement_score" in item
            assert "confidence" in item
            assert 0 <= item["hour"] <= 23
            assert 0 <= item["engagement_score"] <= 1
            assert 0 <= item["confidence"] <= 1

    def test_demo_ai_recommendations(self):
        """Test demo AI recommendations function."""
        from apps.api.routers.analytics_router import demo_ai_recommendations
        
        result = demo_ai_recommendations()
        
        assert isinstance(result, list)
        assert len(result) == 3  # 3 recommendations
        
        for item in result:
            assert "recommendation" in item
            assert "impact" in item
            assert "priority" in item
            assert item["priority"] in ["high", "medium", "low"]
            assert isinstance(item["impact"], str)
            assert len(item["recommendation"]) > 0

    @pytest.mark.asyncio
    async def test_get_metrics(self):
        """Test get metrics function."""
        from apps.api.routers.analytics_router import get_metrics
        
        mock_repo = AsyncMock()
        mock_metrics = [
            {
                "channel_id": 1,
                "date": "2024-01-01",
                "views": 1000,
                "subscribers": 500,
                "engagement_rate": 0.1
            }
        ]
        mock_repo.get_metrics.return_value = mock_metrics
        
        result = await get_metrics(analytics_repo=mock_repo)
        
        assert len(result) == 1
        assert result[0]["channel_id"] == 1
        assert result[0]["views"] == 1000
        mock_repo.get_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_channel_metrics(self):
        """Test get channel-specific metrics function."""
        from apps.api.routers.analytics_router import get_channel_metrics
        
        mock_repo = AsyncMock()
        mock_metrics = [
            {
                "channel_id": 1,
                "date": "2024-01-01", 
                "views": 2000,
                "subscribers": 750,
                "engagement_rate": 0.15
            }
        ]
        mock_repo.get_channel_metrics.return_value = mock_metrics
        
        result = await get_channel_metrics(channel_id=1, analytics_repo=mock_repo)
        
        assert len(result) == 1
        assert result[0]["channel_id"] == 1
        assert result[0]["views"] == 2000
        mock_repo.get_channel_metrics.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_analyze_data(self):
        """Test analyze data function."""
        from apps.api.routers.analytics_router import analyze_data
        
        mock_service = AsyncMock()
        mock_result = {
            "status": "completed",
            "processed_records": 1000,
            "insights": ["High engagement on weekends", "Peak activity at 9 PM"]
        }
        mock_service.analyze_data.return_value = mock_result
        
        request_data = {
            "channel_id": 1,
            "analysis_type": "engagement",
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
        }
        
        result = await analyze_data(request=request_data, analytics_service=mock_service)
        
        assert result["status"] == "completed"
        assert result["processed_records"] == 1000
        assert len(result["insights"]) == 2
        mock_service.analyze_data.assert_called_once_with(request_data)

    @pytest.mark.asyncio
    async def test_forecast_predictions(self):
        """Test forecast predictions function."""
        from apps.api.routers.analytics_router import forecast_predictions
        
        mock_service = AsyncMock()
        mock_forecast = {
            "forecast_period": "30_days",
            "predicted_growth": 15.5,
            "confidence": 0.85,
            "predictions": [
                {"date": "2024-02-01", "value": 1500},
                {"date": "2024-02-02", "value": 1520}
            ]
        }
        mock_service.generate_forecast.return_value = mock_forecast
        
        request_data = {
            "channel_id": 1,
            "metric": "subscribers",
            "forecast_days": 30
        }
        
        result = await forecast_predictions(request=request_data, analytics_service=mock_service)
        
        assert result["forecast_period"] == "30_days"
        assert result["predicted_growth"] == 15.5
        assert result["confidence"] == 0.85
        assert len(result["predictions"]) == 2
        mock_service.generate_forecast.assert_called_once_with(request_data)

    @pytest.mark.asyncio
    async def test_get_insights(self):
        """Test get insights function."""
        from apps.api.routers.analytics_router import get_insights
        
        mock_service = AsyncMock()
        mock_insights = {
            "channel_id": 1,
            "insights": [
                {"type": "growth", "value": "20% increase in subscribers"},
                {"type": "engagement", "value": "High interaction rate on videos"},
                {"type": "content", "value": "Educational content performs best"}
            ],
            "generated_at": datetime.now().isoformat()
        }
        mock_service.get_insights.return_value = mock_insights
        
        result = await get_insights(channel_id=1, analytics_service=mock_service)
        
        assert result["channel_id"] == 1
        assert len(result["insights"]) == 3
        assert result["insights"][0]["type"] == "growth"
        mock_service.get_insights.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_dashboard(self):
        """Test get dashboard function."""
        from apps.api.routers.analytics_router import get_dashboard
        
        mock_service = AsyncMock()
        mock_dashboard = {
            "channel_id": 1,
            "summary": {
                "total_views": 50000,
                "total_subscribers": 2500,
                "engagement_rate": 0.125
            },
            "charts": [
                {"type": "growth_chart", "data": [1, 2, 3]},
                {"type": "engagement_chart", "data": [0.1, 0.12, 0.15]}
            ],
            "last_updated": datetime.now().isoformat()
        }
        mock_service.get_dashboard_data.return_value = mock_dashboard
        
        result = await get_dashboard(channel_id=1, analytics_service=mock_service)
        
        assert result["channel_id"] == 1
        assert result["summary"]["total_views"] == 50000
        assert len(result["charts"]) == 2
        mock_service.get_dashboard_data.assert_called_once_with(1)

    @pytest.mark.asyncio 
    async def test_refresh_channel(self):
        """Test refresh channel function."""
        from apps.api.routers.analytics_router import refresh_channel
        
        mock_service = AsyncMock()
        mock_refresh_result = {
            "status": "success",
            "message": "Channel data refreshed successfully", 
            "records_updated": 150,
            "last_refresh": datetime.now().isoformat()
        }
        mock_service.refresh_channel_data.return_value = mock_refresh_result
        
        result = await refresh_channel(channel_id=1, analytics_service=mock_service)
        
        assert result["status"] == "success"
        assert result["records_updated"] == 150
        mock_service.refresh_channel_data.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_channel_summary(self):
        """Test get channel summary function."""  
        from apps.api.routers.analytics_router import get_channel_summary
        
        mock_service = AsyncMock()
        mock_summary = {
            "channel_id": 1,
            "period": "last_30_days",
            "total_views": 75000,
            "total_subscribers": 3200,
            "avg_engagement_rate": 0.135,
            "top_post": {
                "title": "Best Performing Post",
                "views": 8500,
                "engagement_rate": 0.18
            },
            "growth_metrics": {
                "views_growth": 12.5,
                "subscriber_growth": 8.3
            }
        }
        mock_service.get_channel_summary.return_value = mock_summary
        
        result = await get_channel_summary(channel_id=1, analytics_service=mock_service)
        
        assert result["channel_id"] == 1
        assert result["total_views"] == 75000
        assert result["top_post"]["title"] == "Best Performing Post"
        assert result["growth_metrics"]["views_growth"] == 12.5
        mock_service.get_channel_summary.assert_called_once_with(1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
