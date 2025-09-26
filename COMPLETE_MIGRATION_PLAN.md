# 🚀 COMPLETE MIGRATION PLAN: `core/apps/infra/` → `src/` ARCHITECTURE

## 📊 **CURRENT STATE ANALYSIS**
- **Total files to migrate**: 102
- **Circular dependencies**: core ↔ infra (critical issue)
- **Migration priority**: Start with zero-dependency files

---

## 🎯 **PHASE 1: FOUNDATION & CRITICAL FIXES (Week 1)**

### **Day 1: Create Shared Kernel Foundation**
```bash
# Create shared kernel structure
mkdir -p src/shared_kernel/{domain,application,infrastructure}/{entities,repositories,services,ports}
mkdir -p src/shared_kernel/infrastructure/{cache,email,monitoring,persistence}

# Migrate zero-dependency files first (safest)
cp core/protocols.py src/shared_kernel/domain/protocols.py
cp core/ports/* src/shared_kernel/domain/ports/
cp core/repositories/interfaces.py src/shared_kernel/domain/repositories/
```

### **Day 2: Fix DI Container Critical Issues**
1. **Update core/di_container.py imports:**
   - `from src.shared_kernel.di` → working implementation
   - `from src.__mocks__.*` → proper mock paths
   - Test all imports resolve correctly

2. **Create src/shared_kernel/infrastructure/di/container.py**
3. **Update compatibility layers in apps/api/main.py and apps/bot/container.py**

### **Day 3: Migrate Core Models**
```bash
# Domain entities by business domain
mkdir -p src/{analytics,identity,payments}/domain/entities

# Migrate core models to appropriate domains
core/models/user.py → src/identity/domain/entities/
core/models/payment.py → src/payments/domain/entities/
core/models/analytics_*.py → src/analytics/domain/entities/
core/models/base.py → src/shared_kernel/domain/entities/
```

### **Day 4: Migrate Core Services** 
```bash
# Application services by domain
mkdir -p src/{analytics,identity,payments}/application/services

# Migrate business services
core/services/analytics_*.py → src/analytics/application/services/
core/services/user_*.py → src/identity/application/services/
core/services/payment_*.py → src/payments/application/services/
```

### **Day 5-7: Infrastructure Migration**
```bash
# Infrastructure implementations
mkdir -p src/{analytics,identity,payments}/infrastructure/{persistence,external}

# Migrate repository implementations  
infra/db/repositories/analytics_*.py → src/analytics/infrastructure/persistence/
infra/db/repositories/user_*.py → src/identity/infrastructure/persistence/
infra/db/repositories/payment_*.py → src/payments/infrastructure/persistence/

# Shared infrastructure
infra/cache/ → src/shared_kernel/infrastructure/cache/
infra/email/ → src/shared_kernel/infrastructure/email/
infra/monitoring/ → src/shared_kernel/infrastructure/monitoring/
```

---

## 🎯 **PHASE 2: DOMAIN SEPARATION (Week 2)**

### **Analytics Domain**
```
src/analytics/
├── domain/
│   ├── entities/           # From core/models/analytics_*
│   ├── repositories/       # Interfaces from core/repositories/
│   └── value_objects/      # Analytics-specific VOs
├── application/
│   ├── services/          # From core/services/analytics_*
│   └── use_cases/         # New analytics use cases
└── infrastructure/
    ├── persistence/       # From infra/db/repositories/analytics_*
    └── external/          # TG API adapters
```

### **Identity Domain**  
```
src/identity/
├── domain/
│   ├── entities/          # From core/models/user.py
│   ├── repositories/      # User repository interfaces
│   └── value_objects/     # Email, UserId, etc.
├── application/
│   ├── services/         # From core/services/user_*
│   └── use_cases/        # Registration, auth, etc.
└── infrastructure/
    ├── persistence/      # From infra/db/repositories/user_*
    └── external/         # JWT, OAuth services
```

### **Security Domain**
```
src/security/
├── domain/               # From core/security_engine/
├── application/         # Security use cases
└── infrastructure/      # Auth providers, MFA
```

---

## 🎯 **PHASE 3: APPLICATION LAYER MIGRATION (Week 3)**

### **API Service Migration**
```
src/api_service/
├── presentation/
│   ├── routers/         # From apps/api/routers/
│   ├── middleware/      # From apps/api/middleware/
│   └── dependencies/    # DI configuration
├── application/
│   └── services/        # API-specific services
└── infrastructure/
    └── adapters/        # External API adapters
```

### **Bot Service Migration**  
```
src/bot_service/
├── presentation/
│   ├── handlers/        # Telegram handlers
│   └── commands/        # Bot commands
├── application/
│   └── services/        # Bot business logic
└── infrastructure/
    └── adapters/        # Telegram API adapters
```

---

## 🎯 **PHASE 4: CLEANUP & VALIDATION (Week 4)**

### **Day 1-2: Update Import Statements**
```python
# Create automated import updater
python scripts/update_all_imports.py

# Update patterns:
# OLD: from core.models import User
# NEW: from src.identity.domain.entities import User

# OLD: from infra.db.repositories import UserRepository  
# NEW: from src.identity.infrastructure.persistence import AsyncpgUserRepository
```

### **Day 3-4: Remove Legacy Directories**
```bash
# Create archive backup
mkdir archive/legacy_architecture
mv core apps infra archive/legacy_architecture/

# Keep only compatibility redirects for gradual transition
mkdir {core,apps,infra}
# Create __init__.py files with deprecation warnings and redirects
```

### **Day 5-7: Comprehensive Testing**
```bash
# Test all services start correctly
python -m src.api_service.presentation.main
python -m src.bot_service.presentation.main

# Run full test suite
pytest tests/ -v

# Load testing to ensure no performance regression
python scripts/load_test_after_migration.py
```

---

## 🛠 **AUTOMATED MIGRATION SCRIPTS**

### **Script 1: File Migration**