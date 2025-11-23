#!/bin/bash

###############################################################################
# Phase 4 Post-Deployment Monitoring Script
#
# Purpose: Monitor system health after Phase 4 deployment
#
# Monitors:
#   1. API response times
#   2. Error rates
#   3. Feature flag status
#   4. Database performance
#   5. Recommendation quality
#
# Usage:
#   ./scripts/deploy_phase4_post_check.sh [environment] [duration_minutes]
#
# Examples:
#   ./scripts/deploy_phase4_post_check.sh staging 5
#   ./scripts/deploy_phase4_post_check.sh production 60
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ENVIRONMENT="${1:-production}"
DURATION_MINUTES="${2:-5}"
CHECK_INTERVAL=30  # seconds between checks

CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $(date '+%H:%M:%S') - $1"
    ((CHECKS_PASSED++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $(date '+%H:%M:%S') - $1"
    ((CHECKS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $(date '+%H:%M:%S') - $1"
    ((CHECKS_WARNING++))
}

###############################################################################
# Environment Loading
###############################################################################

load_environment() {
    local env_file=".env.$ENVIRONMENT"

    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        exit 1
    fi

    set -a
    source "$env_file"
    set +a

    log_info "Loaded environment: $ENVIRONMENT"
}

get_api_url() {
    echo "${API_HOST_URL_EXTERNAL:-http://localhost:${API_PORT:-10300}}"
}

get_auth_token() {
    local token_file="$HOME/.analyticbot_token_${ENVIRONMENT}"

    if [[ -f "$token_file" ]]; then
        cat "$token_file"
    else
        log_warning "No auth token found at $token_file"
        echo ""
    fi
}

###############################################################################
# Monitoring Checks
###############################################################################

check_api_health() {
    local api_url
    api_url=$(get_api_url)

    local response
    response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$api_url/health" 2>/dev/null || echo -e "\n000\n0")

    local body
    body=$(echo "$response" | head -n 1)

    local http_code
    http_code=$(echo "$response" | tail -n 2 | head -n 1)

    local response_time
    response_time=$(echo "$response" | tail -n 1)

    if [[ "$http_code" == "200" ]]; then
        local status
        status=$(echo "$body" | jq -r '.status' 2>/dev/null || echo "unknown")

        if [[ "$status" == "healthy" ]]; then
            log_success "API healthy (${response_time}s)"
            return 0
        else
            log_error "API unhealthy: $status"
            return 1
        fi
    else
        log_error "API unreachable (HTTP $http_code)"
        return 1
    fi
}

check_feature_flags_active() {
    # Check logs for feature flag status
    local log_file="${LOG_FILE_PATH:-logs/production.log}"

    if [[ ! -f "$log_file" ]]; then
        log_file="logs/dev_api.log"
    fi

    if [[ -f "$log_file" ]]; then
        local flag_status
        flag_status=$(tail -100 "$log_file" | grep "Feature flags" | tail -1 || echo "")

        if [[ -n "$flag_status" ]]; then
            log_success "Feature flags logged: $flag_status"
            return 0
        else
            log_warning "No feature flag logs found (system may not be processing recommendations yet)"
            return 0
        fi
    else
        log_warning "Log file not found: $log_file"
        return 0
    fi
}

check_recommendation_endpoint() {
    local api_url
    api_url=$(get_api_url)

    local token
    token=$(get_auth_token)

    if [[ -z "$token" ]]; then
        log_warning "Skipping recommendation check (no auth token)"
        return 0
    fi

    # Get a test channel ID
    local test_channel
    test_channel=$(psql "$DATABASE_URL" -t -c "
        SELECT channel_id FROM posts
        WHERE date >= NOW() - INTERVAL '90 days'
        GROUP BY channel_id
        HAVING COUNT(*) > 100
        LIMIT 1
    " 2>/dev/null | tr -d ' ' || echo "")

    if [[ -z "$test_channel" ]]; then
        log_warning "No test channel with sufficient data"
        return 0
    fi

    log_info "Testing recommendations for channel $test_channel..."

    local start_time
    start_time=$(date +%s%N)

    local response
    response=$(curl -s -w "\n%{http_code}" -X GET \
        "$api_url/analytics/predictive/best-times/$test_channel?days=90" \
        -H "Authorization: Bearer $token" \
        2>/dev/null || echo -e "\n000")

    local end_time
    end_time=$(date +%s%N)

    local duration_ms=$(( (end_time - start_time) / 1000000 ))

    local body
    body=$(echo "$response" | head -n -1)

    local http_code
    http_code=$(echo "$response" | tail -n 1)

    if [[ "$http_code" == "200" ]]; then
        local total_posts
        total_posts=$(echo "$body" | jq -r '.data.total_posts_analyzed' 2>/dev/null || echo "0")

        local has_advanced
        has_advanced=$(echo "$body" | jq -r '.data.best_day_hour_combinations != null and .data.content_type_recommendations != null' 2>/dev/null || echo "false")

        if [[ "$total_posts" -gt 0 ]]; then
            if [[ "$has_advanced" == "true" ]]; then
                log_success "Recommendations working with advanced features (${duration_ms}ms, $total_posts posts)"
            else
                log_success "Recommendations working in legacy mode (${duration_ms}ms, $total_posts posts)"
            fi

            # Check response time threshold
            if [[ $duration_ms -lt 3000 ]]; then
                log_success "Response time acceptable (<3s)"
            else
                log_warning "Response time slow (${duration_ms}ms)"
            fi

            return 0
        else
            log_warning "Recommendations returned 0 posts (check data availability)"
            return 0
        fi
    else
        log_error "Recommendations endpoint failed (HTTP $http_code)"
        return 1
    fi
}

check_database_performance() {
    log_info "Checking database query performance..."

    # Check for slow queries
    local slow_query_count
    slow_query_count=$(psql "$DATABASE_URL" -t -c "
        SELECT COUNT(*) FROM pg_stat_statements
        WHERE query LIKE '%posting_time%' AND mean_exec_time > 2000
    " 2>/dev/null || echo "N/A")

    if [[ "$slow_query_count" == "N/A" ]]; then
        log_warning "pg_stat_statements not available (cannot check query performance)"
    elif [[ "$slow_query_count" -gt 0 ]]; then
        log_warning "$slow_query_count slow queries detected (>2s)"
    else
        log_success "No slow queries detected"
    fi

    return 0
}

check_error_logs() {
    local log_file="${LOG_FILE_PATH:-logs/production.log}"

    if [[ ! -f "$log_file" ]]; then
        log_file="logs/dev_api.log"
    fi

    if [[ -f "$log_file" ]]; then
        local error_count
        error_count=$(tail -500 "$log_file" | grep -c "ERROR" || echo "0")

        if [[ "$error_count" -eq 0 ]]; then
            log_success "No errors in recent logs"
        elif [[ "$error_count" -lt 5 ]]; then
            log_warning "$error_count errors in recent logs (check manually)"
        else
            log_error "$error_count errors in recent logs (investigate immediately)"

            # Show sample errors
            log_info "Sample errors:"
            tail -500 "$log_file" | grep "ERROR" | tail -3 | while read -r line; do
                echo "    $line"
            done
        fi

        return 0
    else
        log_warning "Log file not found"
        return 0
    fi
}

check_memory_usage() {
    log_info "Checking API memory usage..."

    # Find API process
    local api_pid
    api_pid=$(pgrep -f "uvicorn.*apps.api.main" | head -1 || echo "")

    if [[ -n "$api_pid" ]]; then
        local mem_mb
        mem_mb=$(ps -o rss= -p "$api_pid" | awk '{print int($1/1024)}')

        if [[ "$mem_mb" -lt 500 ]]; then
            log_success "Memory usage normal (${mem_mb}MB)"
        elif [[ "$mem_mb" -lt 1000 ]]; then
            log_warning "Memory usage elevated (${mem_mb}MB)"
        else
            log_error "Memory usage high (${mem_mb}MB)"
        fi
    else
        log_warning "API process not found (may be in container)"
    fi

    return 0
}

###############################################################################
# Continuous Monitoring
###############################################################################

run_monitoring_cycle() {
    local cycle="$1"

    echo ""
    echo "══════════════════════════════════════════════════════"
    echo "  Monitoring Cycle #$cycle - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "══════════════════════════════════════════════════════"
    echo ""

    check_api_health || true
    check_feature_flags_active || true
    check_recommendation_endpoint || true
    check_database_performance || true
    check_error_logs || true
    check_memory_usage || true
}

###############################################################################
# Main Execution
###############################################################################

print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  Phase 4 Post-Deployment Monitoring                 ║"
    echo "║  Recommendation System Enhancement                  ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "Environment:  $ENVIRONMENT"
    echo "Duration:     ${DURATION_MINUTES} minutes"
    echo "Interval:     ${CHECK_INTERVAL} seconds"
    echo "Start time:   $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

print_summary() {
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "  Monitoring Summary"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo -e "Passed:    ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "Warnings:  ${YELLOW}$CHECKS_WARNING${NC}"
    echo -e "Failed:    ${RED}$CHECKS_FAILED${NC}"
    echo ""

    if [[ $CHECKS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ System stable after deployment!${NC}"

        if [[ $CHECKS_WARNING -gt 0 ]]; then
            echo -e "${YELLOW}⚠ Review warnings above${NC}"
        fi

        echo ""
        echo "Recommendations:"
        echo "  • Continue monitoring for 24 hours"
        echo "  • Review application logs regularly"
        echo "  • Monitor database query performance"

        if [[ "${ENABLE_TIME_WEIGHTING:-false}" == "false" ]]; then
            echo "  • Consider enabling ENABLE_TIME_WEIGHTING after 1 week"
        fi

        echo ""
        return 0
    else
        echo -e "${RED}✗ Issues detected - investigate immediately${NC}"
        echo ""
        echo "Rollback steps:"
        echo "  1. Set ENABLE_ADVANCED_RECOMMENDATIONS=false in .env"
        echo "  2. Restart API: systemctl restart analyticbot-api"
        echo "  3. Verify: curl $API_URL/health"
        echo ""
        return 1
    fi
}

main() {
    print_header
    load_environment

    local total_cycles=$(( (DURATION_MINUTES * 60) / CHECK_INTERVAL ))
    log_info "Will run $total_cycles monitoring cycles"
    echo ""

    for (( cycle=1; cycle<=total_cycles; cycle++ )); do
        run_monitoring_cycle "$cycle"

        if [[ $cycle -lt $total_cycles ]]; then
            log_info "Waiting ${CHECK_INTERVAL}s until next check..."
            sleep "$CHECK_INTERVAL"
        fi
    done

    print_summary
}

main "$@"
