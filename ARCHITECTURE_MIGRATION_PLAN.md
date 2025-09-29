# 🏗️ DETAILED ARCHITECTURE MIGRATION PLAN

## 📊 **CURRENT STATE ANALYSIS**

### Current Structure (332+ Python files):
```
analyticbot/
├── apps/ (178 files)
│   ├── api/ (60 files) - REST API endpoints
│   ├── bot/ (82 files) - Telegram bot logic
│   ├── frontend/ (0 files) - Web interface (JS/HTML)
│   ├── jobs/ (9 files) - Background tasks
│   ├── mtproto/ (22 files) - MTProto protocol
│   └── shared/ (4 files) - Common utilities
├── core/ (38 files)
│   ├── adapters/ - Infrastructure adapters
│   ├── common/ - Common utilities
│   ├── domain/ - Domain entities
│   ├── models/ - Data models
│   ├── ports/ - Interface contracts
│   ├── repositories/ - Data access
│   ├── security_engine/ - Security logic
│   └── services/ - Business services
├── infra/ (72 files)
│   ├── adapters/ - External service adapters
│   ├── db/ - Database layer
│   ├── telegram/ - Telegram infrastructure
│   ├── notifications/ - Notification services
│   └── [20+ other infrastructure modules]
├── src/ (3 files)
│   ├── api_service/ - API service layer
│   └── shared_kernel/ - Shared kernel
├── tests/ (38 files)
└── config/ (3 files)
```

---

## 🎯 **TARGET ARCHITECTURE**

### New Optimal Structure:
```
analyticbot/
├── config/                    # 📋 Centralized Configuration
│   ├── environments/          # Environment-specific configs
│   ├── settings.py           # Main settings
│   └── demo_mode_config.py   # Demo configuration
├── domain/                    # 🏛️ Pure Domain Layer
│   ├── entities/             # Business entities
│   ├── value_objects/        # Value objects
│   ├── services/             # Domain services
│   └── events/               # Domain events
├── application/               # 🔧 Application Layer
│   ├── use_cases/            # Business use cases
│   ├── services/             # Application services
│   ├── commands/             # Command handlers
│   ├── queries/              # Query handlers
│   └── event_bus/            # Event coordination
├── infrastructure/            # 🔌 Infrastructure Layer
│   ├── adapters/             # External service adapters
│   ├── repositories/         # Data persistence
│   ├── messaging/            # Event messaging
│   ├── telegram/             # Telegram integration
│   ├── database/             # Database setup
│   ├── cache/                # Caching layer
│   └── notifications/        # Notification services
├── presentation/              # 🎨 Presentation Layer
│   ├── api/                  # REST API (orchestrator)
│   ├── bot/                  # Telegram bot interface
│   ├── frontend/             # Web interface
│   ├── jobs/                 # Background job interface
│   ├── mtproto/              # MTProto interface
│   └── shared/               # Common presentation utilities
└── tests/                     # 🧪 Test Layer
    ├── unit/
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── presentation/
    ├── integration/
    └── e2e/
```

---

## 📋 **PHASE-BY-PHASE MIGRATION PLAN**

### **PHASE 1: FOUNDATION SETUP (Week 1)**

#### **Step 1.1: Create New Directory Structure**
```bash
# Create new architecture folders
mkdir -p domain/{entities,value_objects,services,events}
mkdir -p application/{use_cases,services,commands,queries,event_bus}  
mkdir -p infrastructure/{adapters,repositories,messaging,telegram,database,cache,notifications}
mkdir -p presentation/{api,bot,frontend,jobs,mtproto,shared}
mkdir -p tests/{unit/{domain,application,infrastructure,presentation},integration,e2e}
mkdir -p config/environments
```

#### **Step 1.2: Create Event Bus Foundation**
**New File**: `application/event_bus/event_bus.py`
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Type, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DomainEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]

class EventHandler(ABC):
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        pass

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
    
    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent):
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler.handle(event)
```

#### **Step 1.3: Migration Script Creation**
**New File**: `scripts/migrate_architecture.py`
```python
#!/usr/bin/env python3
"""
Architecture Migration Script
Safely moves files from current structure to new architecture
"""

import os
import shutil
from pathlib import Path

MIGRATION_MAP = {
    # Core domain logic -> domain/
    "core/domain/": "domain/entities/",
    "core/models/": "domain/entities/",
    "core/services/": "domain/services/",
    
    # Application layer
    "src/api_service/": "application/services/",
    "src/shared_kernel/": "application/services/",
    "core/common/": "application/services/",
    
    # Infrastructure
    "infra/": "infrastructure/",
    "core/adapters/": "infrastructure/adapters/",
    "core/repositories/": "infrastructure/repositories/",
    
    # Presentation  
    "apps/": "presentation/",
}

def migrate_files():
    for old_path, new_path in MIGRATION_MAP.items():
        if os.path.exists(old_path):
            print(f"Migrating {old_path} -> {new_path}")
            # Implementation here
```

---

### **PHASE 2: DOMAIN LAYER MIGRATION (Week 2)**

#### **Step 2.1: Move Core Domain Logic**
```bash
# Move domain entities
mv core/domain/* domain/entities/
mv core/models/* domain/entities/

# Move domain services  
mv core/services/* domain/services/

# Create domain events
# Manual creation based on current business events
```

#### **Step 2.2: File-by-File Migration Map**

| Current Location | New Location | Action Required |
|------------------|--------------|-----------------|
| `core/models/analytics_model.py` | `domain/entities/analytics.py` | Move + rename |
| `core/models/user_model.py` | `domain/entities/user.py` | Move + rename |
| `core/domain/payment.py` | `domain/entities/payment.py` | Move |
| `core/services/analytics_service.py` | `domain/services/analytics_service.py` | Move |
| `core/common/helpers.py` | `application/services/helpers.py` | Move |

#### **Step 2.3: Update Import Statements**
**Script**: `scripts/update_imports.py`
```python
import re
import os

IMPORT_REPLACEMENTS = {
    r'from core\.models': 'from domain.entities',
    r'from core\.domain': 'from domain.entities', 
    r'from core\.services': 'from domain.services',
    r'from core\.common': 'from application.services',
}

def update_file_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old_pattern, new_import in IMPORT_REPLACEMENTS.items():
        content = re.sub(old_pattern, new_import, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
```

---

### **PHASE 3: APPLICATION LAYER CREATION (Week 3)**

#### **Step 3.1: Extract Use Cases from Apps**
**Target Files to Create**:

1. **`application/use_cases/analytics_use_cases.py`**
```python
from domain.entities.analytics import Analytics
from domain.services.analytics_service import AnalyticsService
from infrastructure.repositories.analytics_repository import AnalyticsRepository

class GetAnalyticsUseCase:
    def __init__(self, 
                 analytics_service: AnalyticsService,
                 analytics_repo: AnalyticsRepository):
        self._service = analytics_service
        self._repo = analytics_repo
    
    async def execute(self, user_id: str, filters: dict) -> Analytics:
        # Business logic extracted from apps/api/routers/analytics_router.py
        pass
```

2. **`application/use_cases/bot_use_cases.py`**
```python
# Extract business logic from apps/bot/handlers/
```

#### **Step 3.2: Migration Mapping for Use Cases**

| Current App Logic | New Use Case | Files to Extract From |
|-------------------|--------------|---------------------|
| Analytics operations | `GetAnalyticsUseCase` | `apps/api/routers/analytics_router.py` |
| User management | `CreateUserUseCase` | `apps/bot/handlers/user_handler.py` |
| Payment processing | `ProcessPaymentUseCase` | `apps/api/routers/payment_router.py` |
| Channel management | `ManageChannelUseCase` | `apps/api/routers/admin_channels_router.py` |

---

### **PHASE 4: INFRASTRUCTURE CONSOLIDATION (Week 4)**

#### **Step 4.1: Consolidate Infrastructure**
```bash
# Move infrastructure components
mv infra/* infrastructure/

# Reorganize by concern
mv infrastructure/db/* infrastructure/database/
mv infrastructure/adapters/* infrastructure/adapters/
```

#### **Step 4.2: Standardize Repository Pattern**
**Template**: `infrastructure/repositories/base_repository.py`
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_all(self) -> List[T]:
        pass
```

---

### **PHASE 5: PRESENTATION LAYER REFACTORING (Week 5)**

#### **Step 5.1: Refactor Apps to Presentation Layer**
```bash
# Move apps to presentation
mv apps/* presentation/

# Refactor to use application layer
```

#### **Step 5.2: Apps Communication via Event Bus**

**Before (Direct Import - REMOVE)**:
```python
# apps/api/routers/analytics_router.py
from apps.bot.services.user_service import UserService  # ❌ Remove
```

**After (Event-Driven - ADD)**:
```python
# presentation/api/routers/analytics_router.py  
from application.event_bus.event_bus import EventBus
from application.use_cases.analytics_use_cases import GetAnalyticsUseCase

@router.get("/analytics")
async def get_analytics(user_id: str):
    use_case = GetAnalyticsUseCase()
    return await use_case.execute(user_id)
```

---

## 🔧 **IMPLEMENTATION SCRIPTS**

### **Script 1: Architecture Validator**
**File**: `scripts/validate_architecture.py`
```python
#!/usr/bin/env python3
"""
Validates new architecture compliance
"""

import ast
import os
from pathlib import Path

FORBIDDEN_IMPORTS = [
    # Presentation should not import from other presentation
    (r'presentation/.*', r'from presentation\.(?!shared)'),
    # Domain should not import infrastructure  
    (r'domain/.*', r'from infrastructure\.'),
    # Application should not import presentation
    (r'application/.*', r'from presentation\.'),
]

def validate_file(file_path):
    violations = []
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Check import violations
                    pass
        except SyntaxError:
            pass
    return violations

def main():
    violations = []
    for py_file in Path('.').rglob('*.py'):
        violations.extend(validate_file(py_file))
    
    if violations:
        print(f"❌ Found {len(violations)} architecture violations")
        for violation in violations:
            print(f"  - {violation}")
        exit(1)
    else:
        print("✅ Architecture validation passed!")
```

### **Script 2: Automated Import Fixer**  
**File**: `scripts/fix_imports.py`
```python
#!/usr/bin/env python3
"""
Automatically fixes imports after migration
"""

import re
import glob

IMPORT_FIXES = {
    # Old -> New import patterns
    r'from core\.models\.(\w+)': r'from domain.entities.\1',
    r'from core\.services\.(\w+)': r'from domain.services.\1',
    r'from apps\.(\w+)\.': r'from presentation.\1.',
    r'from infra\.': r'from infrastructure.',
}

def fix_file_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for old_pattern, new_pattern in IMPORT_FIXES.items():
        content = re.sub(old_pattern, new_pattern, content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed imports in {file_path}")

def main():
    python_files = glob.glob('**/*.py', recursive=True)
    for file_path in python_files:
        fix_file_imports(file_path)

if __name__ == '__main__':
    main()
```

---

## 📋 **EXECUTION CHECKLIST**

### **Week 1: Foundation**
- [ ] Create new directory structure
- [ ] Implement event bus
- [ ] Create migration scripts
- [ ] Backup current codebase
- [ ] Run architecture validator (baseline)

### **Week 2: Domain Migration** 
- [ ] Move core/domain -> domain/entities
- [ ] Move core/models -> domain/entities  
- [ ] Move core/services -> domain/services
- [ ] Update all imports
- [ ] Run tests (fix broken ones)

### **Week 3: Application Layer**
- [ ] Extract use cases from apps/
- [ ] Create application services
- [ ] Implement command/query handlers
- [ ] Update presentation layer to use use cases

### **Week 4: Infrastructure**
- [ ] Consolidate infra/ structure
- [ ] Implement repository pattern
- [ ] Standardize adapter interfaces
- [ ] Update all infrastructure references

### **Week 5: Presentation Refactoring**
- [ ] Move apps/ -> presentation/
- [ ] Eliminate direct app-to-app imports
- [ ] Implement event-driven communication
- [ ] Update API orchestration pattern

### **Week 6: Testing & Validation**
- [ ] Migrate test structure
- [ ] Run full test suite
- [ ] Performance validation
- [ ] Architecture compliance check
- [ ] Documentation update

---

## ⚠️ **RISK MITIGATION**

### **Backup Strategy**
```bash
# Before starting migration
git checkout -b architecture-migration-backup
git add -A && git commit -m "Pre-migration backup"

# Create feature branch
git checkout -b feature/architecture-migration
```

### **Rollback Plan** 
1. Keep old folders until migration complete
2. Gradual migration with feature flags
3. Comprehensive test coverage
4. Performance benchmarking

### **Testing Strategy**
- Unit tests: Domain layer isolation
- Integration tests: Cross-layer communication  
- E2E tests: Full workflow validation
- Performance tests: Response time impact

---

## 🎯 **SUCCESS CRITERIA**

### **Technical Metrics**
- ✅ Zero direct app-to-app imports
- ✅ 100% Clean Architecture compliance 
- ✅ <5% performance degradation
- ✅ All existing tests pass
- ✅ New architecture validation passes

### **Business Metrics**
- ✅ Zero downtime deployment
- ✅ Feature development velocity maintained
- ✅ Bug rate unchanged or improved
- ✅ Team onboarding time reduced

---

**ESTIMATED EFFORT**: 6 weeks (1 developer)
**RISK LEVEL**: Medium (with proper testing)
**BUSINESS IMPACT**: High (long-term maintainability)