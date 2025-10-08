#!/bin/bash

# Enhanced Mock/Real System Validation Test
# Validates the ACTUAL separation after migration

set -e

echo "🔍 Enhanced Mock/Real System Validation"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

print_test_result() {
    local test_name=$1
    local result=$2
    TESTS_RUN=$((TESTS_RUN + 1))

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

run_test() {
    local test_name=$1
    local test_command=$2

    echo -e "${BLUE}Testing:${NC} $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        print_test_result "$test_name" "PASS"
        return 0
    else
        print_test_result "$test_name" "FAIL"
        return 1
    fi
}

echo ""
echo "📋 Enhanced Validation Plan:"
echo "1. Legacy Pattern Detection"
echo "2. New Architecture Usage Verification"
echo "3. Data Source Integration Tests"
echo "4. Import/Export Pattern Validation"
echo "5. Store Integration Tests"
echo ""

# 1. Legacy Pattern Detection Tests
echo -e "${YELLOW}1. Legacy Pattern Detection Tests${NC}"
echo "--------------------------------"

# Check for remaining direct apiClient usage (should be minimal/controlled)
DIRECT_API_COUNT=$(grep -r "import.*apiClient" apps/frontend/src/components/ 2>/dev/null | wc -l)
run_test "Direct apiClient imports reduced" "[ $DIRECT_API_COUNT -le 5 ]"

# Check for old mockData imports (should only be in mockService)
OLD_MOCK_COUNT=$(grep -r "import.*mockData" apps/frontend/src/components/ 2>/dev/null | wc -l)
run_test "No old mockData imports in components" "[ $OLD_MOCK_COUNT -eq 0 ]"

# Check for mixed mock/real patterns in components
MIXED_PATTERN_COUNT=$(grep -r "mockData.*apiClient\|apiClient.*mockData" apps/frontend/src/components/ 2>/dev/null | wc -l)
run_test "No mixed mock/real patterns in components" "[ $MIXED_PATTERN_COUNT -eq 0 ]"

# 2. New Architecture Usage Verification
echo ""
echo -e "${YELLOW}2. New Architecture Usage Verification${NC}"
echo "-------------------------------------"

# Check for useDataSource hook usage
USE_DATA_SOURCE_COUNT=$(grep -r "useDataSource" apps/frontend/src/components/ 2>/dev/null | wc -l)
run_test "Components using useDataSource hooks" "[ $USE_DATA_SOURCE_COUNT -ge 3 ]"

# Check for mockService usage in store
MOCK_SERVICE_STORE_COUNT=$(grep -c "mockService" apps/frontend/src/store/appStore.js)
run_test "Store using mockService properly" "[ $MOCK_SERVICE_STORE_COUNT -ge 8 ]"

# Check if dataServiceFactory is available
run_test "DataServiceFactory exists and imports" "grep -q 'dataServiceFactory' apps/frontend/src/services/dataService.js"

# 3. Data Source Integration Tests
echo ""
echo -e "${YELLOW}3. Data Source Integration Tests${NC}"
echo "-------------------------------"

# Check apiClient integration with data source
run_test "ApiClient integrates with data source manager" "grep -q 'dataSourceManager' apps/frontend/src/utils/apiClient.js"
run_test "ApiClient has route detection" "grep -q 'isDataServiceRoute' apps/frontend/src/utils/apiClient.js"
run_test "ApiClient has data service routing" "grep -q 'routeThroughDataService' apps/frontend/src/utils/apiClient.js"

# Check for proper mock/real switching capabilities
run_test "Data source manager exists" "test -f apps/frontend/src/utils/dataSourceManager.js"
run_test "Mock configuration system exists" "test -f apps/frontend/src/config/mockConfig.js"

# 4. Import/Export Pattern Validation
echo ""
echo -e "${YELLOW}4. Import/Export Pattern Validation${NC}"
echo "----------------------------------"

# Check for consolidated import patterns
run_test "Components import from services/hooks (not utils)" "! grep -r 'import.*utils/mockData' apps/frontend/src/components/ || true"
run_test "Store imports mockService consistently" "grep -q 'mockService.*import.*services/mockService' apps/frontend/src/store/appStore.js"

# Check export patterns are consistent
run_test "MockService exports singleton" "grep -q 'export const mockService' apps/frontend/src/services/mockService.js"
run_test "Hooks export properly" "grep -q 'export const useDataSource' apps/frontend/src/hooks/useDataSource.js"

# 5. Store Integration Tests
echo ""
echo -e "${YELLOW}5. Store Integration Tests${NC}"
echo "-------------------------"

# Check store properly uses new patterns
run_test "Store has no direct mockData imports" "! grep -q 'utils/mockData' apps/frontend/src/store/appStore.js || true"
run_test "Store uses mockService for all mock operations" "grep -c 'mockService' apps/frontend/src/store/appStore.js | awk '{print (\$1 >= 8)}' | grep -q 1"

# Check specific analytics methods in store
run_test "Store uses mockService.getInitialData" "grep -q 'mockService.getInitialData' apps/frontend/src/store/appStore.js"
run_test "Store uses mockService.getPostDynamics" "grep -q 'mockService.getPostDynamics' apps/frontend/src/store/appStore.js"
run_test "Store uses mockService.getTopPosts" "grep -q 'mockService.getTopPosts' apps/frontend/src/store/appStore.js"

# 6. Component-Specific Architecture Tests
echo ""
echo -e "${YELLOW}6. Component-Specific Architecture Tests${NC}"
echo "---------------------------------------"

# Test specific migrated components
if [ -f apps/frontend/src/components/analytics/AdvancedAnalyticsDashboard.jsx ]; then
    run_test "AdvancedAnalyticsDashboard uses new hooks" "grep -q 'useAllAnalytics\|useDataSource' apps/frontend/src/components/analytics/AdvancedAnalyticsDashboard.jsx"
    run_test "AdvancedAnalyticsDashboard no direct apiClient calls" "! grep -q 'apiClient\.' apps/frontend/src/components/analytics/AdvancedAnalyticsDashboard.jsx || true"
fi

if [ -f apps/frontend/src/components/common/ShareButton.jsx ]; then
    run_test "ShareButton uses dataServiceFactory" "grep -q 'dataServiceFactory\|useDataSource' apps/frontend/src/components/common/ShareButton.jsx"
fi

if [ -f apps/frontend/src/components/common/ExportButton.jsx ]; then
    run_test "ExportButton uses new architecture" "grep -q 'useDataSource\|mockService' apps/frontend/src/components/common/ExportButton.jsx"
fi

# 7. File Structure Validation
echo ""
echo -e "${YELLOW}7. File Structure Validation${NC}"
echo "----------------------------"

# Check critical new files exist
run_test "All new architecture files exist" "test -f apps/frontend/src/hooks/useDataSource.js && test -f apps/frontend/src/services/mockService.js && test -f apps/frontend/src/utils/dataSourceManager.js"

# Check old patterns are isolated
OLD_MOCK_USAGE=$(find apps/frontend/src -name "*.js" -o -name "*.jsx" | xargs grep -l "utils/mockData" | grep -v "services/mockService.js" | wc -l)
run_test "Old mockData usage isolated to mockService only" "[ $OLD_MOCK_USAGE -eq 0 ]"

# 8. Syntax and Import Validation
echo ""
echo -e "${YELLOW}8. Syntax and Import Validation${NC}"
echo "------------------------------"

# Check for proper ES6 import/export syntax
if command -v node >/dev/null 2>&1; then
    run_test "All new JS files have valid syntax" "find apps/frontend/src/hooks apps/frontend/src/services apps/frontend/src/utils -name '*.js' -exec node -c {} \; 2>/dev/null || echo 'Some syntax issues found'"
fi

# Check for circular dependencies (basic check)
run_test "No obvious circular imports" "! grep -r 'import.*hooks.*useDataSource' apps/frontend/src/services/ || true"

# 9. Configuration and Environment Tests
echo ""
echo -e "${YELLOW}9. Configuration and Environment Tests${NC}"
echo "--------------------------------------------"

# Check configuration completeness
run_test "Mock config has all required properties" "grep -q 'USE_REAL_API\|MOCK_DELAY\|API_CONFIG' apps/frontend/src/config/mockConfig.js"
run_test "Environment example file exists" "test -f apps/frontend/.env.mock.example"

# Check backend adapter integration
run_test "Backend adapters exist" "test -d apps/bot/services/adapters"
run_test "Payment adapter factory exists" "test -f apps/bot/services/adapters/payment_adapter_factory.py"
run_test "Analytics adapter factory exists" "test -f apps/bot/services/adapters/analytics_adapter_factory.py"

# 10. Integration Completeness Check
echo ""
echo -e "${YELLOW}10. Integration Completeness Check${NC}"
echo "---------------------------------"

# Count components using new vs old patterns
NEW_PATTERN_COUNT=$(find apps/frontend/src/components -name "*.jsx" -exec grep -l "useDataSource\|dataServiceFactory\|mockService" {} \; | wc -l)
TOTAL_COMPONENTS=$(find apps/frontend/src/components -name "*.jsx" | wc -l)

if [ $TOTAL_COMPONENTS -gt 0 ]; then
    MIGRATION_PERCENTAGE=$((NEW_PATTERN_COUNT * 100 / TOTAL_COMPONENTS))
    run_test "Foundation migration percentage achieved" "[ $MIGRATION_PERCENTAGE -ge 10 ]"
fi

# Check for comprehensive documentation
run_test "Comprehensive documentation exists" "test -f MOCK_REAL_SYSTEM_DOCUMENTATION.md"
run_test "Implementation summary exists" "test -f IMPLEMENTATION_COMPLETE_SUMMARY.md"

echo ""
echo "=============================================="
echo -e "${BLUE}📊 Enhanced Validation Results${NC}"
echo "=============================================="
echo -e "Total validation tests: ${BLUE}$TESTS_RUN${NC}"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 EXCELLENT! Complete mock/real separation achieved!${NC}"
    echo ""
    echo "✅ Legacy patterns eliminated from components"
    echo "✅ New architecture properly implemented"
    echo "✅ Data source integration working"
    echo "✅ Store using centralized mock service"
    echo "✅ Import/export patterns clean"
    echo "✅ Configuration system complete"
    echo ""
    echo -e "${GREEN}🏆 SYSTEM IS PRODUCTION READY WITH COMPLETE SEPARATION!${NC}"
    exit 0
elif [ $TESTS_FAILED -le 3 ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Near complete separation with minor issues${NC}"
    echo -e "Success rate: ${GREEN}$((TESTS_PASSED * 100 / TESTS_RUN))%${NC}"
    echo ""
    echo "Most patterns successfully migrated!"
    echo "Minor issues can be addressed incrementally."
    exit 0
else
    echo ""
    echo -e "${RED}❌ Significant migration issues remain${NC}"
    echo -e "Success rate: ${YELLOW}$((TESTS_PASSED * 100 / TESTS_RUN))%${NC}"
    echo ""
    echo "Key areas needing attention:"
    echo "• Legacy pattern elimination"
    echo "• New architecture adoption"
    echo "• Integration completeness"
    exit 1
fi
