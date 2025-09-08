#!/bin/bash

echo "🔍 COMPREHENSIVE DUPLICATE CHECK - Week 3-4 Implementation"
echo "========================================================="
echo

echo "1. 📁 Frontend Component Check:"
echo "-------------------------------"
echo "Analytics directory contents:"
ls -la apps/frontend/src/components/analytics/
echo

echo "Checking for duplicate component names in entire frontend:"
find apps/frontend/src -name "*.jsx" -o -name "*.js" | xargs grep -l "AdvancedAnalyticsDashboard\|RealTimeAlertsSystem" | sort | uniq
echo

echo "2. 🔧 Backend Router Check:"
echo "---------------------------"
echo "API routers directory:"
ls -la apps/api/routers/analytics*.py
echo

echo "Checking router prefixes for conflicts:"
echo "Analytics Router Prefixes:"
grep -n "prefix=" apps/api/routers/analytics*.py
echo

echo "3. 🛣️ Route Endpoint Check:"
echo "---------------------------"
echo "Dashboard endpoints across all analytics routers:"
grep -n "@router.get.*dashboard" apps/api/routers/analytics*.py
echo

echo "Checking for duplicate route patterns:"
echo "Real-time metrics endpoints:"
grep -n "real-time\|metrics" apps/api/routers/analytics*.py | head -10
echo

echo "4. 📊 API Client Method Check:"
echo "------------------------------"
echo "Advanced analytics methods in API client:"
grep -A 5 -B 5 "advanced\|Advanced" apps/frontend/src/utils/apiClient.js
echo

echo "5. 🧩 Component Integration Check:"
echo "----------------------------------"
echo "Import statements in main dashboard:"
grep -n "import.*Advanced\|import.*RealTime" apps/frontend/src/components/AnalyticsDashboard.jsx
echo

echo "Component usage in main dashboard:"
grep -n "AdvancedAnalyticsDashboard\|RealTimeAlertsSystem" apps/frontend/src/components/AnalyticsDashboard.jsx
echo

echo "6. 🔄 Main.py Router Registration Check:"
echo "----------------------------------------"
echo "Analytics routers registered in main.py:"
grep -n "analytics.*router" apps/api/main.py
echo

echo "7. 📦 Package Dependencies Check:"
echo "---------------------------------"
echo "Checking for duplicate React component exports:"
if [ -f "apps/frontend/src/components/analytics/index.js" ]; then
    echo "Analytics index.js contents:"
    cat apps/frontend/src/components/analytics/index.js
    echo
    echo "⚠️  WARNING: analytics/index.js references components that may not exist in this directory"
else
    echo "✅ No analytics index.js file (good - no export conflicts)"
fi
echo

echo "8. 🎯 Route Conflict Analysis:"
echo "------------------------------"
echo "Full route analysis by prefix:"
echo
echo "📍 /analytics/* routes (original):"
grep -c "@router\." apps/api/routers/analytics_router.py
echo "endpoints in analytics_router.py"
echo
echo "📍 /api/v2/analytics/* routes (V2):"
grep -c "@router\." apps/api/routers/analytics_v2.py
echo "endpoints in analytics_v2.py"
echo
echo "📍 /api/v2/analytics/advanced/* routes (Week 3-4):"
grep -c "@router\." apps/api/routers/analytics_advanced.py
echo "endpoints in analytics_advanced.py"
echo
echo "📍 /unified-analytics/* routes:"
grep -c "@router\." apps/api/routers/analytics_unified.py
echo "endpoints in analytics_unified.py"
echo

echo "9. ✅ DUPLICATE ANALYSIS SUMMARY:"
echo "================================="

# Check for actual conflicts
CONFLICTS_FOUND=0

echo "Route Prefix Conflicts:"
if [ $(grep "prefix=" apps/api/routers/analytics*.py | sort | uniq | wc -l) -eq $(grep "prefix=" apps/api/routers/analytics*.py | wc -l) ]; then
    echo "✅ No duplicate route prefixes found"
else
    echo "❌ Route prefix conflicts detected!"
    CONFLICTS_FOUND=1
fi

echo
echo "Component Name Conflicts:"
if [ $(find apps/frontend/src -name "*AdvancedAnalytics*.jsx" | wc -l) -eq 1 ] && [ $(find apps/frontend/src -name "*RealTimeAlerts*.jsx" | wc -l) -eq 1 ]; then
    echo "✅ No duplicate component files found"
else
    echo "❌ Duplicate component files detected!"
    CONFLICTS_FOUND=1
fi

echo
echo "API Client Method Conflicts:"
if [ $(grep -c "getAdvancedDashboard\|getRealTimeMetrics\|checkAlerts" apps/frontend/src/utils/apiClient.js) -eq 6 ]; then
    echo "✅ Advanced analytics methods properly added (6 methods found)"
else
    echo "⚠️  Unexpected number of advanced analytics methods"
fi

echo
echo "🎯 FINAL RESULT:"
if [ $CONFLICTS_FOUND -eq 0 ]; then
    echo "✅ NO DUPLICATES FOUND - Safe to proceed with deployment"
    echo "📊 Week 3-4 implementation is clean and conflict-free"
else
    echo "❌ CONFLICTS DETECTED - Review needed before deployment"
fi

echo
echo "🚀 Next Steps:"
echo "1. Restart API service to activate new endpoints"
echo "2. Restart frontend service for component updates"
echo "3. Test advanced analytics functionality"
echo "4. Verify real-time alerts system"
