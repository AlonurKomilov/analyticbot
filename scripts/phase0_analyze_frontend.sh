#!/bin/bash
# scripts/phase0_analyze_frontend.sh

cd /home/abcdeveloper/projects/analyticbot

echo "=============================================="
echo "🔍 PHASE 0: ANALYZING FRONTEND API CALLS"
echo "=============================================="

# Create reports directory
mkdir -p docs/reports

echo ""
echo "📂 Scanning frontend files..."

# Find all files that might contain API calls
find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -exec grep -l "fetch\|axios\|api\." {} \; 2>/dev/null > docs/reports/files_with_api_calls.txt

FILES_COUNT=$(wc -l < docs/reports/files_with_api_calls.txt)
echo "✅ Found $FILES_COUNT files with API calls"

echo ""
echo "🔎 Extracting API endpoint patterns..."

# Extract all API endpoint patterns
{
  echo "=============================================="
  echo "FRONTEND API CALLS ANALYSIS"
  echo "=============================================="
  echo ""

  # Look for fetch calls
  echo "FETCH CALLS:"
  echo "----------------------------------------------"
  find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
    -exec grep -h "fetch(" {} \; 2>/dev/null | \
    grep -oE "fetch\(['\"\`][^'\"\`]+" | \
    sed "s/fetch(['\"\`]//" | \
    sort | uniq

  echo ""
  echo ""

  # Look for axios calls
  echo "AXIOS CALLS:"
  echo "----------------------------------------------"
  find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
    -exec grep -h "axios\." {} \; 2>/dev/null | \
    grep -oE "axios\.(get|post|put|delete|patch)\(['\"\`][^'\"\`]+" | \
    sed "s/axios\.(get|post|put|delete|patch)(['\"\`]/\U\1 /" | \
    sort | uniq

  echo ""
  echo ""

  # Look for API base URLs
  echo "API BASE URLS:"
  echo "----------------------------------------------"
  find apps/frontend/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
    -exec grep -h "API_BASE\|API_URL\|baseURL\|VITE_API" {} \; 2>/dev/null | \
    grep -v "^//" | \
    head -20

} > docs/reports/phase0_frontend_api_calls.txt

echo "✅ Report saved to docs/reports/phase0_frontend_api_calls.txt"

echo ""
echo "🔍 Extracting unique endpoint paths..."

# Extract just the endpoint paths
grep -rh "fetch\|axios" apps/frontend/src 2>/dev/null | \
  grep -oE "['\"\`]/(api/)?[a-z-]+/[^'\"\`]*['\"\`]" | \
  tr -d "'\"\`" | \
  sort | uniq > docs/reports/phase0_frontend_endpoints.txt

ENDPOINTS_COUNT=$(wc -l < docs/reports/phase0_frontend_endpoints.txt)
echo "✅ Found $ENDPOINTS_COUNT unique endpoint patterns"
echo "✅ Saved to docs/reports/phase0_frontend_endpoints.txt"

echo ""
echo "=============================================="
echo "✅ FRONTEND ANALYSIS COMPLETE"
echo "=============================================="
echo ""
echo "Generated files:"
echo "  - docs/reports/files_with_api_calls.txt ($FILES_COUNT files)"
echo "  - docs/reports/phase0_frontend_api_calls.txt"
echo "  - docs/reports/phase0_frontend_endpoints.txt ($ENDPOINTS_COUNT endpoints)"
echo ""
echo "Next: Run Step 4 to create migration map"
echo "      python3 scripts/phase0_create_migration_map.py"
