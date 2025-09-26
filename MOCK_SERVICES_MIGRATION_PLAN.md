# Mock Services Centralization - Migration Plan

## Overview

This migration consolidates all scattered mock services into a centralized, clean testing infrastructure.

## Problem Solved

**Before:**
- 18+ mock services scattered across domains
- Inconsistent mocking patterns
- Test code mixed with production code
- Difficult maintenance and discovery

**After:**
- Centralized mock infrastructure in `tests/mocks/`
- Consistent base classes and patterns
- Clean separation from production code
- Easy service discovery and management

## Architecture

```
tests/
├── mocks/
│   ├── __init__.py              # Main exports
│   ├── base.py                  # BaseMockService, metrics
│   ├── registry.py              # Service registry
│   ├── factory.py               # Service factory
│   ├── protocols.py             # Service protocols
│   ├── auto_register.py         # Auto-registration
│   ├── compat.py                # Backward compatibility
│   ├── services/                # Centralized services
│   │   ├── mock_analytics_service.py
│   │   ├── mock_payment_service.py
│   │   ├── mock_email_service.py
│   │   └── ...
│   ├── adapters/                # Mock adapters
│   └── data/                    # Mock data generators
```

## Usage Examples

### New Recommended Usage

```python
from tests.mocks import mock_factory

# Create individual services
analytics = mock_factory.create_analytics_service()
payment = mock_factory.create_payment_service()

# Create complete testing suite
test_env = mock_factory.create_testing_suite()
analytics = test_env["analytics"]
payment = test_env["payment"]

# Reset all mocks
mock_factory.reset_all_services()
```

### Backward Compatibility

```python
# Old code still works (with deprecation warning)
from tests.mocks.compat import MockAnalyticsService
service = MockAnalyticsService()  # Warns about deprecation
```

## Migration Status

### ✅ Completed
- [x] Infrastructure setup (registry, factory, base classes)
- [x] MockAnalyticsService centralized
- [x] MockPaymentService centralized  
- [x] MockEmailService centralized
- [x] Backward compatibility layer

### 🔄 In Progress
- [ ] MockTelegramService migration
- [ ] MockAuthService migration
- [ ] MockAdminService migration
- [ ] MockAIService migration
- [ ] MockDemoDataService migration
- [ ] MockDatabaseService migration

### 📋 Pending
- [ ] Update all imports to use centralized services
- [ ] Remove scattered mock files
- [ ] Update test configurations
- [ ] Documentation updates

## Migration Steps

### Phase 1: Infrastructure ✅
1. Created centralized mock infrastructure
2. Established consistent patterns
3. Built service registry and factory

### Phase 2: Service Migration (Current)
1. Migrate each mock service to centralized location
2. Maintain backward compatibility
3. Update service implementations with consistent patterns

### Phase 3: Import Updates
1. Update all code to use centralized imports
2. Remove deprecation warnings
3. Clean up old mock files

### Phase 4: Cleanup
1. Remove scattered mock service files
2. Update documentation
3. Add architectural tests to prevent regression

## Benefits Achieved

1. **Clean Architecture**: Test infrastructure separated from production
2. **Consistency**: All mocks follow same patterns via BaseMockService
3. **Maintainability**: Single location for all mock services
4. **Discoverability**: Easy to find and use mock services
5. **Metrics**: Built-in call tracking for test verification
6. **Flexibility**: Factory pattern allows easy configuration

## Files to Remove (Post-Migration)

```bash
# Scattered mock services (18+ files)
src/api_service/infrastructure/testing/services/mock_*.py
src/api_service/application/services/__mocks__/mock_*.py
src/bot_service/application/services/adapters/mock_*.py
```

## Testing the Migration

```python
import tests.mocks.mock_factory as factory
from tests.mocks.base import mock_metrics

# Test service creation
analytics = factory.create_analytics_service()
assert analytics.get_service_name() == "MockAnalyticsService"

# Test metrics collection
await analytics.get_channel_metrics("test_channel")
stats = mock_metrics.get_stats()
assert stats["total_calls"] == 1

# Test reset functionality
factory.reset_all_services()
assert analytics.metrics_generated == 0
```

## Next Steps

1. Complete remaining service migrations
2. Update imports across codebase  
3. Remove deprecated files
4. Add integration tests for mock infrastructure