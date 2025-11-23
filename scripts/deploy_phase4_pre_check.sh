#!/bin/bash

###############################################################################
# Phase 4 Pre-Deployment Validation Script
#
# Purpose: Validate system is ready for Phase 4 deployment
#
# Checks:
#   1. Database schema (migration 004 applied)
#   2. Feature flags configured
#   3. API health and connectivity
#   4. Dependencies installed
#   5. Backup verification
#
# Usage:
#   ./scripts/deploy_phase4_pre_check.sh [environment]
#
# Examples:
#   ./scripts/deploy_phase4_pre_check.sh staging
#   ./scripts/deploy_phase4_pre_check.sh production
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
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_TOTAL=0

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
    ((CHECKS_TOTAL++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
    ((CHECKS_TOTAL++))
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

###############################################################################
# Environment Loading
###############################################################################

load_environment() {
    log_info "Loading environment: $ENVIRONMENT"

    local env_file=".env.$ENVIRONMENT"

    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        return 1
    fi

    # Load environment variables
    set -a
    source "$env_file"
    set +a

    log_success "Environment loaded from $env_file"
    return 0
}

###############################################################################
# Validation Checks
###############################################################################

check_database_connection() {
    log_info "Checking database connection..."

    # Try to connect to database
    if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
        log_success "Database connection successful"
        return 0
    else
        log_error "Cannot connect to database: $DATABASE_URL"
        return 1
    fi
}

check_migration_004() {
    log_info "Verifying migration 004 (content-type columns)..."

    local result
    result=$(psql "$DATABASE_URL" -t -c "
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = 'posts'
        AND column_name IN ('has_video', 'has_media')
    " 2>/dev/null || echo "0")

    if [[ "$result" -ge 2 ]]; then
        log_success "Migration 004 applied (has_video, has_media columns exist)"

        # Check if indexes exist
        local index_count
        index_count=$(psql "$DATABASE_URL" -t -c "
            SELECT COUNT(*) FROM pg_indexes
            WHERE tablename = 'posts'
            AND indexname IN ('idx_posts_content_type', 'idx_posts_date_content')
        " 2>/dev/null || echo "0")

        if [[ "$index_count" -ge 2 ]]; then
            log_success "Content-type indexes exist"
        else
            log_warning "Content-type indexes missing (performance may be degraded)"
        fi

        return 0
    else
        log_error "Migration 004 NOT applied - run infra/db/migrations/004_add_post_content_type_detection.sql"
        return 1
    fi
}

check_data_backfill() {
    log_info "Checking content-type data backfill..."

    local video_count
    video_count=$(psql "$DATABASE_URL" -t -c "
        SELECT COUNT(*) FROM posts WHERE has_video = TRUE
    " 2>/dev/null || echo "0")

    local media_count
    media_count=$(psql "$DATABASE_URL" -t -c "
        SELECT COUNT(*) FROM posts WHERE has_media = TRUE
    " 2>/dev/null || echo "0")

    if [[ "$video_count" -gt 0 || "$media_count" -gt 0 ]]; then
        log_success "Data backfilled ($video_count videos, $media_count images detected)"
        return 0
    else
        log_warning "No content-type data detected (may need manual backfill or wait for new posts)"
        return 0
    fi
}

check_feature_flags() {
    log_info "Validating feature flag configuration..."

    local flags_configured=0

    if [[ -n "${ENABLE_ADVANCED_RECOMMENDATIONS:-}" ]]; then
        log_success "ENABLE_ADVANCED_RECOMMENDATIONS = $ENABLE_ADVANCED_RECOMMENDATIONS"
        ((flags_configured++))
    else
        log_error "ENABLE_ADVANCED_RECOMMENDATIONS not set"
    fi

    if [[ -n "${ENABLE_TIME_WEIGHTING:-}" ]]; then
        log_success "ENABLE_TIME_WEIGHTING = $ENABLE_TIME_WEIGHTING"
        ((flags_configured++))
    else
        log_error "ENABLE_TIME_WEIGHTING not set"
    fi

    if [[ -n "${ENABLE_CONTENT_TYPE_ANALYSIS:-}" ]]; then
        log_success "ENABLE_CONTENT_TYPE_ANALYSIS = $ENABLE_CONTENT_TYPE_ANALYSIS"
        ((flags_configured++))
    else
        log_error "ENABLE_CONTENT_TYPE_ANALYSIS not set"
    fi

    if [[ $flags_configured -eq 3 ]]; then
        return 0
    else
        log_error "Feature flags not properly configured in environment"
        return 1
    fi
}

check_conservative_flags() {
    log_info "Checking for conservative flag settings (production best practice)..."

    if [[ "$ENVIRONMENT" == "production" ]]; then
        if [[ "${ENABLE_TIME_WEIGHTING:-true}" == "false" ]]; then
            log_success "Time-weighting disabled (conservative approach)"
        else
            log_warning "Time-weighting enabled on first deployment (consider disabling initially)"
        fi

        if [[ "${ENABLE_CONTENT_TYPE_ANALYSIS:-false}" == "true" ]]; then
            log_success "Content-type analysis enabled (low risk)"
        fi
    fi

    return 0
}

check_api_health() {
    log_info "Checking API health endpoint..."

    local api_url="${API_HOST_URL_EXTERNAL:-http://localhost:${API_PORT:-10300}}"

    local health_status
    health_status=$(curl -s "$api_url/health" | jq -r '.status' 2>/dev/null || echo "")

    if [[ "$health_status" == "healthy" ]]; then
        log_success "API health check passed"
        return 0
    else
        log_warning "API not reachable or unhealthy (may be starting up)"
        return 0
    fi
}

check_code_repository() {
    log_info "Checking code repository..."

    # Check if we're in a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local branch
        branch=$(git rev-parse --abbrev-ref HEAD)

        local commit
        commit=$(git rev-parse --short HEAD)

        log_success "Git repository: branch=$branch, commit=$commit"

        # Check for uncommitted changes
        if git diff-index --quiet HEAD --; then
            log_success "No uncommitted changes"
        else
            log_warning "Uncommitted changes detected - ensure all changes are committed"
        fi

        return 0
    else
        log_warning "Not a git repository"
        return 0
    fi
}

check_dependencies() {
    log_info "Checking Python dependencies..."

    if [[ -f "requirements.txt" ]]; then
        log_success "requirements.txt found"
    else
        log_error "requirements.txt not found"
        return 1
    fi

    # Check if virtual environment is active
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        log_success "Virtual environment active: $VIRTUAL_ENV"
    else
        log_warning "No virtual environment active"
    fi

    return 0
}

check_backup_readiness() {
    log_info "Checking backup preparation..."

    # Check if backup directory exists
    if [[ -d "backups" ]]; then
        local backup_count
        backup_count=$(ls -1 backups/*.sql 2>/dev/null | wc -l || echo "0")

        if [[ "$backup_count" -gt 0 ]]; then
            log_success "Backups directory exists with $backup_count backup files"
        else
            log_warning "No database backups found in backups/"
        fi
    else
        log_warning "backups/ directory not found"
    fi

    log_info "📝 Recommendation: Create pre-deployment backup:"
    echo "    pg_dump \"$DATABASE_URL\" > backups/pre_phase4_\$(date +%Y%m%d_%H%M%S).sql"

    return 0
}

check_rollback_script() {
    log_info "Checking rollback scripts..."

    if [[ -f "infra/db/migrations/004_rollback.sql" ]]; then
        log_success "Rollback script exists: 004_rollback.sql"
    else
        log_error "Rollback script missing: infra/db/migrations/004_rollback.sql"
        return 1
    fi

    return 0
}

check_monitoring_tools() {
    log_info "Checking monitoring tools..."

    local tools=("curl" "jq" "psql")
    local missing=()

    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            log_success "$tool installed"
        else
            log_error "$tool not installed"
            missing+=("$tool")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Install missing tools: ${missing[*]}"
        return 1
    fi

    return 0
}

###############################################################################
# Main Execution
###############################################################################

print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  Phase 4 Pre-Deployment Validation                  ║"
    echo "║  Recommendation System Enhancement                  ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "Environment: $ENVIRONMENT"
    echo "Date: $(date)"
    echo ""
}

print_summary() {
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "  Validation Summary"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "Total checks:  $CHECKS_TOTAL"
    echo -e "Passed:        ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "Failed:        ${RED}$CHECKS_FAILED${NC}"
    echo ""

    if [[ $CHECKS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ System ready for Phase 4 deployment!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Create database backup (recommended)"
        echo "  2. Deploy to staging first: make deploy-staging"
        echo "  3. Run post-deployment validation: ./scripts/deploy_phase4_post_check.sh staging"
        echo "  4. Monitor for 24 hours"
        echo "  5. Deploy to production: make deploy-production"
        echo ""
        return 0
    else
        echo -e "${RED}✗ System NOT ready - fix errors above${NC}"
        echo ""
        return 1
    fi
}

main() {
    print_header

    # Load environment
    if ! load_environment; then
        print_summary
        exit 1
    fi

    echo ""
    echo "═══ Running Validation Checks ═══"
    echo ""

    # Run all checks
    check_database_connection || true
    check_migration_004 || true
    check_data_backfill || true
    check_feature_flags || true
    check_conservative_flags || true
    check_api_health || true
    check_code_repository || true
    check_dependencies || true
    check_backup_readiness || true
    check_rollback_script || true
    check_monitoring_tools || true

    print_summary
}

main "$@"
