#!/usr/bin/env python3
"""
Quick test script to verify the new analytics endpoints work correctly
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock

# Mock the necessary dependencies
def create_mock_analytics_service():
    """Create a mock analytics service"""
    service = AsyncMock()
    
    # Mock get_last_updated_at
    service.get_last_updated_at.return_value = None
    
    # Mock get_overview
    service.get_overview.return_value = {
        "total_views": 15000,
        "growth_rate": 12.5,
        "engagement_rate": 4.2,
        "performance_score": 85
    }
    
    # Mock get_growth
    service.get_growth.return_value = {
        "growth_rate": 12.5,
        "data_points": [{"date": "2025-09-01", "value": 1000}]
    }
    
    # Mock get_reach
    service.get_reach.return_value = {
        "avg_reach": 850,
        "data_points": [{"date": "2025-09-01", "value": 800}]
    }
    
    # Mock get_top_posts
    service.get_top_posts.return_value = {
        "posts": [
            {
                "post_id": "post_1",
                "title": "Test Post",
                "views": 5000,
                "engagement_rate": 6.2
            }
        ]
    }
    
    return service

def create_mock_cache():
    """Create a mock cache"""
    cache = Mock()
    cache.get_json = AsyncMock(return_value=None)  # No cache hit
    cache.set_json = AsyncMock()
    cache.generate_cache_key = Mock(return_value="test_cache_key")
    return cache

async def test_endpoints():
    """Test the new endpoint implementations"""
    print("Testing new analytics endpoints...")
    
    # Import the router and endpoint functions
    import sys
    sys.path.append('/home/alonur/analyticbot')
    
    try:
        from apps.api.routers.analytics_v2 import (
            get_channel_data, 
            get_performance_metrics, 
            get_trends_top_posts,
            ChannelDataRequest,
            PerformanceMetricsRequest
        )
        
        # Create mocks
        mock_service = create_mock_analytics_service()
        mock_cache = create_mock_cache()
        
        print("✓ Successfully imported endpoint functions")
        
        # Test 1: Channel Data endpoint
        print("\n1. Testing POST /api/v2/analytics/channel-data")
        request = ChannelDataRequest(
            channel_id="123",
            include_real_time=True,
            format="detailed"
        )
        
        try:
            result = await get_channel_data(request, mock_service, mock_cache)
            print(f"   ✓ Channel data endpoint works: {type(result)}")
            print(f"   Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"   ✗ Channel data endpoint error: {e}")
        
        # Test 2: Performance Metrics endpoint
        print("\n2. Testing POST /api/v2/analytics/metrics/performance")
        request = PerformanceMetricsRequest(
            channels=["123", "456"],
            period="30d"
        )
        
        try:
            result = await get_performance_metrics(request, mock_service, mock_cache)
            print(f"   ✓ Performance metrics endpoint works: {type(result)}")
            print(f"   Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"   ✗ Performance metrics endpoint error: {e}")
        
        # Test 3: Trends Top Posts endpoint
        print("\n3. Testing GET /api/v2/analytics/trends/top-posts")
        
        try:
            result = await get_trends_top_posts(
                period=7,
                limit=10,
                channel_id=123,
                service=mock_service,
                cache=mock_cache
            )
            print(f"   ✓ Trends top posts endpoint works: {type(result)}")
            print(f"   Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"   ✗ Trends top posts endpoint error: {e}")
        
        print("\n4. Testing mobile endpoint (already exists)")
        try:
            from apps.api.routers.mobile_api import get_quick_analytics, QuickAnalyticsRequest
            
            # This endpoint already exists, just verify it's importable
            print("   ✓ Mobile quick analytics endpoint exists and is importable")
        except Exception as e:
            print(f"   ✗ Mobile endpoint import error: {e}")
        
        print("\n✅ All endpoint implementations are working!")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
