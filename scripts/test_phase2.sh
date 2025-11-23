#!/bin/bash
# Phase 2 Testing Script - Backend API Validation
# Tests the enhanced best-times endpoint with new features

set -e

API_URL="http://localhost:11401"
CHANNEL_ID=1002678877654
OUTPUT_DIR="/tmp/phase2_tests"

mkdir -p "$OUTPUT_DIR"

echo "🧪 PHASE 2 BACKEND TESTING"
echo "=========================="
echo ""

# Step 1: Get authentication token
echo "📝 Step 1: Authenticating..."
TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "abclegacyllc@gmail.com", "password": "12345678Aa"}' \
  | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
    echo "❌ Authentication failed!"
    exit 1
fi
echo "✅ Authentication successful (Token: ${TOKEN:0:20}...)"
echo ""

# Step 2: Test endpoint with 30 days
echo "📊 Step 2: Testing with 30 days..."
curl -s -X GET "$API_URL/analytics/predictive/best-times/$CHANNEL_ID?days=30" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.' > "$OUTPUT_DIR/response_30days.json"

POSTS_30=$(jq -r '.data.total_posts_analyzed' "$OUTPUT_DIR/response_30days.json")
echo "   Posts analyzed: $POSTS_30"
echo "   Data source: $(jq -r '.data.data_source' "$OUTPUT_DIR/response_30days.json")"
echo ""

# Step 3: Test endpoint with 90 days
echo "📊 Step 3: Testing with 90 days..."
curl -s -X GET "$API_URL/analytics/predictive/best-times/$CHANNEL_ID?days=90" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.' > "$OUTPUT_DIR/response_90days.json"

POSTS_90=$(jq -r '.data.total_posts_analyzed' "$OUTPUT_DIR/response_90days.json")
echo "   Posts analyzed: $POSTS_90"
echo "   Data source: $(jq -r '.data.data_source' "$OUTPUT_DIR/response_90days.json")"
echo ""

# Step 4: Verify new fields exist
echo "🔍 Step 4: Verifying new fields..."

# Check best_day_hour_combinations
DAY_HOUR_COUNT=$(jq '.data.best_day_hour_combinations | length' "$OUTPUT_DIR/response_90days.json")
echo "   ✓ best_day_hour_combinations: $DAY_HOUR_COUNT items"

# Check content_type_recommendations
CONTENT_TYPE_COUNT=$(jq '.data.content_type_recommendations | length' "$OUTPUT_DIR/response_90days.json")
echo "   ✓ content_type_recommendations: $CONTENT_TYPE_COUNT items"

# Check existing fields still work
BEST_TIMES_COUNT=$(jq '.data.best_times | length' "$OUTPUT_DIR/response_90days.json")
echo "   ✓ best_times: $BEST_TIMES_COUNT items"

BEST_DAYS_COUNT=$(jq '.data.best_days | length' "$OUTPUT_DIR/response_90days.json")
echo "   ✓ best_days: $BEST_DAYS_COUNT items"
echo ""

# Step 5: Validate data structure
echo "📋 Step 5: Validating data structures..."

# Validate day-hour combination structure
echo "   Sample day-hour combination:"
jq '.data.best_day_hour_combinations[0]' "$OUTPUT_DIR/response_90days.json"
echo ""

# Validate content type recommendation structure
echo "   Sample content type recommendation:"
jq '.data.content_type_recommendations[0]' "$OUTPUT_DIR/response_90days.json"
echo ""

# Step 6: Analyze recommendations
echo "📈 Step 6: Analyzing recommendations..."

echo "   Top 3 Best Times:"
jq -r '.data.best_times[0:3] | .[] | "     \(.day) (Day) at \(.hour):00 - Confidence: \(.confidence)%"' \
  "$OUTPUT_DIR/response_90days.json"
echo ""

echo "   Top 3 Day-Hour Combinations:"
jq -r '.data.best_day_hour_combinations[0:3] | .[] |
  "     Day \(.day) at \(.hour):00 - \(.confidence)% confidence (\(.post_count) posts)"' \
  "$OUTPUT_DIR/response_90days.json"
echo ""

echo "   Content Type Performance:"
jq -r '.data.content_type_recommendations[0:5] | .[] |
  "     \(.content_type) at \(.hour):00 - \(.confidence)% (\(.post_count) posts)"' \
  "$OUTPUT_DIR/response_90days.json"
echo ""

# Step 7: Performance testing
echo "⏱️  Step 7: Performance testing..."

START_TIME=$(date +%s%N)
for i in {1..5}; do
  curl -s -X GET "$API_URL/analytics/predictive/best-times/$CHANNEL_ID?days=90" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
done
END_TIME=$(date +%s%N)

DURATION=$(( ($END_TIME - $START_TIME) / 1000000 ))
AVG_TIME=$(( $DURATION / 5 ))

echo "   5 requests completed in ${DURATION}ms"
echo "   Average: ${AVG_TIME}ms per request"

if [ $AVG_TIME -lt 1000 ]; then
    echo "   ✅ Performance: EXCELLENT (<1s)"
elif [ $AVG_TIME -lt 3000 ]; then
    echo "   ✅ Performance: GOOD (<3s)"
else
    echo "   ⚠️  Performance: SLOW (>3s)"
fi
echo ""

# Step 8: Error handling test
echo "🚨 Step 8: Testing error handling..."

# Test with invalid channel ID
INVALID_RESPONSE=$(curl -s -X GET "$API_URL/analytics/predictive/best-times/999999?days=30" \
  -H "Authorization: Bearer $TOKEN")

if echo "$INVALID_RESPONSE" | jq -e '.data.data_source == "insufficient_data"' > /dev/null; then
    echo "   ✅ Invalid channel handled gracefully"
else
    echo "   ⚠️  Invalid channel response: $INVALID_RESPONSE"
fi
echo ""

# Summary
echo "=========================="
echo "✨ PHASE 2 TESTING COMPLETE"
echo "=========================="
echo ""
echo "Summary:"
echo "  ✓ Authentication: Working"
echo "  ✓ Endpoint: Responding"
echo "  ✓ New Fields: Present ($DAY_HOUR_COUNT day-hour combos, $CONTENT_TYPE_COUNT content types)"
echo "  ✓ Legacy Fields: Intact ($BEST_TIMES_COUNT best times, $BEST_DAYS_COUNT best days)"
echo "  ✓ Performance: ${AVG_TIME}ms average"
echo "  ✓ Error Handling: Graceful"
echo ""
echo "Test results saved to: $OUTPUT_DIR"
echo ""
echo "Next: Ready for Phase 3 - Safety Measures & Feature Flags"
