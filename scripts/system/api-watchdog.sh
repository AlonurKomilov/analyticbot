#!/bin/bash
# API Watchdog - Auto-restart backend if it crashes
# Run with: nohup ./scripts/api-watchdog.sh &
# Stop with: pkill -f "api-watchdog.sh"

PROJECT_DIR="/home/abcdeveloper/projects/analyticbot"
CHECK_INTERVAL=60  # Check every 60 seconds
LOG_FILE="$PROJECT_DIR/logs/watchdog.log"
RESTART_COOLDOWN=120  # Wait 2 minutes between restarts
LAST_RESTART=0

cd "$PROJECT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_api_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://localhost:11400/health 2>/dev/null)
    [ "$response" = "200" ]
}

restart_api() {
    current_time=$(date +%s)
    time_since_restart=$((current_time - LAST_RESTART))
    
    if [ $time_since_restart -lt $RESTART_COOLDOWN ]; then
        log "⏳ Cooldown active. Wait $((RESTART_COOLDOWN - time_since_restart))s before next restart."
        return
    fi
    
    log "🔄 Restarting API server..."
    
    # Kill any existing API/uvicorn on port 11400
    pkill -f "uvicorn.*11400" 2>/dev/null || true
    sleep 2
    pkill -9 -f "uvicorn.*11400" 2>/dev/null || true
    sleep 1
    
    # Activate venv and load environment
    source "$PROJECT_DIR/.venv/bin/activate"
    if [ -f "$PROJECT_DIR/.env.development" ]; then
        set -a
        source "$PROJECT_DIR/.env.development"
        set +a
    fi
    
    # Start uvicorn
    nohup uvicorn apps.api.main:app \
        --host 0.0.0.0 \
        --port 11400 \
        --reload \
        --log-level debug \
        --reload-exclude venv \
        --reload-exclude .venv \
        --reload-exclude "*/__pycache__/*" \
        >> "$PROJECT_DIR/logs/dev_api.log" 2>&1 &
    
    new_pid=$!
    echo $new_pid > "$PROJECT_DIR/logs/dev_api.pid"
    LAST_RESTART=$(date +%s)
    
    log "✅ API started (PID: $new_pid)"
    
    # Wait for health
    for i in {1..30}; do
        sleep 2
        if check_api_health; then
            log "✅ API healthy after restart"
            return
        fi
    done
    log "⚠️ API may not be fully healthy yet"
}

log "🐕 API Watchdog started (check every ${CHECK_INTERVAL}s)"

while true; do
    if ! check_api_health; then
        log "❌ API health check failed!"
        restart_api
    fi
    sleep $CHECK_INTERVAL
done
