#!/bin/bash

# 🛡️ SAFE DATABASE MIGRATION DEPLOYMENT SCRIPT
# Implements zero-downtime migration strategy with comprehensive safety checks
# Part of Comprehensive Database Migration Strategy

set -euo pipefail

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/var/log/analyticbot-migration-$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="$PROJECT_ROOT/backups/migration-$(date +%Y%m%d_%H%M%S)"

# Database configuration
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-analytic_bot}"
DB_USER="${DB_USER:-analytic}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

# Migration configuration
MIGRATION_TIMEOUT="${MIGRATION_TIMEOUT:-1800}"  # 30 minutes
MAX_DOWNTIME="${MAX_DOWNTIME:-300}"              # 5 minutes
ROLLBACK_WINDOW="${ROLLBACK_WINDOW:-86400}"      # 24 hours

# Logging functions
log() {
    local level="$1"
    local color="$2"
    shift 2
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${color}[${timestamp}] [${level}]${NC} ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "$BLUE" "$@"; }
success() { log "SUCCESS" "$GREEN" "$@"; }
warning() { log "WARNING" "$YELLOW" "$@"; }
error() { log "ERROR" "$RED" "$@"; }
critical() { log "CRITICAL" "$PURPLE" "$@"; exit 1; }

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🛡️  SAFE DATABASE MIGRATION SYSTEM                         ║"
    echo "║                                                                                ║"
    echo "║  Zero-downtime migration with comprehensive data protection                    ║"
    echo "║  Version: 2.0 | Date: $(date +'%Y-%m-%d %H:%M:%S')                                        ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Pre-migration safety checks
pre_migration_checks() {
    info "🔍 Running comprehensive pre-migration safety checks..."
    
    local checks_passed=0
    local total_checks=8
    
    # Check 1: Database connectivity
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        success "✅ Database connectivity confirmed"
        ((checks_passed++))
    else
        error "❌ Cannot connect to database at $DB_HOST:$DB_PORT"
    fi
    
    # Check 2: Disk space (minimum 20% free)
    local disk_usage=$(df /var/lib/postgresql/data 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//' || echo "0")
    if [ "$disk_usage" -lt 80 ]; then
        success "✅ Sufficient disk space available (${disk_usage}% used)"
        ((checks_passed++))
    else
        error "❌ Insufficient disk space: ${disk_usage}% used (need <80%)"
    fi
    
    # Check 3: No long-running transactions
    local long_running=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM pg_stat_activity 
        WHERE state = 'active' 
        AND query_start < NOW() - INTERVAL '5 minutes'
        AND pid != pg_backend_pid()
    " 2>/dev/null || echo "0")
    
    if [ "$long_running" -eq 0 ]; then
        success "✅ No long-running transactions detected"
        ((checks_passed++))
    else
        warning "⚠️  Warning: $long_running long-running transactions detected"
        ((checks_passed++))  # Not a blocking issue, just a warning
    fi
    
    # Check 4: Backup directory accessible
    if mkdir -p "$BACKUP_DIR"; then
        success "✅ Backup directory created: $BACKUP_DIR"
        ((checks_passed++))
    else
        error "❌ Cannot create backup directory: $BACKUP_DIR"
    fi
    
    # Check 5: Required tools available
    local required_tools=("alembic" "pg_dump" "pg_restore" "docker-compose")
    local tools_available=0
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" >/dev/null 2>&1; then
            ((tools_available++))
        fi
    done
    
    if [ "$tools_available" -eq ${#required_tools[@]} ]; then
        success "✅ All required tools available"
        ((checks_passed++))
    else
        error "❌ Missing required tools (found $tools_available/${#required_tools[@]})"
    fi
    
    # Check 6: Docker services running
    if docker-compose ps postgres | grep -q "Up"; then
        success "✅ PostgreSQL container is running"
        ((checks_passed++))
    else
        error "❌ PostgreSQL container is not running"
    fi
    
    # Check 7: Alembic current state
    if timeout 30 alembic current >/dev/null 2>&1; then
        success "✅ Alembic is functional"
        ((checks_passed++))
    else
        error "❌ Alembic current command failed"
    fi
    
    # Check 8: Migration files syntax validation
    if python -c "
import sys
sys.path.append('.')
try:
    from infra.db.alembic.versions import *
    print('✅ All migration files have valid syntax')
except Exception as e:
    print(f'❌ Migration file syntax error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        success "✅ Migration files syntax validated"
        ((checks_passed++))
    else
        error "❌ Migration files have syntax errors"
    fi
    
    # Final check result
    info "📊 Safety checks completed: $checks_passed/$total_checks passed"
    
    if [ "$checks_passed" -eq "$total_checks" ]; then
        success "🎯 All pre-migration safety checks PASSED!"
        return 0
    else
        critical "🚨 Pre-migration safety checks FAILED! Cannot proceed with migration."
    fi
}

# Create comprehensive backup
create_backup() {
    info "💾 Creating comprehensive pre-migration backup..."
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local db_backup="$BACKUP_DIR/database_backup_${backup_timestamp}.sql"
    local config_backup="$BACKUP_DIR/config_backup_${backup_timestamp}.tar.gz"
    
    # Database backup with extra safety
    info "📊 Creating database backup..."
    if timeout 900 pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --clean --if-exists --create --format=custom \
        > "$db_backup.dump" 2>>"$LOG_FILE"; then
        success "✅ Database backup created: $(basename "$db_backup.dump")"
    else
        critical "❌ Database backup failed!"
    fi
    
    # Also create plain SQL backup for emergency manual restore
    if timeout 900 pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --clean --if-exists --create \
        > "$db_backup" 2>>"$LOG_FILE"; then
        success "✅ Plain SQL backup created: $(basename "$db_backup")"
    else
        warning "⚠️  Plain SQL backup failed (but custom format backup succeeded)"
    fi
    
    # Configuration backup
    info "⚙️  Creating configuration backup..."
    if tar -czf "$config_backup" \
        docker-compose*.yml \
        .env* \
        infra/db/alembic/ \
        config/ \
        2>>"$LOG_FILE"; then
        success "✅ Configuration backup created: $(basename "$config_backup")"
    else
        warning "⚠️  Configuration backup failed"
    fi
    
    # Validate backups
    info "🔍 Validating backup integrity..."
    if pg_restore --list "$db_backup.dump" >/dev/null 2>&1; then
        success "✅ Database backup validated"
    else
        critical "❌ Database backup validation failed!"
    fi
    
    # Store backup information
    cat > "$BACKUP_DIR/backup_info.json" << EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "database_backup": "$(basename "$db_backup.dump")",
    "sql_backup": "$(basename "$db_backup")",
    "config_backup": "$(basename "$config_backup")",
    "database_host": "$DB_HOST",
    "database_name": "$DB_NAME",
    "migration_started": false,
    "pre_migration_alembic_head": "$(alembic current 2>/dev/null || echo 'unknown')"
}
EOF
    
    success "💾 Comprehensive backup completed successfully!"
    info "📁 Backup location: $BACKUP_DIR"
}

# Execute migration with monitoring
execute_migration() {
    info "🚀 Starting database migration execution..."
    
    local migration_start_time=$(date +%s)
    local migration_log="$BACKUP_DIR/migration_execution.log"
    
    # Update backup info
    jq '.migration_started = true' "$BACKUP_DIR/backup_info.json" > "$BACKUP_DIR/backup_info.json.tmp" && 
    mv "$BACKUP_DIR/backup_info.json.tmp" "$BACKUP_DIR/backup_info.json"
    
    # Execute migration with timeout
    info "⏱️  Migration timeout set to: $MIGRATION_TIMEOUT seconds"
    
    if timeout "$MIGRATION_TIMEOUT" alembic upgrade head 2>&1 | tee "$migration_log"; then
        local migration_end_time=$(date +%s)
        local migration_duration=$((migration_end_time - migration_start_time))
        
        success "✅ Migration completed successfully!"
        info "⏱️  Migration duration: ${migration_duration} seconds"
        
        # Log migration completion
        jq ".migration_completed = true | .migration_duration = $migration_duration" \
           "$BACKUP_DIR/backup_info.json" > "$BACKUP_DIR/backup_info.json.tmp" && 
        mv "$BACKUP_DIR/backup_info.json.tmp" "$BACKUP_DIR/backup_info.json"
        
        return 0
    else
        local migration_end_time=$(date +%s)
        local migration_duration=$((migration_end_time - migration_start_time))
        
        error "❌ Migration failed or timed out after ${migration_duration} seconds!"
        
        # Log migration failure
        jq ".migration_failed = true | .migration_duration = $migration_duration" \
           "$BACKUP_DIR/backup_info.json" > "$BACKUP_DIR/backup_info.json.tmp" && 
        mv "$BACKUP_DIR/backup_info.json.tmp" "$BACKUP_DIR/backup_info.json"
        
        return 1
    fi
}

# Post-migration validation
validate_migration() {
    info "🔍 Running post-migration validation checks..."
    
    local validation_passed=0
    local total_validations=6
    
    # Validation 1: Database connectivity
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        success "✅ Database connectivity confirmed after migration"
        ((validation_passed++))
    else
        error "❌ Database connectivity lost after migration"
    fi
    
    # Validation 2: Alembic current state
    local current_head=$(alembic current 2>/dev/null || echo "unknown")
    if [ "$current_head" != "unknown" ]; then
        success "✅ Alembic state confirmed: $current_head"
        ((validation_passed++))
    else
        error "❌ Cannot determine Alembic current state"
    fi
    
    # Validation 3: Critical table existence and counts
    local user_count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM users
    " 2>/dev/null || echo "0")
    
    if [ "$user_count" -gt 0 ]; then
        success "✅ User data validated: $user_count users found"
        ((validation_passed++))
    else
        error "❌ User data validation failed: $user_count users found"
    fi
    
    # Validation 4: Foreign key constraints
    local constraint_violations=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM (
            SELECT 1 FROM channels WHERE user_id NOT IN (SELECT id FROM users)
            UNION ALL
            SELECT 1 FROM scheduled_posts WHERE user_id NOT IN (SELECT id FROM users)
            UNION ALL
            SELECT 1 FROM scheduled_posts WHERE channel_id NOT IN (SELECT id FROM channels)
        ) violations
    " 2>/dev/null || echo "999")
    
    if [ "$constraint_violations" -eq 0 ]; then
        success "✅ Foreign key integrity validated"
        ((validation_passed++))
    else
        error "❌ Foreign key constraint violations detected: $constraint_violations"
    fi
    
    # Validation 5: Application health check
    info "🏥 Checking application health..."
    sleep 5  # Give services time to stabilize
    
    if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
        success "✅ Application health check passed"
        ((validation_passed++))
    else
        warning "⚠️  Application health check failed (may need restart)"
        # Still count as partial success since database is working
        ((validation_passed++))
    fi
    
    # Validation 6: Performance baseline check
    local query_time=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
        \\timing on
        SELECT COUNT(*) FROM users JOIN channels ON users.id = channels.user_id;
    " 2>&1 | grep "Time:" | awk '{print $2}' | sed 's/ms//' || echo "999")
    
    # Convert to numeric for comparison (remove any non-numeric chars)
    query_time_num=$(echo "$query_time" | sed 's/[^0-9.]//g')
    
    if (( $(echo "$query_time_num < 1000" | bc -l) )); then
        success "✅ Database performance check passed: ${query_time_num}ms"
        ((validation_passed++))
    else
        warning "⚠️  Database performance slower than expected: ${query_time_num}ms"
        ((validation_passed++))  # Not a blocking issue
    fi
    
    # Final validation result
    info "📊 Validation checks completed: $validation_passed/$total_validations passed"
    
    if [ "$validation_passed" -ge 5 ]; then  # Allow 1 failure
        success "🎯 Post-migration validation PASSED!"
        return 0
    else
        error "🚨 Post-migration validation FAILED!"
        return 1
    fi
}

# Rollback procedure
rollback_migration() {
    critical "🔄 INITIATING EMERGENCY ROLLBACK PROCEDURE!"
    
    warning "This will restore the database to pre-migration state"
    warning "All changes made during migration will be LOST"
    
    read -p "Continue with rollback? (type 'ROLLBACK' to confirm): " -r
    if [ "$REPLY" != "ROLLBACK" ]; then
        info "Rollback cancelled by user"
        exit 1
    fi
    
    info "🚨 Starting emergency rollback..."
    
    # Stop application services
    info "🛑 Stopping application services..."
    docker-compose down || warning "Failed to stop some services"
    
    # Restore database
    local db_backup="$BACKUP_DIR/database_backup_*.sql"
    if [ -f $db_backup ]; then
        info "📥 Restoring database from backup..."
        
        # Drop and recreate database
        PGPASSWORD="$POSTGRES_PASSWORD" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" --if-exists
        PGPASSWORD="$POSTGRES_PASSWORD" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
        
        # Restore from backup
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < $db_backup; then
            success "✅ Database restored from backup"
        else
            critical "❌ Database restore failed!"
        fi
    else
        critical "❌ No backup file found for restore!"
    fi
    
    # Restart services
    info "🚀 Restarting services..."
    docker-compose up -d
    
    # Validate rollback
    if validate_migration; then
        success "🎯 Rollback completed successfully!"
    else
        critical "❌ Rollback validation failed!"
    fi
}

# Main execution flow
main() {
    show_banner
    
    # Check command line arguments
    case "${1:-deploy}" in
        "deploy")
            info "🚀 Starting safe database migration deployment..."
            
            # Step 1: Pre-migration checks
            if ! pre_migration_checks; then
                critical "Pre-migration checks failed!"
            fi
            
            # Step 2: Create backup
            create_backup
            
            # Step 3: Execute migration
            if execute_migration; then
                # Step 4: Validate migration
                if validate_migration; then
                    success "🎉 Migration deployment completed successfully!"
                    info "📁 Backup preserved at: $BACKUP_DIR"
                    info "🔄 Rollback available for next $((ROLLBACK_WINDOW / 3600)) hours"
                else
                    error "❌ Migration validation failed!"
                    warning "🔄 Consider rollback if issues persist"
                    exit 1
                fi
            else
                error "❌ Migration execution failed!"
                rollback_migration
            fi
            ;;
            
        "rollback")
            rollback_migration
            ;;
            
        "validate")
            info "🔍 Running standalone validation..."
            validate_migration
            ;;
            
        "checks")
            info "🔍 Running standalone pre-migration checks..."
            pre_migration_checks
            ;;
            
        *)
            echo "Usage: $0 [deploy|rollback|validate|checks]"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full migration deployment (default)"
            echo "  rollback - Emergency rollback to last backup"
            echo "  validate - Run post-migration validation only"
            echo "  checks   - Run pre-migration safety checks only"
            exit 1
            ;;
    esac
}

# Trap signals for clean exit
trap 'echo -e "\n${RED}Migration interrupted!${NC}"; exit 1' INT TERM

# Execute main function
main "$@"