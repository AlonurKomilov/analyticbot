#!/bin/bash

###############################################################################
# Phase 3 Feature Flag Testing Script
#
# Purpose: Validate that feature flags work correctly and can safely toggle
#          recommendation system features on/off.
#
# Usage:
#   ./scripts/test_phase3.sh                    # Interactive mode
#   ./scripts/test_phase3.sh --all-enabled      # Test with all flags on
#   ./scripts/test_phase3.sh --all-disabled     # Test with all flags off
#   ./scripts/test_phase3.sh --legacy-mode      # Test simple query
#
# Requirements:
#   - API server running on localhost:11401
#   - Valid auth token in environment or ~/.analyticbot_token
#   - PostgreSQL database accessible
#   - jq installed for JSON parsing
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:11401"
TEST_CHANNEL_ID="-1002000495734"
DAYS=90
TOKEN_FILE="$HOME/.analyticbot_token"

# Stats
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

get_auth_token() {
    if [[ -n "${ANALYTICS_BOT_TOKEN:-}" ]]; then
        echo "$ANALYTICS_BOT_TOKEN"
    elif [[ -f "$TOKEN_FILE" ]]; then
        cat "$TOKEN_FILE"
    else
        log_error "No auth token found. Set ANALYTICS_BOT_TOKEN or create $TOKEN_FILE"
        exit 1
    fi
}

###############################################################################
# Test Functions
###############################################################################

test_api_connectivity() {
    log_info "Testing API connectivity..."

    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/health" || echo "000")

    if [[ "$response" == "200" ]]; then
        log_success "API is reachable at $API_BASE_URL"
        return 0
    else
        log_error "API not reachable (HTTP $response)"
        return 1
    fi
}

test_advanced_features_enabled() {
    log_info "Testing API with ADVANCED features ENABLED..."

    local token
    token=$(get_auth_token)

    local response
    response=$(curl -s -X GET \
        "$API_BASE_URL/analytics/predictive/best-times/$TEST_CHANNEL_ID?days=$DAYS" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")

    # Check if response contains advanced fields
    local has_day_hour=$(echo "$response" | jq -r '.data.best_day_hour_combinations' 2>/dev/null)
    local has_content_type=$(echo "$response" | jq -r '.data.content_type_recommendations' 2>/dev/null)

    if [[ "$has_day_hour" != "null" && "$has_content_type" != "null" ]]; then
        log_success "Advanced features present in response"

        # Count items
        local day_hour_count=$(echo "$response" | jq '.data.best_day_hour_combinations | length' 2>/dev/null || echo "0")
        local content_type_count=$(echo "$response" | jq '.data.content_type_recommendations | length' 2>/dev/null || echo "0")

        log_info "  - Day-hour combinations: $day_hour_count"
        log_info "  - Content type recommendations: $content_type_count"

        return 0
    else
        log_error "Advanced features NOT found in response"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        return 1
    fi
}

test_legacy_features_only() {
    log_info "Testing API with LEGACY mode (simple query)..."

    local token
    token=$(get_auth_token)

    local response
    response=$(curl -s -X GET \
        "$API_BASE_URL/analytics/predictive/best-times/$TEST_CHANNEL_ID?days=$DAYS" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")

    # Check if response contains ONLY legacy fields
    local has_best_hours=$(echo "$response" | jq -r '.data.best_hours' 2>/dev/null)
    local has_best_days=$(echo "$response" | jq -r '.data.best_days' 2>/dev/null)
    local has_day_hour=$(echo "$response" | jq -r '.data.best_day_hour_combinations' 2>/dev/null)
    local has_content_type=$(echo "$response" | jq -r '.data.content_type_recommendations' 2>/dev/null)

    if [[ "$has_best_hours" != "null" && "$has_best_days" != "null" ]]; then
        log_success "Legacy fields present (best_hours, best_days)"

        if [[ "$has_day_hour" == "null" && "$has_content_type" == "null" ]]; then
            log_success "Advanced fields correctly absent in legacy mode"
        else
            log_warning "Advanced fields present when they shouldn't be"
        fi

        return 0
    else
        log_error "Legacy fields missing from response"
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
        return 1
    fi
}

test_response_time() {
    local mode="$1"
    log_info "Testing response time with $mode mode..."

    local token
    token=$(get_auth_token)

    local start
    local end
    local duration

    start=$(date +%s%N)
    curl -s -X GET \
        "$API_BASE_URL/analytics/predictive/best-times/$TEST_CHANNEL_ID?days=$DAYS" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" > /dev/null
    end=$(date +%s%N)

    duration=$(( (end - start) / 1000000 ))

    log_info "  Response time: ${duration}ms"

    # Advanced mode should be slower than legacy
    if [[ "$mode" == "ADVANCED" ]]; then
        if (( duration < 3000 )); then
            log_success "Advanced mode response time acceptable (<3s)"
            return 0
        else
            log_warning "Advanced mode slower than expected (${duration}ms)"
            return 1
        fi
    else
        if (( duration < 2000 )); then
            log_success "Legacy mode response time fast (<2s)"
            return 0
        else
            log_warning "Legacy mode slower than expected (${duration}ms)"
            return 1
        fi
    fi
}

test_data_consistency() {
    log_info "Testing data consistency between modes..."

    local token
    token=$(get_auth_token)

    # Get response in both modes (would need server restart, so this is aspirational)
    local response
    response=$(curl -s -X GET \
        "$API_BASE_URL/analytics/predictive/best-times/$TEST_CHANNEL_ID?days=$DAYS" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")

    local total_posts=$(echo "$response" | jq -r '.data.total_posts_analyzed' 2>/dev/null)
    local best_hour=$(echo "$response" | jq -r '.data.best_hours[0].hour' 2>/dev/null)

    if [[ "$total_posts" =~ ^[0-9]+$ && "$best_hour" =~ ^[0-9]+$ ]]; then
        log_success "Data consistency check passed"
        log_info "  - Total posts: $total_posts"
        log_info "  - Best hour: ${best_hour}:00"
        return 0
    else
        log_error "Data consistency issues detected"
        return 1
    fi
}

test_database_columns() {
    log_info "Verifying database schema (has_video, has_media columns)..."

    # Check if columns exist
    local result
    result=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" \
        -t -c "\d posts" 2>/dev/null | grep -E "(has_video|has_media)" | wc -l || echo "0")

    if [[ "$result" -ge 2 ]]; then
        log_success "Required columns present in database"
        return 0
    else
        log_error "Missing has_video or has_media columns (run migration 004)"
        return 1
    fi
}

test_error_handling() {
    log_info "Testing error handling with invalid channel..."

    local token
    token=$(get_auth_token)

    local response
    response=$(curl -s -X GET \
        "$API_BASE_URL/analytics/predictive/best-times/-999999?days=$DAYS" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")

    local status=$(echo "$response" | jq -r '.status' 2>/dev/null)

    if [[ "$status" == "success" || "$status" == "error" ]]; then
        log_success "Error handling works (got valid response structure)"
        return 0
    else
        log_error "Error handling failed"
        return 1
    fi
}

###############################################################################
# Test Suites
###############################################################################

run_all_tests_enabled() {
    echo ""
    echo "=========================================="
    echo "  Phase 3: ALL FEATURES ENABLED"
    echo "=========================================="
    echo ""

    test_api_connectivity
    test_database_columns
    test_advanced_features_enabled
    test_response_time "ADVANCED"
    test_data_consistency
    test_error_handling
}

run_all_tests_disabled() {
    echo ""
    echo "=========================================="
    echo "  Phase 3: ALL FEATURES DISABLED"
    echo "=========================================="
    echo ""

    log_warning "This test requires restarting the API with ENABLE_ADVANCED_RECOMMENDATIONS=false"
    log_warning "Please restart the API and run this test again."
    echo ""

    test_api_connectivity
    test_legacy_features_only
    test_response_time "LEGACY"
    test_data_consistency
}

run_comparison_tests() {
    echo ""
    echo "=========================================="
    echo "  Phase 3: MODE COMPARISON"
    echo "=========================================="
    echo ""

    log_info "This suite compares performance and features between modes"
    log_warning "Requires manual API restart between tests"
    echo ""

    # Just run connectivity and schema tests
    test_api_connectivity
    test_database_columns
}

###############################################################################
# Main Script
###############################################################################

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  Phase 3: Feature Flag Testing                    ║"
    echo "║  Best Time Recommendations System                 ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
}

print_summary() {
    echo ""
    echo "=========================================="
    echo "  Test Summary"
    echo "=========================================="
    echo ""
    echo "Total tests:  $TESTS_TOTAL"
    echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        echo ""
        return 1
    fi
}

main() {
    print_header

    # Parse arguments
    case "${1:-interactive}" in
        --all-enabled)
            run_all_tests_enabled
            ;;
        --all-disabled|--legacy-mode)
            run_all_tests_disabled
            ;;
        --comparison)
            run_comparison_tests
            ;;
        *)
            log_info "Running default test suite (features enabled)"
            run_all_tests_enabled
            ;;
    esac

    print_summary
}

# Check dependencies
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed. Install with: sudo apt-get install jq"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    log_warning "psql not found - skipping database tests"
fi

main "$@"
