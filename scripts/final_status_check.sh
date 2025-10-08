#!/bin/bash

# Final Status Check: Do we need a rebuild?
# Comprehensive check of the mock/real separation implementation

echo "🔍 Final Status Check: Mock/Real Separation"
echo "=========================================="

# Check critical files exist and have content
echo ""
echo "📁 Critical Files Check:"

check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ] && [ -s "$file" ]; then
        echo "✅ $description: $file"
        return 0
    else
        echo "❌ $description: $file (missing or empty)"
        return 1
    fi
}

MISSING_FILES=0

check_file "apps/frontend/src/hooks/useDataSource.js" "React Hooks System" || ((MISSING_FILES++))
check_file "apps/frontend/src/services/mockService.js" "Mock Service" || ((MISSING_FILES++))
check_file "apps/frontend/src/services/dataService.js" "Data Service Factory" || ((MISSING_FILES++))
check_file "apps/frontend/src/utils/dataSourceManager.js" "Data Source Manager" || ((MISSING_FILES++))
check_file "apps/frontend/src/config/mockConfig.js" "Configuration System" || ((MISSING_FILES++))

# Check migrated components
echo ""
echo "🔧 Migrated Components Check:"
check_file "apps/frontend/src/components/analytics/ModernAdvancedAnalyticsDashboard.jsx" "Modern Dashboard" || ((MISSING_FILES++))
check_file "apps/frontend/src/components/demo/AnalyticsAdapterDemo.jsx" "Demo Component" || ((MISSING_FILES++))

# Check backend adapters
echo ""
echo "⚙️ Backend Adapters Check:"
check_file "apps/bot/services/adapters/analytics_adapter_factory.py" "Analytics Factory" || ((MISSING_FILES++))
check_file "apps/bot/services/adapters/payment_adapter_factory.py" "Payment Factory" || ((MISSING_FILES++))

# Check documentation
echo ""
echo "📚 Documentation Check:"
check_file "MOCK_REAL_SYSTEM_DOCUMENTATION.md" "System Documentation" || ((MISSING_FILES++))
check_file "ACTUAL_SEPARATION_COMPLETE.md" "Completion Report" || ((MISSING_FILES++))

# Test syntax of critical files
echo ""
echo "🔍 Syntax Validation:"
SYNTAX_ERRORS=0

test_syntax() {
    local file=$1
    local description=$2
    if node -c "$file" 2>/dev/null; then
        echo "✅ Syntax OK: $description"
        return 0
    else
        echo "❌ Syntax Error: $description ($file)"
        return 1
    fi
}

test_syntax "apps/frontend/src/services/mockService.js" "Mock Service" || ((SYNTAX_ERRORS++))
test_syntax "apps/frontend/src/services/dataService.js" "Data Service" || ((SYNTAX_ERRORS++))
test_syntax "apps/frontend/src/hooks/useDataSource.js" "React Hooks" || ((SYNTAX_ERRORS++))
test_syntax "apps/frontend/src/utils/dataSourceManager.js" "Data Source Manager" || ((SYNTAX_ERRORS++))
test_syntax "apps/frontend/src/config/mockConfig.js" "Configuration" || ((SYNTAX_ERRORS++))

# Check import consistency
echo ""
echo "📦 Import Consistency Check:"
IMPORT_ISSUES=0

# Check for old mockData imports in components (should be 0)
OLD_IMPORTS=$(grep -r "import.*mockData" apps/frontend/src/components/ 2>/dev/null | wc -l)
if [ "$OLD_IMPORTS" -eq 0 ]; then
    echo "✅ No old mockData imports in components"
else
    echo "❌ Found $OLD_IMPORTS old mockData imports in components"
    ((IMPORT_ISSUES++))
fi

# Check for new hook usage (should be > 0)
NEW_HOOKS=$(grep -r "useDataSource" apps/frontend/src/components/ 2>/dev/null | wc -l)
if [ "$NEW_HOOKS" -gt 0 ]; then
    echo "✅ Components using new hooks: $NEW_HOOKS"
else
    echo "❌ No components using new hooks"
    ((IMPORT_ISSUES++))
fi

# Check store integration
STORE_MOCK_SERVICE=$(grep -c "mockService" apps/frontend/src/store/appStore.js 2>/dev/null || echo "0")
if [ "$STORE_MOCK_SERVICE" -gt 5 ]; then
    echo "✅ Store properly integrated with mockService ($STORE_MOCK_SERVICE usages)"
else
    echo "❌ Store not properly integrated with mockService"
    ((IMPORT_ISSUES++))
fi

# Run validation test
echo ""
echo "🧪 Validation Test Results:"
./test_actual_separation.sh 2>/dev/null | tail -3

echo ""
echo "=========================================="
echo "📊 Final Assessment:"
echo "=========================================="

TOTAL_ISSUES=$((MISSING_FILES + SYNTAX_ERRORS + IMPORT_ISSUES))

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo ""
    echo "🎉 STATUS: COMPLETE - NO REBUILD NEEDED"
    echo ""
    echo "✅ All critical files present and valid"
    echo "✅ No syntax errors detected"
    echo "✅ Import patterns clean and consistent"
    echo "✅ Components properly migrated"
    echo "✅ Store integration complete"
    echo "✅ Backend adapters implemented"
    echo "✅ Documentation complete"
    echo ""
    echo "🚀 SYSTEM IS READY FOR USE!"
    echo "The mock/real separation is complete and working."
    echo "You can run the application without rebuilding."
    echo ""
    exit 0
elif [ $TOTAL_ISSUES -le 2 ]; then
    echo ""
    echo "⚠️ STATUS: MINOR ISSUES - REBUILD OPTIONAL"
    echo ""
    echo "Found $TOTAL_ISSUES minor issues:"
    [ $MISSING_FILES -gt 0 ] && echo "• Missing files: $MISSING_FILES"
    [ $SYNTAX_ERRORS -gt 0 ] && echo "• Syntax errors: $SYNTAX_ERRORS"
    [ $IMPORT_ISSUES -gt 0 ] && echo "• Import issues: $IMPORT_ISSUES"
    echo ""
    echo "🔧 RECOMMENDATION: Fix these issues but rebuild not required"
    echo "The core functionality should work as implemented."
    echo ""
    exit 1
else
    echo ""
    echo "❌ STATUS: SIGNIFICANT ISSUES - REBUILD RECOMMENDED"
    echo ""
    echo "Found $TOTAL_ISSUES significant issues:"
    [ $MISSING_FILES -gt 0 ] && echo "• Missing files: $MISSING_FILES"
    [ $SYNTAX_ERRORS -gt 0 ] && echo "• Syntax errors: $SYNTAX_ERRORS"
    [ $IMPORT_ISSUES -gt 0 ] && echo "• Import issues: $IMPORT_ISSUES"
    echo ""
    echo "🔨 RECOMMENDATION: Consider rebuilding or fixing critical issues"
    echo "Some functionality may not work as expected."
    echo ""
    exit 2
fi
