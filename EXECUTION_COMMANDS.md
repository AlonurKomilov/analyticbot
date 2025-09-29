# 🎯 STEP-BY-STEP EXECUTION COMMANDS

## 📋 **PHASE 1: FOUNDATION (COMPLETED)**
✅ New architecture structure created  
✅ Event bus implemented  
✅ Migration scripts ready

---

## 🏗️ **PHASE 2: DOMAIN LAYER MIGRATION (START HERE)**

### **Step 2.1: Run baseline validation**
```bash
cd /home/abcdeveloper/projects/analyticbot
python3 scripts/validate_architecture.py
```

### **Step 2.2: Backup current state**
```bash
# Create backup branch
git checkout -b architecture-migration-backup
git add -A && git commit -m "Pre-migration backup - current state"

# Create working branch
git checkout -b feature/clean-architecture-migration
```

### **Step 2.3: Migrate domain entities**
```bash
# Move core domain models to new domain layer
cp -r core/models/* domain/entities/ 2>/dev/null || echo "No core/models found"
cp -r core/domain/* domain/entities/ 2>/dev/null || echo "No core/domain found"

# Move domain services
cp -r core/services/* domain/services/ 2>/dev/null || echo "No core/services found"

# Verify what we copied
echo "🔍 Domain entities created:"
ls -la domain/entities/
echo "🔍 Domain services created:"
ls -la domain/services/
```

### **Step 2.4: Create specific domain entities (manual)**
```bash
# You'll need to manually create these based on your current models:
touch domain/entities/analytics.py
touch domain/entities/user.py  
touch domain/entities/payment.py
touch domain/entities/channel.py
touch domain/entities/message.py

# Create domain services
touch domain/services/analytics_service.py
touch domain/services/user_service.py
touch domain/services/payment_service.py
```

---

## 🔧 **PHASE 3: APPLICATION LAYER CREATION**

### **Step 3.1: Extract use cases from current apps**
```bash
# Analyze current business logic locations
echo "🔍 Current API endpoints (potential use cases):"
find apps/api -name "*router*.py" | head -10

echo "🔍 Current bot handlers (potential use cases):"
find apps/bot -name "*handler*.py" | head -10

# Create use case files
touch application/use_cases/analytics_use_cases.py
touch application/use_cases/user_use_cases.py
touch application/use_cases/payment_use_cases.py
touch application/use_cases/channel_use_cases.py
```

### **Step 3.2: Create application services**
```bash
# Move shared utilities to application layer
cp -r core/common/* application/services/ 2>/dev/null || echo "No core/common found"
cp -r src/api_service/* application/services/ 2>/dev/null || echo "No src/api_service found"
cp -r src/shared_kernel/* application/services/ 2>/dev/null || echo "No src/shared_kernel found"

# Create application service files
touch application/services/analytics_app_service.py
touch application/services/user_app_service.py
touch application/commands/create_user_command.py
touch application/queries/get_analytics_query.py
```

---

## 🔌 **PHASE 4: INFRASTRUCTURE MIGRATION**

### **Step 4.1: Move infrastructure components**
```bash
# Copy infrastructure to new location
cp -r infra/* infrastructure/ 2>/dev/null || echo "No infra folder found"

# Reorganize by concern
mkdir -p infrastructure/database/migrations
mkdir -p infrastructure/adapters/telegram
mkdir -p infrastructure/adapters/external_apis
mkdir -p infrastructure/repositories/implementations

# Move database components
mv infrastructure/db/* infrastructure/database/ 2>/dev/null || echo "No db folder to move"

# Move adapters
cp -r core/adapters/* infrastructure/adapters/ 2>/dev/null || echo "No core/adapters found"
cp -r core/repositories/* infrastructure/repositories/ 2>/dev/null || echo "No core/repositories found"
```

### **Step 4.2: Create repository interfaces**
```bash
# Create repository interface files
touch infrastructure/repositories/analytics_repository.py
touch infrastructure/repositories/user_repository.py
touch infrastructure/repositories/payment_repository.py

# Create adapter files
touch infrastructure/adapters/telegram/telegram_adapter.py
touch infrastructure/adapters/external_apis/payment_gateway_adapter.py
```

---

## 🎨 **PHASE 5: PRESENTATION LAYER REFACTORING**

### **Step 5.1: Move apps to presentation**
```bash
# Copy apps to presentation layer
cp -r apps/api/* presentation/api/ 2>/dev/null
cp -r apps/bot/* presentation/bot/ 2>/dev/null  
cp -r apps/frontend/* presentation/frontend/ 2>/dev/null
cp -r apps/jobs/* presentation/jobs/ 2>/dev/null
cp -r apps/mtproto/* presentation/mtproto/ 2>/dev/null
cp -r apps/shared/* presentation/shared/ 2>/dev/null

echo "✅ Apps copied to presentation layer"
```

### **Step 5.2: Update imports in presentation layer**
```bash
# Create import fixing script
python3 -c "
import re
import glob

# Fix imports in all presentation files
for file_path in glob.glob('presentation/**/*.py', recursive=True):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace old imports with new ones
        replacements = [
            (r'from core\.models\.', 'from domain.entities.'),
            (r'from core\.services\.', 'from domain.services.'),
            (r'from core\.common\.', 'from application.services.'),
            (r'from apps\.', 'from presentation.'),
        ]
        
        for old, new in replacements:
            content = re.sub(old, new, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f'Updated imports in {file_path}')
    except Exception as e:
        print(f'Error updating {file_path}: {e}')
"
```

---

## 🧪 **PHASE 6: TESTING & VALIDATION**

### **Step 6.1: Run architecture validation**
```bash
# Run the validator to check compliance
python3 scripts/validate_architecture.py

# Check for remaining old imports
echo "🔍 Checking for old import patterns:"
grep -r "from apps\." presentation/ || echo "✅ No old apps imports found"
grep -r "from core\." domain/ application/ || echo "✅ No old core imports found"
```

### **Step 6.2: Run existing tests**
```bash
# Run tests to see what breaks
python3 -m pytest tests/ -v | head -50

# Check if tests still pass (expect some failures initially)
echo "📊 Test results summary:"
python3 -m pytest tests/ --tb=no -q | tail -5
```

### **Step 6.3: Fix broken imports gradually**
```bash
# Create import fixer for tests
python3 -c "
import re
import glob

# Fix imports in test files
for file_path in glob.glob('tests/**/*.py', recursive=True):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace test imports
        replacements = [
            (r'from apps\.', 'from presentation.'),
            (r'from core\.models\.', 'from domain.entities.'),
            (r'from core\.services\.', 'from domain.services.'),
            (r'from infra\.', 'from infrastructure.'),
        ]
        
        for old, new in replacements:
            content = re.sub(old, new, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print(f'Fixed test imports in {file_path}')
    except Exception as e:
        print(f'Error fixing {file_path}: {e}')
"
```

---

## 📈 **PROGRESS TRACKING COMMANDS**

### **Check migration progress**
```bash
echo "📊 MIGRATION PROGRESS REPORT"
echo "============================="

echo "📁 New structure files:"
find domain application infrastructure presentation -name "*.py" | wc -l

echo "📁 Old structure files remaining:"
find apps core infra src -name "*.py" 2>/dev/null | wc -l || echo "0"

echo "🔍 Import violations remaining:"
python3 scripts/validate_architecture.py 2>&1 | grep -c "violation" || echo "0"

echo "🧪 Test status:"
python3 -m pytest tests/ -q --tb=no | tail -1
```

### **Verify specific layer compliance**
```bash
# Check domain layer purity (should have no external dependencies)
echo "🏛️ Domain layer dependencies:"
grep -r "from \(infrastructure\|presentation\|application\)" domain/ || echo "✅ Domain layer is pure"

# Check application layer (should not depend on presentation)
echo "🔧 Application layer dependencies:"
grep -r "from presentation" application/ || echo "✅ Application layer compliant"

# Check presentation layer (should use application/domain via interfaces)
echo "🎨 Presentation layer direct core dependencies:"
grep -r "from \(core\|infra\)\." presentation/ || echo "✅ Presentation layer compliant"
```

---

## ⚡ **QUICK FIXES FOR COMMON ISSUES**

### **Fix circular imports**
```bash
# Find potential circular imports
python3 -c "
import ast
import os
from collections import defaultdict

def find_imports(file_path):
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return imports
    except:
        return []

# Check for circular dependencies
deps = defaultdict(list)
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            imports = find_imports(path)
            for imp in imports:
                deps[path].append(imp)

print('Potential circular imports to review:')
for file, imports in deps.items():
    if any('from presentation' in imp for imp in imports):
        if 'presentation/' in file:
            print(f'{file}: {[i for i in imports if \"presentation\" in i]}')
"
```

### **Generate migration report**
```bash
# Create final migration report
cat > MIGRATION_REPORT.md << 'EOF'
# Architecture Migration Report

## Files Migrated:
- Domain: $(find domain -name "*.py" | wc -l) files
- Application: $(find application -name "*.py" | wc -l) files  
- Infrastructure: $(find infrastructure -name "*.py" | wc -l) files
- Presentation: $(find presentation -name "*.py" | wc -l) files

## Architecture Compliance:
$(python3 scripts/validate_architecture.py)

## Test Results:
$(python3 -m pytest tests/ -q --tb=no)

## Next Steps:
1. Review and fix remaining import violations
2. Implement missing use cases in application layer
3. Add integration tests for new structure
4. Update documentation
EOF

echo "📋 Migration report generated: MIGRATION_REPORT.md"
```

---

## 🚀 **EXECUTION ORDER SUMMARY**

```bash
# 1. FOUNDATION (DONE)
# ✅ Already completed

# 2. DOMAIN MIGRATION  
git checkout -b feature/clean-architecture-migration
python3 scripts/validate_architecture.py  # baseline
# Manually create domain entities based on current models

# 3. APPLICATION LAYER
# Extract use cases from current routers/handlers
# Create application services

# 4. INFRASTRUCTURE  
cp -r infra/* infrastructure/
# Reorganize and standardize

# 5. PRESENTATION
cp -r apps/* presentation/
# Fix imports and remove cross-dependencies

# 6. VALIDATION
python3 scripts/validate_architecture.py
python3 -m pytest tests/
# Fix remaining issues

# 7. CLEANUP
# Remove old folders after verification
# Update documentation
```

**TOTAL ESTIMATED TIME**: 3-4 weeks
**RISK**: Medium (with proper backup and testing)
**IMPACT**: High (maintainable, scalable architecture)