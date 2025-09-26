# Module Extraction Migration Guide

## Overview
This guide covers the extraction of functionality from shared_kernel into dedicated modules for better separation of concerns.

## Extracted Modules

### 1. Monitoring Module (`src/monitoring/`)

**Purpose**: Centralized logging, metrics collection, and health monitoring

**Components**:
- `domain/models.py` - LogEntry, Metric, HealthCheck domain models
- `application/services/monitoring_service.py` - Core monitoring service
- Module follows clean architecture with domain → application → infrastructure layers

**Usage Example**:
```python
from src.monitoring import get_monitoring_service, LogLevel

# Get monitoring service
monitoring = get_monitoring_service()

# Log messages
await monitoring.log(LogLevel.INFO, "User logged in", "auth", {"user_id": 123})

# Record metrics
await monitoring.record_metric("api_requests", 1, {"endpoint": "/users"}, "counter")

# Health check
health = await monitoring.perform_health_check("database")
```

**Migration Steps**:
1. Replace imports from `src.shared_kernel.infrastructure.monitoring` with `src.monitoring`
2. Update dependency injection to use monitoring module services
3. Update configuration to point to monitoring module

## Benefits of Extraction

1. **Separation of Concerns**: Monitoring is now a dedicated module with clear boundaries
2. **Independent Development**: Monitoring can be developed and tested independently
3. **Reusability**: Monitoring module can be easily reused across projects
4. **Maintainability**: Cleaner module structure with focused responsibilities

## Module Dependency Rules

After extraction, modules should follow these dependency rules:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Module A  │    │ shared_kernel│    │ Monitoring  │
│             │───▶│             │    │             │
└─────────────┘    │ - interfaces│    └─────────────┘
                   │ - events    │           ▲
┌─────────────┐    │ - exceptions│           │
│   Module B  │───▶│             │───────────┘
└─────────────┘    └─────────────┘
```

**Rules**:
- ✅ Modules can depend on shared_kernel
- ✅ Modules can depend on extracted infrastructure modules (like monitoring)  
- ❌ Modules should NOT depend on each other directly
- ✅ Use events/interfaces for inter-module communication

## Next Steps

1. **Complete Migration**: Update all modules to use the new monitoring module
2. **Add More Extractions**: Consider extracting other infrastructure concerns
3. **Enforce Boundaries**: Add linting rules to prevent direct module dependencies
4. **Documentation**: Update architecture docs to reflect new module structure

## Testing

Test the extracted monitoring module:

```python
import sys
sys.path.insert(0, 'src')

from monitoring import get_monitoring_service, LogLevel

# Test basic functionality
monitoring = get_monitoring_service()
# ... test code
```
