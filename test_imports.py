#!/usr/bin/env python3
"""
Import test script to validate all Phase 4.6 dependencies
"""

import sys
import traceback

def test_import(module_name: str, description: str = ""):
    """Test importing a module and report results"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - {description}: {e}")
        return False

def main():
    print("🧪 Testing Phase 4.6 imports...\n")
    
    # Core dependencies
    test_import("apps.mtproto.config", "MTProto configuration")
    test_import("apps.mtproto.di", "Dependency injection container")
    test_import("infra.tg.telethon_client", "Telethon client wrapper")
    test_import("infra.tg.account_pool", "Account pool manager")
    test_import("infra.tg.proxy_pool", "Proxy pool manager") 
    test_import("infra.common.ratelimit", "Enhanced rate limiter")
    test_import("apps.mtproto.metrics", "Prometheus metrics")
    test_import("infra.obs.otel", "OpenTelemetry tracing")
    test_import("apps.mtproto.health_http", "Health check server")
    test_import("infra.tg.dc_router", "DC router")
    test_import("infra.common.faults", "Fault injection")
    
    # Database and core models
    test_import("infra.db.connection", "Database connection")
    test_import("core.models.common", "Common domain models")
    
    # Optional external dependencies
    print("\n📦 Testing optional dependencies:")
    test_import("telethon", "Telethon Telegram client")
    test_import("dependency_injector", "Dependency injection framework")
    test_import("slowapi", "Rate limiting framework")
    test_import("prometheus_client", "Prometheus metrics")
    test_import("opentelemetry.trace", "OpenTelemetry tracing")
    
    print("\n✨ Import test completed!")

if __name__ == "__main__":
    main()
