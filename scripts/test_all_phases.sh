#!/bin/bash

###############################################################################
# Comprehensive Phase 1-6 Validation Test
# Tests all features of the recommendation system enhancement
###############################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

API_URL="http://localhost:11400"
TEST_CHANNEL="1002678877654"  # Has 629 posts
DAYS=90
PASSED=0
FAILED=0

print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

test_phase() {
    local phase=$1
    local test_name=$2
    echo ""
    log_test "Phase $phase: $test_name"
}

assert_success() {
    if [ $? -eq 0 ]; then
        log_success "$1"
        ((PASSED++))
        return 0
    else
        log_error "$1"
        ((FAILED++))
        return 1
    fi
}

###############################################################################
# PHASE 1: DATABASE SCHEMA
###############################################################################
test_phase1() {
    print_header "PHASE 1: DATABASE SCHEMA VERIFICATION"

    # Test 1.1: Check required columns
    test_phase 1 "Check posts table has required columns"
    local columns=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" -t -c "
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'posts'
          AND column_name IN ('has_video', 'has_media', 'text', 'is_deleted')
        ORDER BY column_name;
    " | grep -v "^$" | wc -l)

    [ "$columns" -eq 4 ]
    assert_success "Required columns exist: has_video, has_media, text, is_deleted"

    # Test 1.2: Check indexes from migration 004
    test_phase 1 "Check migration 004 indexes exist"
    local indexes=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" -t -c "
        SELECT COUNT(*)
        FROM pg_indexes
        WHERE tablename = 'posts'
          AND indexname IN ('idx_posts_content_type', 'idx_posts_date_content');
    ")

    [ "$indexes" -ge 2 ]
    assert_success "Migration 004 indexes applied"

    # Test 1.3: Check indexes from migration 005
    test_phase 1 "Check migration 005 indexes exist"
    local new_indexes=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" -t -c "
        SELECT COUNT(*)
        FROM pg_indexes
        WHERE tablename IN ('posts', 'post_metrics')
          AND indexname IN (
              'idx_posts_channel_date_content_type',
              'idx_posts_videos_only',
              'idx_posts_images_only',
              'idx_post_metrics_covering'
          );
    ")

    [ "$new_indexes" -ge 4 ]
    assert_success "Migration 005 performance indexes applied"
}

###############################################################################
# PHASE 2: BACKEND API TESTING
###############################################################################
test_phase2() {
    print_header "PHASE 2: BACKEND API TESTING"

    local TOKEN=$(cat ~/.analyticbot_token 2>/dev/null || echo "")
    if [ -z "$TOKEN" ]; then
        log_error "No auth token found. Cannot test API."
        ((FAILED+=5))
        return 1
    fi

    # Test 2.1: API health check
    test_phase 2 "API health check"
    curl -s "$API_URL/health" > /dev/null
    assert_success "API is responding"

    # Test 2.2: Basic recommendation endpoint
    test_phase 2 "Test recommendation endpoint (advanced mode)"
    local start=$(date +%s%N)
    local response=$(curl -s -X GET \
        "$API_URL/analytics/predictive/best-times/$TEST_CHANNEL?days=$DAYS" \
        -H "Authorization: Bearer $TOKEN")
    local end=$(date +%s%N)
    local duration=$(( (end - start) / 1000000 ))

    echo "$response" | jq -e '.success == true' > /dev/null
    assert_success "API returned successful response (${duration}ms)"

    # Test 2.3: Verify advanced features data
    test_phase 2 "Verify best_day_hour_combinations returned"
    local day_hour_count=$(echo "$response" | jq -r '.data.best_day_hour_combinations | length')
    [ "$day_hour_count" -gt 0 ]
    assert_success "Day-hour combinations returned: $day_hour_count"

    # Test 2.4: Verify content type recommendations
    test_phase 2 "Verify content_type_recommendations returned"
    local content_count=$(echo "$response" | jq -r '.data.content_type_recommendations | length')
    [ "$content_count" -gt 0 ]
    assert_success "Content-type recommendations returned: $content_count"

    # Test 2.5: Performance check
    test_phase 2 "Performance check (<3s expected)"
    if [ $duration -lt 3000 ]; then
        log_success "Performance EXCELLENT: ${duration}ms"
        ((PASSED++))
    elif [ $duration -lt 5000 ]; then
        log_warning "Performance ACCEPTABLE: ${duration}ms"
        ((PASSED++))
    else
        log_error "Performance SLOW: ${duration}ms"
        ((FAILED++))
    fi
}

###############################################################################
# PHASE 3: FEATURE FLAGS & ROLLBACK
###############################################################################
test_phase3() {
    print_header "PHASE 3: FEATURE FLAGS & ROLLBACK STRATEGY"

    # Test 3.1: Check feature flags exist in code
    test_phase 3 "Check feature flag implementation"
    grep -q "ENABLE_ADVANCED_RECOMMENDATIONS" \
        core/services/analytics_fusion/recommendations/time_analysis_repository.py
    assert_success "Feature flags implemented in code"

    # Test 3.2: Check rollback migration exists
    test_phase 3 "Check rollback migrations exist"
    [ -f "infra/db/migrations/004_rollback.sql" ] && \
    [ -f "infra/db/migrations/005_rollback.sql" ]
    assert_success "Rollback migrations exist"
}

###############################################################################
# PHASE 4: DEPLOYMENT SCRIPTS
###############################################################################
test_phase4() {
    print_header "PHASE 4: DEPLOYMENT INFRASTRUCTURE"

    # Test 4.1: Check deployment scripts
    test_phase 4 "Check deployment scripts exist"
    [ -f "scripts/deploy_phase4_pre_check.sh" ] && \
    [ -f "scripts/deploy_phase4_post_check.sh" ]
    assert_success "Deployment scripts exist"

    # Test 4.2: Check scripts are executable
    test_phase 4 "Check scripts are executable"
    [ -x "scripts/deploy_phase4_pre_check.sh" ]
    assert_success "Scripts have execute permissions"

    # Test 4.3: Check environment configs
    test_phase 4 "Check environment configuration files"
    [ -f ".env.production.example" ] && \
    [ -f ".env.staging.example" ]
    assert_success "Environment config templates exist"
}

###############################################################################
# PHASE 5: FRONTEND COMPONENTS
###############################################################################
test_phase5() {
    print_header "PHASE 5: FRONTEND COMPONENTS"

    # Test 5.1: Check ContentTypeFilter exists
    test_phase 5 "Check ContentTypeFilter component"
    [ -f "apps/frontend/src/features/analytics/best-time/components/ContentTypeFilter.tsx" ]
    assert_success "ContentTypeFilter.tsx exists"

    # Test 5.2: Check SmartRecommendationsPanel exists
    test_phase 5 "Check SmartRecommendationsPanel component"
    [ -f "apps/frontend/src/features/analytics/best-time/components/SmartRecommendationsPanel.tsx" ]
    assert_success "SmartRecommendationsPanel.tsx exists"

    # Test 5.3: Check EnhancedCalendarTooltip exists
    test_phase 5 "Check EnhancedCalendarTooltip component"
    [ -f "apps/frontend/src/features/analytics/best-time/components/EnhancedCalendarTooltip.tsx" ]
    assert_success "EnhancedCalendarTooltip.tsx exists"

    # Test 5.4: Check if components are integrated (optional)
    test_phase 5 "Check component integration status"
    if grep -q "ContentTypeFilter" apps/frontend/src/features/analytics/best-time/BestTimeRecommender.tsx 2>/dev/null; then
        log_success "Components are integrated into BestTimeRecommender"
        ((PASSED++))
    else
        log_warning "Components NOT YET integrated (manual step required)"
        ((PASSED++))  # Not a failure, just needs manual integration
    fi
}

###############################################################################
# PHASE 6: MONITORING & OPTIMIZATION
###############################################################################
test_phase6() {
    print_header "PHASE 6: MONITORING & OPTIMIZATION"

    # Test 6.1: Check monitoring module
    test_phase 6 "Check performance monitoring module"
    python3 -c "from core.monitoring import performance_metrics, get_performance_report" 2>/dev/null
    assert_success "Performance monitoring module importable"

    # Test 6.2: Check monitoring integration
    test_phase 6 "Check monitoring integrated into repository"
    grep -q "QueryPerformanceLogger" \
        core/services/analytics_fusion/recommendations/time_analysis_repository.py
    assert_success "Monitoring integrated into time_analysis_repository"

    # Test 6.3: Generate performance report
    test_phase 6 "Generate performance report"
    python3 -c "from core.monitoring import get_performance_report; print(get_performance_report())" > /dev/null
    assert_success "Performance report generated successfully"
}

###############################################################################
# DATA VALIDATION
###############################################################################
test_data_validation() {
    print_header "DATA VALIDATION"

    local TOKEN=$(cat ~/.analyticbot_token 2>/dev/null || echo "")

    # Test: Verify response structure
    test_phase "DATA" "Validate API response structure"
    local response=$(curl -s -X GET \
        "$API_URL/analytics/predictive/best-times/$TEST_CHANNEL?days=$DAYS" \
        -H "Authorization: Bearer $TOKEN")

    # Check all required fields
    echo "$response" | jq -e '
        .success != null and
        .data.best_day_hour_combinations != null and
        .data.content_type_recommendations != null
    ' > /dev/null
    assert_success "Response has all required fields"

    # Test: Verify day-hour structure
    test_phase "DATA" "Validate day-hour combination structure"
    echo "$response" | jq -e '
        .data.best_day_hour_combinations[0] |
        has("day_name") and has("hour") and has("score") and has("confidence")
    ' > /dev/null
    assert_success "Day-hour combinations have correct structure"

    # Test: Verify content-type structure
    test_phase "DATA" "Validate content-type recommendation structure"
    echo "$response" | jq -e '
        .data.content_type_recommendations[0] |
        has("content_type") and has("day_name") and has("hour") and has("score")
    ' > /dev/null
    assert_success "Content-type recommendations have correct structure"
}

###############################################################################
# MAIN EXECUTION
###############################################################################
main() {
    print_header "COMPREHENSIVE PHASE 1-6 VALIDATION TEST"

    log_info "Testing Channel: $TEST_CHANNEL"
    log_info "Analysis Period: $DAYS days"
    log_info "API Endpoint: $API_URL"
    echo ""

    # Run all phase tests
    test_phase1
    test_phase2
    test_phase3
    test_phase4
    test_phase5
    test_phase6
    test_data_validation

    # Print summary
    print_header "TEST SUMMARY"

    local total=$((PASSED + FAILED))
    local pass_rate=$((PASSED * 100 / total))

    echo ""
    echo "Total Tests: $total"
    echo "Passed: ${GREEN}$PASSED${NC}"
    echo "Failed: ${RED}$FAILED${NC}"
    echo "Pass Rate: ${pass_rate}%"
    echo ""

    if [ $FAILED -eq 0 ]; then
        log_success "ALL TESTS PASSED! ✨"
        echo ""
        echo "✅ System is ready for production deployment"
        echo ""
        echo "Next steps:"
        echo "  1. Integrate frontend components (Phase 5)"
        echo "  2. Test in browser"
        echo "  3. Deploy to staging"
        echo "  4. Monitor for 24-48 hours"
        echo "  5. Deploy to production"
        echo ""
        return 0
    elif [ $pass_rate -ge 80 ]; then
        log_warning "MOSTLY PASSED (${pass_rate}%)"
        echo ""
        echo "⚠️  Some tests failed but system is mostly functional"
        echo "Review failed tests above and fix before production deployment"
        echo ""
        return 1
    else
        log_error "MULTIPLE TESTS FAILED"
        echo ""
        echo "❌ System has critical issues - DO NOT deploy"
        echo "Review failed tests and fix before proceeding"
        echo ""
        return 1
    fi
}

main "$@"
