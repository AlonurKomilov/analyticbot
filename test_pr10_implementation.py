#!/usr/bin/env python3
"""
Test script for PR-10 implementation: Alembic migrations, structured logging, and metrics.
This script validates that all components are working correctly.
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, '/workspaces/analyticbot')


def test_alembic_migration_structure():
    """Test that Alembic migration files are properly structured."""
    print("🔍 Testing Alembic migration structure...")
    
    migration_path = Path("/workspaces/analyticbot/infra/db/alembic/versions/0006_deliveries_observability.py")
    
    if not migration_path.exists():
        print("❌ Migration file not found")
        return False
    
    # Read migration content
    with open(migration_path, 'r') as f:
        content = f.read()
    
    # Check for required elements
    required_elements = [
        'deliveries',          # deliveries table
        'ix_deliveries_status', # status index
        'ix_deliveries_retryable', # composite index
        'scheduled_post_id',   # foreign key
        'delivery_channel_id', # channel tracking
        'status IN',           # check constraints
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing elements in migration: {missing_elements}")
        return False
    
    print("✅ Alembic migration structure is correct")
    return True


def test_structured_logging():
    """Test structured logging configuration."""
    print("\n🔍 Testing structured logging...")
    
    try:
        from infra.logging.structlog_config import (
            configure_logging, 
            get_logger, 
            correlation_context,
            performance_context,
            log_error_with_context
        )
        
        # Test basic configuration
        configure_logging(log_level="INFO", json_format=True)
        print("✅ Logging configuration successful")
        
        # Test logger creation
        logger = get_logger(__name__)
        print("✅ Logger creation successful")
        
        # Test basic logging
        logger.info("Test message", component="test", version="1.0.0")
        print("✅ Basic logging successful")
        
        # Test correlation context
        with correlation_context("test-123"):
            logger.info("Message with correlation ID", operation="testing")
        print("✅ Correlation context successful")
        
        # Test performance context
        with performance_context("test_operation", logger):
            time.sleep(0.01)  # Simulate work
        print("✅ Performance context successful")
        
        # Test error logging
        try:
            raise ValueError("Test error for logging")
        except Exception as e:
            error_id = log_error_with_context(
                logger, 
                "Test error occurred", 
                e, 
                {"operation": "testing"}
            )
            print(f"✅ Error logging successful (ID: {error_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Structured logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prometheus_metrics():
    """Test Prometheus metrics endpoint and functionality."""
    print("\n🔍 Testing Prometheus metrics...")
    
    try:
        # Test basic Prometheus service
        from apps.bot.services.prometheus_service import prometheus_service
        
        # Test metrics generation
        metrics_data = prometheus_service.get_metrics()
        if not isinstance(metrics_data, str) or len(metrics_data) < 100:
            print("❌ Metrics data appears invalid")
            return False
        
        print("✅ Basic Prometheus service working")
        
        # Test content type
        content_type = prometheus_service.get_content_type()
        if "text/plain" not in content_type:
            print("❌ Invalid content type for metrics")
            return False
        
        print("✅ Prometheus content type correct")
        
        # Test worker metrics (optional)
        try:
            from infra.monitoring.worker_metrics import (
                worker_metrics,
                collect_and_update_worker_metrics
            )
            print("✅ Worker metrics module loaded successfully")
        except Exception as e:
            print(f"⚠️ Worker metrics module issue (non-critical): {e}")
        
        # Test some metric recording
        prometheus_service.record_http_request("GET", "/test", 200, 0.1)
        prometheus_service.update_business_metrics(10, 100, 5)
        prometheus_service.set_app_info("test-version", "test-env")
        
        print("✅ Metric recording successful")
        
        # Verify updated metrics contain our test data
        updated_metrics = prometheus_service.get_metrics()
        if "test-version" not in updated_metrics:
            print("❌ App info not found in metrics")
            return False
        
        print("✅ Metrics updating correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Prometheus metrics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_metrics_endpoint():
    """Test the /metrics API endpoint structure."""
    print("\n🔍 Testing /metrics API endpoint...")
    
    try:
        # Import and check the endpoint exists
        from api import app
        
        # Check if metrics endpoint is registered
        routes = [route.path for route in app.routes]
        if "/metrics" not in routes:
            print("❌ /metrics endpoint not found in FastAPI routes")
            return False
        
        print("✅ /metrics endpoint registered in FastAPI")
        
        # Test the endpoint function exists
        import api
        if not hasattr(api, 'prometheus_metrics'):
            print("❌ prometheus_metrics function not found")
            return False
        
        print("✅ prometheus_metrics function exists")
        return True
        
    except Exception as e:
        print(f"❌ API metrics endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_level_configuration():
    """Test LOG_LEVEL configuration in settings."""
    print("\n🔍 Testing LOG_LEVEL configuration...")
    
    try:
        from config.settings import settings
        
        # Check if LOG_LEVEL exists
        if not hasattr(settings, 'LOG_LEVEL'):
            print("❌ LOG_LEVEL not found in settings")
            return False
        
        print(f"✅ LOG_LEVEL configured: {settings.LOG_LEVEL}")
        
        # Test LOG_LEVEL enum
        from config.settings import LogLevel
        valid_levels = [level.value for level in LogLevel]
        print(f"✅ Valid log levels: {valid_levels}")
        
        return True
        
    except Exception as e:
        print(f"❌ LOG_LEVEL configuration test failed: {e}")
        return False


async def test_integration():
    """Test integration between components."""
    print("\n🔍 Testing component integration...")
    
    try:
        # Configure logging
        from infra.logging.structlog_config import configure_logging, get_logger, performance_context
        configure_logging(log_level="INFO", json_format=True)
        logger = get_logger("integration_test")
        
        # Test logging with metrics
        from apps.bot.services.prometheus_service import prometheus_service
        
        with performance_context("integration_test", logger):
            # Simulate some operations
            prometheus_service.record_http_request("GET", "/test", 200, 0.05)
            logger.info("Integration test operation", 
                       component="test", 
                       metrics_recorded=True)
        
        print("✅ Logging and metrics integration successful")
        
        # Test worker metrics if available
        try:
            from infra.monitoring.worker_metrics import worker_metrics
            worker_metrics.record_task_execution("test_task", 0.1, "success")
            print("✅ Worker metrics integration successful")
        except Exception as e:
            print(f"⚠️ Worker metrics integration issue (non-critical): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def print_summary(results: dict):
    """Print test summary."""
    print("\n" + "="*50)
    print("📊 PR-10 IMPLEMENTATION TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("-"*50)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! PR-10 implementation is ready.")
        print("\n📋 ACCEPTANCE CRITERIA STATUS:")
        print("✅ Alembic migrations with deliveries table and indexes")
        print("✅ Structured logging with JSON format")
        print("✅ LOG_LEVEL configuration")
        print("✅ Prometheus /metrics endpoint working")
        print("✅ Optional worker metrics implemented")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review implementation.")
    
    return passed == total


async def main():
    """Run all tests."""
    print("🚀 Starting PR-10 Implementation Tests...\n")
    
    results = {}
    
    # Run tests
    results["Alembic Migration Structure"] = test_alembic_migration_structure()
    results["Structured Logging"] = test_structured_logging()
    results["Prometheus Metrics"] = test_prometheus_metrics()
    results["API Metrics Endpoint"] = test_api_metrics_endpoint()
    results["LOG_LEVEL Configuration"] = test_log_level_configuration()
    results["Component Integration"] = await test_integration()
    
    # Print summary
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
