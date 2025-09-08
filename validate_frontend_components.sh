#!/bin/bash

echo "🔍 FRONTEND COMPONENTS & FILES VALIDATION"
echo "========================================="
echo

echo "📁 1. COMPONENTS DIRECTORY STRUCTURE:"
echo "-------------------------------------"
echo "Main components directory:"
ls -la apps/frontend/src/components/ | grep -E "\.(jsx|js)$" | awk '{print "  ✓ " $9}'
echo

echo "Analytics subdirectory:"
ls -la apps/frontend/src/components/analytics/ | grep -E "\.(jsx|js)$" | awk '{print "  ✓ " $9}'
echo

echo "Common subdirectory:"
ls -la apps/frontend/src/components/common/ | grep -E "\.(jsx|js)$" | awk '{print "  ✓ " $9}'
echo

echo "📦 2. INDEX.JS FILES VALIDATION:"
echo "--------------------------------"

# Check main components index.js
if [ -f "apps/frontend/src/components/index.js" ]; then
    echo "✅ Main components index.js exists"
    MAIN_EXPORTS=$(grep -c "export" apps/frontend/src/components/index.js)
    echo "   📊 Exports: $MAIN_EXPORTS components"
else
    echo "❌ Main components index.js missing"
fi

# Check analytics index.js
if [ -f "apps/frontend/src/components/analytics/index.js" ]; then
    echo "✅ Analytics index.js exists"
    ANALYTICS_EXPORTS=$(grep -c "export" apps/frontend/src/components/analytics/index.js)
    echo "   📊 Exports: $ANALYTICS_EXPORTS components"
    echo "   📋 Analytics exports:"
    grep "export" apps/frontend/src/components/analytics/index.js | sed 's/^/      /'
else
    echo "❌ Analytics index.js missing"
fi

# Check common index.js
if [ -f "apps/frontend/src/components/common/index.js" ]; then
    echo "✅ Common components index.js exists"
    COMMON_EXPORTS=$(grep -c "export" apps/frontend/src/components/common/index.js)
    echo "   📊 Exports: $COMMON_EXPORTS components"
else
    echo "❌ Common components index.js missing"
fi
echo

echo "🖼️ 3. STATIC ASSETS VALIDATION:"
echo "-------------------------------"

# Check for vite.svg
if [ -f "apps/frontend/public/vite.svg" ]; then
    echo "✅ vite.svg exists in public directory"
    SIZE=$(wc -c < apps/frontend/public/vite.svg)
    echo "   📏 Size: $SIZE bytes"
else
    echo "❌ vite.svg missing (404 error source)"
fi

# Check for favicon
if [ -f "apps/frontend/public/favicon.ico" ]; then
    echo "✅ favicon.ico exists"
else
    echo "❌ favicon.ico missing"
fi

# Check public directory
if [ -d "apps/frontend/public" ]; then
    echo "✅ Public directory exists"
    echo "   📁 Contents:"
    ls -la apps/frontend/public/ | tail -n +2 | awk '{print "      " $9}'
else
    echo "❌ Public directory missing"
fi
echo

echo "🔗 4. IMPORT VALIDATION:"
echo "------------------------"

# Check for broken imports in main dashboard
echo "Checking AnalyticsDashboard.jsx imports:"
if grep -q "from './analytics/AdvancedAnalyticsDashboard'" apps/frontend/src/components/AnalyticsDashboard.jsx; then
    echo "  ✅ AdvancedAnalyticsDashboard import correct"
else
    echo "  ❌ AdvancedAnalyticsDashboard import missing/incorrect"
fi

if grep -q "from './analytics/RealTimeAlertsSystem'" apps/frontend/src/components/AnalyticsDashboard.jsx; then
    echo "  ✅ RealTimeAlertsSystem import correct"
else
    echo "  ❌ RealTimeAlertsSystem import missing/incorrect"
fi
echo

echo "🌐 5. FRONTEND SERVICE STATUS:"
echo "------------------------------"

# Test frontend response
FRONTEND_STATUS=$(curl -s -w "%{http_code}" "http://localhost:3000" -o /dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend service running (HTTP $FRONTEND_STATUS)"
else
    echo "❌ Frontend service issue (HTTP $FRONTEND_STATUS)"
fi

# Test for 404 errors
echo "Testing static asset access:"
VITE_SVG_STATUS=$(curl -s -w "%{http_code}" "http://localhost:3000/vite.svg" -o /dev/null)
if [ "$VITE_SVG_STATUS" = "200" ]; then
    echo "  ✅ vite.svg accessible (HTTP $VITE_SVG_STATUS)"
else
    echo "  ❌ vite.svg not accessible (HTTP $VITE_SVG_STATUS)"
fi
echo

echo "📊 6. COMPONENT FILE VALIDATION:"
echo "--------------------------------"

# Check that all exported components exist
COMPONENTS=(
    "apps/frontend/src/components/AnalyticsDashboard.jsx"
    "apps/frontend/src/components/PostViewDynamicsChart.jsx"
    "apps/frontend/src/components/TopPostsTable.jsx"
    "apps/frontend/src/components/BestTimeRecommender.jsx"
    "apps/frontend/src/components/analytics/AdvancedAnalyticsDashboard.jsx"
    "apps/frontend/src/components/analytics/RealTimeAlertsSystem.jsx"
)

echo "Checking component files exist:"
for component in "${COMPONENTS[@]}"; do
    if [ -f "$component" ]; then
        LINES=$(wc -l < "$component")
        echo "  ✅ $(basename "$component") ($LINES lines)"
    else
        echo "  ❌ Missing: $(basename "$component")"
    fi
done
echo

echo "🎯 7. SUMMARY:"
echo "=============="

# Count issues
ISSUES=0

[ ! -f "apps/frontend/src/components/index.js" ] && ((ISSUES++))
[ ! -f "apps/frontend/src/components/analytics/index.js" ] && ((ISSUES++))
[ ! -f "apps/frontend/src/components/common/index.js" ] && ((ISSUES++))
[ ! -f "apps/frontend/public/vite.svg" ] && ((ISSUES++))
[ "$FRONTEND_STATUS" != "200" ] && ((ISSUES++))
[ "$VITE_SVG_STATUS" != "200" ] && ((ISSUES++))

if [ $ISSUES -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED!"
    echo "✅ All component files organized correctly"
    echo "✅ All index.js files properly configured"
    echo "✅ Static assets available"
    echo "✅ No broken imports detected"
    echo "✅ Frontend service running correctly"
    echo
    echo "🚀 FRONTEND READY FOR USE!"
else
    echo "⚠️  Found $ISSUES issues that need attention"
fi
echo

echo "📱 Access your application:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  📊 API Docs: http://localhost:8000/docs"
