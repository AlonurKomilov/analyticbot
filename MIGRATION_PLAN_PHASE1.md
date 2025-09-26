# 🚀 MIGRATION PHASE 1: Foundation & Critical Fixes

## Day 1-2: Assessment & Dependency Mapping

### 1. Create Migration Inventory
```bash
# Analyze current dependencies
python scripts/analyze_dependencies.py

# Map imports between core/apps/infra
find core apps infra -name "*.py" -exec grep -l "from \(core\|apps\|infra\)" {} \;

# Identify circular dependencies
python scripts/find_circular_deps.py
```

### 2. Core Components to Migrate
- `core/models/` → `src/shared_kernel/domain/entities/`
- `core/services/` → `src/*/application/services/`  
- `core/repositories/` → `src/*/domain/repositories/`
- `core/security_engine/` → `src/security/`
- `core/ports/` → `src/shared_kernel/domain/ports/`

### 3. Infrastructure Components to Migrate
- `infra/db/repositories/` → `src/*/infrastructure/persistence/`
- `infra/cache/` → `src/shared_kernel/infrastructure/cache/`
- `infra/email/` → `src/shared_kernel/infrastructure/email/`
- `infra/monitoring/` → `src/shared_kernel/infrastructure/monitoring/`

## Day 3-4: Fix Critical DI Container

### Priority 1: Fix Import Errors in core/di_container.py
1. Update all `from src.*` imports to working paths
2. Create proper service factories
3. Test basic dependency injection works

### Priority 2: Create Shared Kernel Structure
```
src/shared_kernel/
├── domain/
│   ├── entities/       # From core/models/
│   ├── repositories/   # From core/repositories/interfaces.py
│   └── ports/         # From core/ports/
├── application/
│   ├── services/      # Common application services
│   └── use_cases/     # Cross-domain use cases
└── infrastructure/
    ├── persistence/   # From infra/db/
    ├── cache/        # From infra/cache/
    └── monitoring/   # From infra/monitoring/
```

## Day 5-7: Create Migration Scripts

### Automated Migration Tools
1. `scripts/migrate_imports.py` - Update import statements
2. `scripts/migrate_files.py` - Move files to new structure  
3. `scripts/create_compatibility_layers.py` - Maintain backward compatibility
4. `scripts/validate_migration.py` - Test migration success

## Success Criteria for Phase 1
- [ ] DI container works without import errors
- [ ] Basic services can start (API, Bot)
- [ ] Shared kernel structure created
- [ ] Migration scripts ready
- [ ] Compatibility layers in place