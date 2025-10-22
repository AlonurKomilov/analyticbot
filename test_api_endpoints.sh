#!/bin/bash

# Frontend API Integration Test Script
# Tests orchestrator endpoints with proper formatting

BASE_URL="${API_BASE_URL:-http://localhost:11400}"
TEST_CHANNEL_ID="12345"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   FRONTEND API INTEGRATION TEST - Orchestrator Endpoints  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}�� Base URL: ${BASE_URL}${NC}"
echo -e "${CYAN}📍 Test Channel ID: ${TEST_CHANNEL_ID}${NC}\n"

# Test counter
TOTAL=0
PASSED=0
FAILED=0

test_endpoint() {
    local METHOD=$1
    local ENDPOINT=$2
    local AUTH=$3
    local DATA=$4
    local DESCRIPTION=$5

    TOTAL=$((TOTAL + 1))
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Test ${TOTAL}: ${DESCRIPTION}${NC}"
    echo -e "${YELLOW}${METHOD} ${ENDPOINT}${NC}"

    if [ "$AUTH" = "true" ]; then
        echo -e "${YELLOW}🔐 Auth: Required (will test without token - expecting 403)${NC}"
    else
        echo -e "${YELLOW}🔓 Auth: Not required${NC}"
    fi

    # Make request
    if [ "$METHOD" = "GET" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}${ENDPOINT}" 2>&1)
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}${ENDPOINT}" \
            -H "Content-Type: application/json" \
            -d "${DATA}" 2>&1)
    fi

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    # Check result
    if [ "$AUTH" = "true" ]; then
        # Expecting 401 for auth-required endpoints
        if [ "$HTTP_CODE" = "403" ]; then
            echo -e "${GREEN}✅ PASS - Correctly returns 403 Unauthorized${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}❌ FAIL - Expected 403, got ${HTTP_CODE}${NC}"
            echo -e "${RED}Response: ${BODY:0:200}${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        # Expecting 200 for non-auth endpoints
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✅ PASS - Status: ${HTTP_CODE}${NC}"
            echo -e "${GREEN}Response: ${BODY:0:200}...${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}❌ FAIL - Status: ${HTTP_CODE}${NC}"
            echo -e "${RED}Response: ${BODY:0:200}${NC}"
            FAILED=$((FAILED + 1))
        fi
    fi
}

# ==========================================
# PREDICTIVE ANALYTICS API TESTS
# ==========================================

echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  PREDICTIVE ANALYTICS API TESTS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

test_endpoint "GET" \
    "/insights/predictive/intelligence/health" \
    "false" \
    "" \
    "Predictive Health Check (No Auth)"

test_endpoint "POST" \
    "/insights/predictive/forecast" \
    "true" \
    '{"channel_ids":[12345],"prediction_type":"engagement","forecast_days":7,"confidence_level":0.95}' \
    "Generate Forecast (Auth Required)"

test_endpoint "POST" \
    "/insights/predictive/intelligence/contextual" \
    "true" \
    '{"channel_id":12345,"intelligence_context":["temporal","environmental"],"analysis_period_days":30,"prediction_horizon_days":7}' \
    "Contextual Intelligence (Auth Required)"

test_endpoint "GET" \
    "/insights/predictive/intelligence/temporal/${TEST_CHANNEL_ID}?analysis_depth=comprehensive" \
    "true" \
    "" \
    "Temporal Patterns (Auth Required)"

test_endpoint "POST" \
    "/insights/predictive/intelligence/cross-channel" \
    "true" \
    '{"channel_ids":[12345],"analysis_dimensions":["engagement","content"],"comparison_period_days":30}' \
    "Cross-Channel Intelligence (Auth Required)"

# ==========================================
# ALERTS API TESTS
# ==========================================

echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  ALERTS API TESTS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

test_endpoint "GET" \
    "/analytics/alerts/health" \
    "false" \
    "" \
    "Alerts Health Check (No Auth)"

test_endpoint "GET" \
    "/analytics/alerts/stats" \
    "false" \
    "" \
    "Alerts Stats (No Auth)"

test_endpoint "GET" \
    "/analytics/alerts/monitor/live/${TEST_CHANNEL_ID}?hours=6" \
    "true" \
    "" \
    "Live Monitoring (Auth Required)"

test_endpoint "POST" \
    "/analytics/alerts/check/${TEST_CHANNEL_ID}?analysis_type=comprehensive" \
    "true" \
    '{}' \
    "Check Alerts (Auth Required)"

test_endpoint "POST" \
    "/analytics/alerts/competitive/monitor" \
    "true" \
    '{"channel_id":12345,"monitoring_period_days":7,"include_competitor_analysis":true}' \
    "Competitive Monitoring (Auth Required)"

test_endpoint "POST" \
    "/analytics/alerts/workflow/comprehensive/${TEST_CHANNEL_ID}?include_competitive=true" \
    "true" \
    '{}' \
    "Comprehensive Workflow (Auth Required)"

# ==========================================
# TEST SUMMARY
# ==========================================

echo -e "\n${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  TEST SUMMARY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${CYAN}Total Tests: ${TOTAL}${NC}"
echo -e "${GREEN}✅ Passed: ${PASSED}${NC}"
echo -e "${RED}❌ Failed: ${FAILED}${NC}"

PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")
echo -e "\n${CYAN}📊 Pass Rate: ${PASS_RATE}%${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the results above.${NC}\n"
    exit 1
fi
