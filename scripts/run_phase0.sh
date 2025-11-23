#!/bin/bash
# scripts/run_phase0.sh
# Execute all Phase 0 analysis steps

cd /home/abcdeveloper/projects/analyticbot

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    API RESTRUCTURE - PHASE 0 EXECUTION                     ║"
echo "║                         Option A: Flat Resources                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Create reports directory
mkdir -p reports

# Check if API is running
echo "🔍 Checking if API server is running..."
if curl -s http://localhost:11400/health/ > /dev/null 2>&1; then
    echo "✅ API server is running"
else
    echo "❌ API server is not running"
    echo "⚠️  Please start the API server first: make dev"
    echo ""
    read -p "Press Enter to continue anyway (will skip Step 1) or Ctrl+C to exit..."
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "STEP 1: Analyze Current API Structure"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

if curl -s http://localhost:11400/health/ > /dev/null 2>&1; then
    python3 scripts/phase0_analyze_current_structure.py
    if [ $? -eq 0 ]; then
        echo "✅ Step 1 completed successfully"
    else
        echo "❌ Step 1 failed"
        exit 1
    fi
else
    echo "⚠️  Skipping Step 1 (API not running)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "STEP 2: Analyze API Usage from Logs"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

python3 scripts/phase0_analyze_usage.py
if [ $? -eq 0 ]; then
    echo "✅ Step 2 completed successfully"
else
    echo "❌ Step 2 failed"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "STEP 3: Analyze Frontend API Calls"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

./scripts/phase0_analyze_frontend.sh
if [ $? -eq 0 ]; then
    echo "✅ Step 3 completed successfully"
else
    echo "❌ Step 3 failed"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "STEP 4: Create Migration Map"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f "reports/openapi_current.json" ]; then
    python3 scripts/phase0_create_migration_map.py
    if [ $? -eq 0 ]; then
        echo "✅ Step 4 completed successfully"
    else
        echo "❌ Step 4 failed"
        exit 1
    fi
else
    echo "⚠️  Skipping Step 4 (openapi_current.json not found)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                         PHASE 0 ANALYSIS COMPLETE                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Generated Reports:"
echo "══════════════════════════════════════════════════════════════════════════"

if [ -f "reports/openapi_current.json" ]; then
    echo "✅ reports/openapi_current.json            - Current OpenAPI spec"
fi
if [ -f "reports/phase0_current_structure.txt" ]; then
    ENDPOINTS=$(grep "Total Endpoints:" reports/phase0_current_structure.txt | awk '{print $3}')
    PREFIXES=$(grep "Total Prefix Groups:" reports/phase0_current_structure.txt | awk '{print $4}')
    echo "✅ reports/phase0_current_structure.txt    - $ENDPOINTS endpoints, $PREFIXES prefixes"
fi
if [ -f "reports/phase0_issues.txt" ]; then
    ISSUES=$(wc -l < reports/phase0_issues.txt)
    echo "✅ reports/phase0_issues.txt               - $ISSUES issues detected"
fi
if [ -f "reports/phase0_endpoint_usage.txt" ]; then
    REQUESTS=$(grep "Total API Requests:" reports/phase0_endpoint_usage.txt | awk '{print $4}')
    echo "✅ reports/phase0_endpoint_usage.txt       - $REQUESTS requests analyzed"
fi
if [ -f "reports/phase0_frontend_api_calls.txt" ]; then
    echo "✅ reports/phase0_frontend_api_calls.txt   - Frontend API calls"
fi
if [ -f "reports/phase0_frontend_endpoints.txt" ]; then
    FE_ENDPOINTS=$(wc -l < reports/phase0_frontend_endpoints.txt)
    echo "✅ reports/phase0_frontend_endpoints.txt   - $FE_ENDPOINTS unique endpoints"
fi
if [ -f "reports/phase0_migration_map.json" ]; then
    echo "✅ reports/phase0_migration_map.json       - Migration map (JSON)"
fi
if [ -f "reports/phase0_migration_map.txt" ]; then
    echo "✅ reports/phase0_migration_map.txt        - Migration map (readable)"
fi

echo ""
echo "📋 Next Steps:"
echo "══════════════════════════════════════════════════════════════════════════"
echo "1. Review the migration map:     cat reports/phase0_migration_map.txt"
echo "2. Check detected issues:        cat reports/phase0_issues.txt"
echo "3. Review most-used endpoints:   head -20 reports/phase0_endpoint_usage.txt"
echo "4. Proceed to Step 5:            See docs/API_RESTRUCTURE_PHASE_0_PREPARATION.md"
echo ""
echo "⚠️  IMPORTANT: Review all reports before proceeding to Phase 1!"
echo ""
