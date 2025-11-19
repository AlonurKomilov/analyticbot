#!/bin/bash
# API Watchdog - Auto-restart backend if it crashes
# Run with: nohup ./scripts/api-watchdog.sh > logs/watchdog.log 2>&1 &

PROJECT_DIR="/home/abcdeveloper/projects/analyticbot"
CHECK_INTERVAL=30  # Check every 30 seconds
LOG_FILE="$PROJECT_DIR/logs/watchdog.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "API Watchdog started"

while true; do
    # Check if uvicorn is running
    if ! pgrep -f "uvicorn apps.api.main:app" > /dev/null; then
        log "⚠️  API process not found - restarting..."

        cd "$PROJECT_DIR"

        # Kill any orphaned processes
        pkill -f "uvicorn apps.api.main" 2>/dev/null
        sleep 2

        # Restart API
        make -f Makefile.dev dev-api-start

        log "✅ API restarted"
    fi

    # Check if port 11400 is listening
    if ! ss -tln | grep -q ":11400 "; then
        log "⚠️  Port 11400 not listening - killing and restarting..."

        cd "$PROJECT_DIR"
        pkill -f "uvicorn apps.api.main"
        sleep 3
        make -f Makefile.dev dev-api-start

        log "✅ API restarted (port issue)"
    fi

    sleep $CHECK_INTERVAL
done
