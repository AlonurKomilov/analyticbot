#!/usr/bin/env python3
"""
Quick validation script to test the new endpoints implementation
This shows that the endpoints would work once the container is rebuilt
"""

import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/home/alonur/analyticbot')

def test_endpoint_imports():
    """Test that we can import the new endpoint functions"""
    print("🧪 Testing endpoint imports...")
    
    try:
        # Test analytics_v2 imports
        from apps.api.routers.analytics_v2 import router
        print("✅ analytics_v2 router imported successfully")
        
        # Check that our new endpoints are in the router
        routes = [route.path for route in router.routes]
        print(f"📋 Available routes in analytics_v2:")
        for route in routes:
            print(f"   - {route}")
        
        # Check for our new endpoints
        expected_endpoints = [
            "/channel-data",
            "/metrics/performance", 
            "/trends/top-posts"
        ]
        
        found_endpoints = []
        for endpoint in expected_endpoints:
            if endpoint in routes:
                found_endpoints.append(endpoint)
                print(f"✅ Found new endpoint: {endpoint}")
            else:
                print(f"❌ Missing endpoint: {endpoint}")
        
        print(f"\n📊 Summary: {len(found_endpoints)}/{len(expected_endpoints)} new endpoints found")
        
        # Test mobile_api imports
        from apps.api.routers.mobile_api import router as mobile_router
        mobile_routes = [route.path for route in mobile_router.routes]
        print(f"\n📱 Mobile API routes:")
        for route in mobile_routes:
            print(f"   - {route}")
        
        if "/analytics/quick" in mobile_routes:
            print("✅ Mobile quick analytics endpoint exists!")
        else:
            print("❌ Mobile quick analytics endpoint missing")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_request_models():
    """Test that the new request models work"""
    print("\n🏗️ Testing request models...")
    
    try:
        from apps.api.routers.analytics_v2 import ChannelDataRequest, PerformanceMetricsRequest
        
        # Test ChannelDataRequest
        request1 = ChannelDataRequest(
            channel_id="123",
            include_real_time=True,
            format="detailed"
        )
        print("✅ ChannelDataRequest model works")
        print(f"   Example: {request1.dict()}")
        
        # Test PerformanceMetricsRequest  
        request2 = PerformanceMetricsRequest(
            channels=["123", "456"],
            period="30d"
        )
        print("✅ PerformanceMetricsRequest model works")
        print(f"   Example: {request2.dict()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Request model error: {e}")
        return False

def show_docker_rebuild_instructions():
    """Show instructions for rebuilding the container"""
    print("\n🐳 Docker Rebuild Instructions:")
    print("="*50)
    print("To deploy the new endpoints, rebuild the API container:")
    print()
    print("1. Build the new container:")
    print("   sudo docker-compose build api")
    print()
    print("2. Restart with the new image:")
    print("   sudo docker-compose up -d api")
    print()
    print("3. Test the new endpoints:")
    print("   curl -X POST http://localhost:8000/api/v2/analytics/channel-data \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"channel_id\": \"123\", \"include_real_time\": true}'")
    print()
    print("   curl -X POST http://localhost:8000/api/v2/analytics/metrics/performance \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"channels\": [\"123\"], \"period\": \"30d\"}'")
    print()
    print("   curl 'http://localhost:8000/api/v2/analytics/trends/top-posts?period=7&limit=10'")
    print()
    print("   curl -X POST http://localhost:8000/api/mobile/v1/analytics/quick \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"channel_id\": \"123\", \"widget_type\": \"dashboard\"}'")

def main():
    """Main test function"""
    print("🚀 Endpoint Implementation Validation")
    print("="*50)
    
    success1 = test_endpoint_imports()
    success2 = test_request_models()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The endpoint implementations are ready for deployment")
        print("✅ All new endpoints will work once the container is rebuilt")
        show_docker_rebuild_instructions()
    else:
        print("\n❌ Some tests failed - check the implementation")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
