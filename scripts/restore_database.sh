#!/bin/bash
#
# Database Restore Script - AnalyticBot
#
# DANGEROUS: This script will OVERWRITE your database!
# Always create a backup before restoring.
#
# Usage: ./scripts/restore_database.sh [backup_file]
#        ./scripts/restore_database.sh --list
#        ./scripts/restore_database.sh --latest
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="/home/abcdeveloper/backups/database"
LOG_DIR="/home/abcdeveloper/backups/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/restore_${DATE_ONLY}.log"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env.development" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env.development" | grep DATABASE_URL | xargs)
fi

# Parse DATABASE_URL
DB_URL="${DATABASE_URL:-postgresql+asyncpg://analytic:change_me@localhost:10100/analytic_bot}"
DB_URL_CLEAN="${DB_URL#postgresql+asyncpg://}"
DB_CREDS="${DB_URL_CLEAN%%@*}"
DB_USER="${DB_CREDS%%:*}"
DB_PASS="${DB_CREDS#*:}"
DB_HOST_PORT="${DB_URL_CLEAN#*@}"
DB_HOST="${DB_HOST_PORT%%:*}"
DB_PORT="${DB_HOST_PORT#*:}"
DB_PORT="${DB_PORT%%/*}"
DB_NAME="${DB_HOST_PORT##*/}"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
}

log_error() {
    log "ERROR" "$@"
}

log_warning() {
    log "WARNING" "$@"
}

log_success() {
    log "SUCCESS" "$@"
}

list_backups() {
    echo "============================================================================"
    echo "Available Backups"
    echo "============================================================================"
    echo ""

    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/analyticbot_*.sql.gz 2>/dev/null)" ]; then
        echo "No backups found in $BACKUP_DIR"
        exit 0
    fi

    local count=1
    for backup in $(ls -t "$BACKUP_DIR"/analyticbot_*.sql.gz); do
        local filename=$(basename "$backup")
        local size=$(du -h "$backup" | cut -f1)
        local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup" 2>/dev/null || stat -c "%y" "$backup" 2>/dev/null | cut -d'.' -f1)
        local age=$(( ($(date +%s) - $(stat -f "%m" "$backup" 2>/dev/null || stat -c "%Y" "$backup" 2>/dev/null)) / 86400 ))

        echo "[$count] $filename"
        echo "    Size: $size"
        echo "    Date: $date"
        echo "    Age:  $age day(s) ago"

        # Show metadata if available
        if [ -f "${backup}.meta" ]; then
            local db_size=$(grep "database_size" "${backup}.meta" | cut -d'"' -f4)
            echo "    DB:   $db_size"
        fi
        echo ""

        ((count++))
    done

    echo "============================================================================"
    exit 0
}

get_latest_backup() {
    local latest=$(ls -t "$BACKUP_DIR"/analyticbot_*.sql.gz 2>/dev/null | head -1)
    if [ -z "$latest" ]; then
        log_error "No backups found"
        exit 1
    fi
    echo "$latest"
}

verify_backup_file() {
    local backup_file="$1"

    log_info "Verifying backup file: $(basename "$backup_file")"

    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi

    # Test gzip integrity
    if ! gzip -t "$backup_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_error "Backup file is corrupted (gzip test failed)"
        return 1
    fi

    # Check if it's a valid PostgreSQL dump
    if ! gunzip -c "$backup_file" | head -100 | grep -q "PostgreSQL database dump"; then
        log_error "File does not appear to be a valid PostgreSQL dump"
        return 1
    fi

    log_success "Backup file verification passed"
    return 0
}

create_pre_restore_backup() {
    log_info "Creating pre-restore backup..."

    local pre_restore_file="$BACKUP_DIR/pre_restore_${TIMESTAMP}.sql"
    local pre_restore_file_gz="${pre_restore_file}.gz"

    PGPASSWORD="$DB_PASS" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=plain \
        --no-owner \
        --no-acl \
        -f "$pre_restore_file" 2>&1 | tee -a "$LOG_FILE"

    if [ ! -f "$pre_restore_file" ]; then
        log_error "Pre-restore backup failed"
        return 1
    fi

    gzip -9 "$pre_restore_file"

    local size=$(du -h "$pre_restore_file_gz" | cut -f1)
    log_success "Pre-restore backup created: $(basename "$pre_restore_file_gz") ($size)"

    echo "$pre_restore_file_gz"
}

show_restore_warning() {
    local backup_file="$1"
    local filename=$(basename "$backup_file")
    local size=$(du -h "$backup_file" | cut -f1)
    local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup_file" 2>/dev/null || stat -c "%y" "$backup_file" 2>/dev/null | cut -d'.' -f1)

    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                            ⚠️  WARNING ⚠️                               ║"
    echo "╠════════════════════════════════════════════════════════════════════════╣"
    echo "║  You are about to RESTORE the database from a backup.                 ║"
    echo "║  This will PERMANENTLY OVERWRITE all current data in the database!    ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Restore Details:"
    echo "  Database:    $DB_NAME @ $DB_HOST:$DB_PORT"
    echo "  Backup file: $filename"
    echo "  Backup size: $size"
    echo "  Backup date: $date"
    echo ""
    echo "A pre-restore backup will be created automatically."
    echo ""
}

confirm_restore() {
    local backup_file="$1"

    show_restore_warning "$backup_file"

    echo -n "Type 'RESTORE' (in uppercase) to confirm: "
    read confirmation

    if [ "$confirmation" != "RESTORE" ]; then
        log_info "Restore cancelled by user"
        exit 0
    fi

    echo ""
    echo -n "Are you absolutely sure? Type 'YES' to proceed: "
    read final_confirmation

    if [ "$final_confirmation" != "YES" ]; then
        log_info "Restore cancelled by user"
        exit 0
    fi

    log_info "Restore confirmed by user"
    echo ""
}

restore_database() {
    local backup_file="$1"

    log_info "Starting database restore..."
    log_info "Backup: $(basename "$backup_file")"

    # Decompress and restore
    log_info "Decompressing and restoring backup..."

    # Drop all connections to the database first
    log_info "Terminating active connections to database..."
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" \
        2>&1 | tee -a "$LOG_FILE" || true

    # Drop and recreate database
    log_warning "Dropping database: $DB_NAME"
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
        "DROP DATABASE IF EXISTS $DB_NAME;" 2>&1 | tee -a "$LOG_FILE"

    log_info "Creating fresh database: $DB_NAME"
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
        "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>&1 | tee -a "$LOG_FILE"

    # Restore from backup
    log_info "Restoring data from backup..."
    gunzip -c "$backup_file" | PGPASSWORD="$DB_PASS" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --set ON_ERROR_STOP=on \
        2>&1 | tee -a "$LOG_FILE"

    if [ $? -ne 0 ]; then
        log_error "Restore failed! Check logs: $LOG_FILE"
        return 1
    fi

    log_success "Database restore completed"
    return 0
}

verify_restored_database() {
    log_info "Verifying restored database..."

    # Check connection
    if ! PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &>/dev/null; then
        log_error "Cannot connect to restored database"
        return 1
    fi

    # Check table count
    local table_count=$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)

    log_info "Tables restored: $table_count"

    if (( table_count < 10 )); then
        log_warning "Low table count detected: $table_count (expected 30+)"
    fi

    # Check if alembic_version exists
    if PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c \
        "SELECT version_num FROM alembic_version LIMIT 1" &>/dev/null; then
        local migration=$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
            "SELECT version_num FROM alembic_version" | xargs)
        log_info "Migration version: $migration"
    fi

    log_success "Database verification passed"
    return 0
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    echo "============================================================================"
    echo "AnalyticBot Database Restore"
    echo "============================================================================"
    echo ""

    mkdir -p "$LOG_DIR"

    # Parse arguments
    if [ $# -eq 0 ]; then
        echo "Usage: $0 [backup_file|--list|--latest]"
        echo ""
        echo "Options:"
        echo "  --list           List all available backups"
        echo "  --latest         Restore from the most recent backup"
        echo "  <backup_file>    Restore from specific backup file"
        echo ""
        exit 1
    fi

    if [ "$1" == "--list" ]; then
        list_backups
    fi

    local backup_file=""

    if [ "$1" == "--latest" ]; then
        backup_file=$(get_latest_backup)
        log_info "Selected latest backup: $(basename "$backup_file")"
    else
        backup_file="$1"
        if [ ! -f "$backup_file" ]; then
            # Try to find in backup directory
            local filename=$(basename "$backup_file")
            if [ -f "$BACKUP_DIR/$filename" ]; then
                backup_file="$BACKUP_DIR/$filename"
            else
                log_error "Backup file not found: $backup_file"
                exit 1
            fi
        fi
    fi

    log_info "Restore started"

    # Verify backup file
    if ! verify_backup_file "$backup_file"; then
        log_error "Backup verification failed"
        exit 1
    fi

    # Confirm with user
    confirm_restore "$backup_file"

    # Create pre-restore backup
    pre_restore_backup=$(create_pre_restore_backup)
    if [ -z "$pre_restore_backup" ]; then
        log_error "Failed to create pre-restore backup. Aborting."
        exit 1
    fi

    log_info "Pre-restore backup: $(basename "$pre_restore_backup")"
    echo ""

    # Perform restore
    if ! restore_database "$backup_file"; then
        log_error "Restore failed!"
        echo ""
        echo "╔════════════════════════════════════════════════════════════════════════╗"
        echo "║  RESTORE FAILED!                                                       ║"
        echo "║  Your pre-restore backup is available at:                             ║"
        echo "║  $(printf '%-70s' "$pre_restore_backup")║"
        echo "╚════════════════════════════════════════════════════════════════════════╝"
        exit 1
    fi

    # Verify restored database
    if ! verify_restored_database; then
        log_warning "Database verification had issues (but restore completed)"
    fi

    # Success summary
    echo ""
    echo "============================================================================"
    log_success "Restore completed successfully!"
    echo "============================================================================"
    echo "Restored from: $(basename "$backup_file")"
    echo "Database: $DB_NAME"
    echo "Pre-restore backup: $(basename "$pre_restore_backup")"
    echo "Log: $LOG_FILE"
    echo ""
    echo "⚠️  IMPORTANT: Restart your application services now!"
    echo "============================================================================"
    echo ""

    exit 0
}

# Trap errors
trap 'log_error "Restore script failed with error code $?"' ERR

# Run main function
main "$@"
