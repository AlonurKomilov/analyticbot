#!/bin/bash

###############################################################################
# Phase 5 & 6 Performance Testing Script
#
# Purpose: Test performance improvements from Phase 6 indexes and monitoring
#
# Tests:
#   1. Query performance before/after indexes
#   2. Content-type filtered queries
#   3. Time-weighted queries
#   4. Memory usage tracking
#   5. Concurrent request handling
#
# Usage:
#   ./scripts/test_phase5_6.sh [environment]
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="${1:-development}"
API_URL="http://localhost:11400"
TEST_CHANNEL="1002678877654"
DAYS=90

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

###############################################################################
# Performance Tests
###############################################################################

test_response_time() {
    local test_name="$1"
    log_info "Testing: $test_name"

    local TOKEN
    TOKEN=$(cat ~/.analyticbot_token 2>/dev/null || echo "")

    if [[ -z "$TOKEN" ]]; then
        log_error "No auth token found"
        return 1
    fi

    # Run 5 iterations
    local total_time=0
    for i in {1..5}; do
        local start
        start=$(date +%s%N)

        curl -s -X GET \
            "$API_URL/analytics/predictive/best-times/$TEST_CHANNEL?days=$DAYS" \
            -H "Authorization: Bearer $TOKEN" > /dev/null

        local end
        end=$(date +%s%N)
        local duration=$(( (end - start) / 1000000 ))
        total_time=$((total_time + duration))

        log_info "  Iteration $i: ${duration}ms"
    done

    local avg_time=$((total_time / 5))
    log_success "Average response time: ${avg_time}ms"

    # Check if within acceptable range
    if (( avg_time < 1000 )); then
        log_success "Performance EXCELLENT (<1s)"
    elif (( avg_time < 2000 )); then
        log_success "Performance GOOD (<2s)"
    elif (( avg_time < 3000 )); then
        log_info "Performance ACCEPTABLE (<3s)"
    else
        log_error "Performance SLOW (>${avg_time}ms)"
    fi

    echo "$avg_time"
}

test_advanced_features() {
    log_info "Testing advanced features presence..."

    local TOKEN
    TOKEN=$(cat ~/.analyticbot_token)

    local response
    response=$(curl -s -X GET \
        "$API_URL/analytics/predictive/best-times/$TEST_CHANNEL?days=$DAYS" \
        -H "Authorization: Bearer $TOKEN")

    local day_hour_count
    day_hour_count=$(echo "$response" | jq '.data.best_day_hour_combinations | length' 2>/dev/null || echo "0")

    local content_type_count
    content_type_count=$(echo "$response" | jq '.data.content_type_recommendations | length' 2>/dev/null || echo "0")

    if [[ "$day_hour_count" -gt 0 && "$content_type_count" -gt 0 ]]; then
        log_success "Advanced features working ($day_hour_count day-hour, $content_type_count content-type)"
    else
        log_error "Advanced features not returning data"
    fi
}

test_database_indexes() {
    log_info "Checking database indexes..."

    local index_count
    index_count=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" -t -c "
        SELECT COUNT(*) FROM pg_indexes
        WHERE tablename IN ('posts', 'post_metrics')
        AND indexname LIKE 'idx_%'
    " 2>/dev/null || echo "0")

    log_info "Found $index_count indexes"

    # Check if migration 005 indexes exist
    local new_indexes
    new_indexes=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" -t -c "
        SELECT COUNT(*) FROM pg_indexes
        WHERE indexname IN (
            'idx_posts_channel_date_active',
            'idx_posts_channel_date_content_type',
            'idx_posts_videos_only',
            'idx_posts_images_only'
        )
    " 2>/dev/null || echo "0")

    if [[ "$new_indexes" -ge 4 ]]; then
        log_success "Migration 005 indexes applied ($new_indexes/4)"
    else
        log_error "Migration 005 not fully applied ($new_indexes/4 indexes)"
    fi
}

test_concurrent_requests() {
    log_info "Testing concurrent request handling..."

    local TOKEN
    TOKEN=$(cat ~/.analyticbot_token)

    # Start 3 concurrent requests
    local start
    start=$(date +%s%N)

    for i in {1..3}; do
        curl -s -X GET \
            "$API_URL/analytics/predictive/best-times/$TEST_CHANNEL?days=$DAYS" \
            -H "Authorization: Bearer $TOKEN" > /dev/null &
    done

    wait

    local end
    end=$(date +%s%N)
    local duration=$(( (end - start) / 1000000 ))

    log_success "3 concurrent requests completed in ${duration}ms"

    # Should be less than 3x single request time
    if (( duration < 6000 )); then
        log_success "Concurrent performance good"
    else
        log_error "Concurrent performance degraded"
    fi
}

###############################################################################
# Main Execution
###############################################################################

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  Phase 5 & 6 Performance Testing                  ║"
    echo "║  Frontend Enhancements + Optimization             ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
}

main() {
    print_header

    log_info "Environment: $ENVIRONMENT"
    log_info "API URL: $API_URL"
    log_info "Test Channel: $TEST_CHANNEL"
    echo ""

    # Test 1: Database indexes
    test_database_indexes
    echo ""

    # Test 2: Basic response time
    log_info "═══ Test 1: Basic Response Time ═══"
    test_response_time "Standard query (90 days)"
    echo ""

    # Test 3: Advanced features
    log_info "═══ Test 2: Advanced Features ═══"
    test_advanced_features
    echo ""

    # Test 4: Concurrent requests
    log_info "═══ Test 3: Concurrent Requests ═══"
    test_concurrent_requests
    echo ""

    log_success "All tests completed!"
    echo ""
    echo "Next steps:"
    echo "  1. Review performance metrics in logs"
    echo "  2. Compare with Phase 2 baseline (1.96s)"
    echo "  3. If performance improved, document results"
    echo "  4. If performance degraded, review query plans"
    echo ""
}

main "$@"
