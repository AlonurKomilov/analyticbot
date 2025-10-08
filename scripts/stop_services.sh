#!/bin/bash
set -e

# AnalyticBot Stop Services Script
# Gracefully stops all running services

echo "🛑 Stopping AnalyticBot Services"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Stop Docker services if running
if command -v docker > /dev/null 2>&1 && docker ps | grep -q "analyticbot"; then
    echo "Stopping Docker services..."
    docker-compose down > /dev/null 2>&1 || true
    print_status "Docker services stopped"
fi

# Stop local services
if [ -d "pids" ]; then
    # Stop API
    if [ -f "pids/api.pid" ]; then
        API_PID=$(cat pids/api.pid)
        if ps -p $API_PID > /dev/null 2>&1; then
            kill $API_PID
            print_status "API service stopped"
        fi
        rm -f pids/api.pid
    fi

    # Stop Bot
    if [ -f "pids/bot.pid" ]; then
        BOT_PID=$(cat pids/bot.pid)
        if ps -p $BOT_PID > /dev/null 2>&1; then
            kill $BOT_PID
            print_status "Bot service stopped"
        fi
        rm -f pids/bot.pid
    fi

    # Stop Frontend
    if [ -f "pids/frontend.pid" ]; then
        FRONTEND_PID=$(cat pids/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID
            print_status "Frontend service stopped"
        fi
        rm -f pids/frontend.pid
    fi
fi

# Kill any remaining processes
pkill -f "uvicorn apps.api.main:app" 2>/dev/null || true
pkill -f "apps/bot/run_bot.py" 2>/dev/null || true
pkill -f "vite.*frontend" 2>/dev/null || true

print_status "All services stopped successfully"

echo ""
echo -e "${GREEN}🏁 All AnalyticBot services have been stopped${NC}"
