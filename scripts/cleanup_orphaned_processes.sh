#!/bin/bash
# Automated Cleanup Script for Orphaned Processes
# Runs periodically to clean up stuck workers, old connections, and zombie processes

set -e

LOG_FILE="/tmp/analyticbot_cleanup.log"
MAX_PROCESS_AGE_DAYS=1  # Kill processes older than 1 day
MAX_MEMORY_PERCENT=85   # Trigger cleanup if memory exceeds 85%

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting automated process cleanup"
log "=========================================="

# Function to check memory usage
check_memory() {
    local mem_percent=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
    echo "$mem_percent"
}

# Function to kill orphaned multiprocessing workers
cleanup_orphaned_workers() {
    log "Checking for orphaned Python multiprocessing workers..."

    # Find processes older than MAX_PROCESS_AGE_DAYS
    local cutoff_date=$(date -d "$MAX_PROCESS_AGE_DAYS days ago" +%s)
    local current_date=$(date +%s)

    # Get orphaned multiprocessing workers (older than 1 day)
    local orphaned_pids=$(ps aux | grep "multiprocessing" | grep -v grep | awk '{
        # Extract start date from column 9 (format: Nov07, Nov10, or time like 11:16)
        start=$9
        # If it contains ":", it started today, skip it
        if (start ~ /:/) {
            next
        }
        # Otherwise it'\''s a date like Nov07
        print $2
    }')

    if [ -z "$orphaned_pids" ]; then
        log "✅ No orphaned workers found"
        return 0
    fi

    local count=$(echo "$orphaned_pids" | wc -w)
    log "⚠️  Found $count orphaned workers"

    for pid in $orphaned_pids; do
        local cmd=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "unknown")
        log "  Killing PID $pid: $cmd"
        kill -9 "$pid" 2>/dev/null || log "    Failed to kill $pid (may already be dead)"
    done

    log "✅ Cleanup complete: $count processes killed"
}

# Function to cleanup old PostgreSQL idle connections
cleanup_idle_connections() {
    log "Checking for old idle PostgreSQL connections..."

    # This would require psql access - skipping for now
    # You can add: psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';"

    log "ℹ️  PostgreSQL cleanup skipped (requires DB credentials)"
}

# Function to cleanup zombie processes
cleanup_zombies() {
    log "Checking for zombie processes..."

    local zombie_count=$(ps aux | awk '$8=="Z" {print $2}' | wc -l)

    if [ "$zombie_count" -eq 0 ]; then
        log "✅ No zombie processes found"
        return 0
    fi

    log "⚠️  Found $zombie_count zombie processes"

    # Try to reap zombies by killing their parent processes
    ps aux | awk '$8=="Z" {print $2}' | while read pid; do
        local parent=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
        if [ -n "$parent" ] && [ "$parent" != "1" ]; then
            log "  Killing parent PID $parent of zombie $pid"
            kill -TERM "$parent" 2>/dev/null || true
        fi
    done

    log "✅ Zombie cleanup attempted"
}

# Function to restart stuck services
restart_stuck_services() {
    log "Checking for stuck services..."

    # Check if MTProto worker is consuming too much memory
    local worker_mem=$(ps aux | grep "apps.mtproto.worker" | grep -v grep | awk '{sum+=$6} END {print sum/1024}')

    if [ -n "$worker_mem" ] && [ "${worker_mem%.*}" -gt 1000 ]; then
        log "⚠️  MTProto worker using ${worker_mem}MB (>1GB), restarting..."
        pkill -f "apps.mtproto.worker" || true
        sleep 2
        log "✅ MTProto worker restarted"
    else
        log "✅ No stuck services detected"
    fi
}

# Main cleanup flow
main() {
    local mem_percent=$(check_memory)
    log "Current memory usage: ${mem_percent}%"

    # Always cleanup orphaned workers
    cleanup_orphaned_workers

    # If memory is high, do more aggressive cleanup
    if [ "$mem_percent" -gt "$MAX_MEMORY_PERCENT" ]; then
        log "⚠️  High memory usage detected (${mem_percent}% > ${MAX_MEMORY_PERCENT}%)"
        cleanup_zombies
        restart_stuck_services
    fi

    # Report final stats
    local mem_after=$(check_memory)
    local mem_freed=$((mem_percent - mem_after))

    log "=========================================="
    log "Cleanup complete!"
    log "Memory before: ${mem_percent}%"
    log "Memory after:  ${mem_after}%"
    log "Memory freed:  ${mem_freed}%"
    log "=========================================="
}

# Run main cleanup
main

# Keep last 1000 lines of log
tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"

exit 0
