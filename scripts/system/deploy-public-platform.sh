#!/bin/bash
# ============================================================================
# Public Analytics Platform - Deployment Script
# 
# This script deploys the public analytics platform with all components:
# - Public catalog (analyticbot.org) - Port 11320
# - User app (app.analyticbot.org) - Port 11300
# - Moderator dashboard (moderator.analyticbot.org) - Port 11330
# - Admin panel (admin.analyticbot.org) - Port 11310
# - API (api.analyticbot.org) - Port 11400
#
# Usage: ./deploy-public-platform.sh [command]
# Commands:
#   start    - Start all services
#   stop     - Stop all services
#   restart  - Restart all services
#   status   - Check status of all services
#   nginx    - Update nginx configuration (requires sudo)
#   logs     - Show logs
# ============================================================================

set -e

PROJECT_DIR="/home/abcdev/projects/analyticbot"
LOG_DIR="/tmp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Kill process on a port
kill_port() {
    local port=$1
    if check_port $port; then
        log_info "Stopping service on port $port..."
        pkill -f "port.*$port\|$port" 2>/dev/null || true
        fuser -k $port/tcp 2>/dev/null || true
        sleep 1
    fi
}

# Start Public Frontend (port 11320)
start_public() {
    log_info "Starting Public Frontend (port 11320)..."
    cd "$PROJECT_DIR/apps/frontend/apps/public"
    nohup npm run dev > "$LOG_DIR/public-frontend.log" 2>&1 &
    sleep 3
    if check_port 11320; then
        log_success "Public Frontend started on port 11320"
    else
        log_error "Failed to start Public Frontend"
    fi
}

# Start User Frontend (port 11300)
start_user() {
    log_info "Starting User Frontend (port 11300)..."
    cd "$PROJECT_DIR/apps/frontend/apps/user"
    nohup npm run dev > "$LOG_DIR/user-frontend.log" 2>&1 &
    sleep 3
    if check_port 11300; then
        log_success "User Frontend started on port 11300"
    else
        log_warning "User Frontend not started (may not be needed)"
    fi
}

# Start Moderator Frontend (port 11330)
start_moderator() {
    log_info "Starting Moderator Frontend (port 11330)..."
    cd "$PROJECT_DIR/apps/frontend/apps/moderator"
    nohup npm run dev > "$LOG_DIR/moderator-frontend.log" 2>&1 &
    sleep 3
    if check_port 11330; then
        log_success "Moderator Frontend started on port 11330"
    else
        log_error "Failed to start Moderator Frontend"
    fi
}

# Start Admin Frontend (port 11310)
start_admin() {
    log_info "Starting Admin Frontend (port 11310)..."
    cd "$PROJECT_DIR/apps/frontend/apps/admin"
    nohup npm run dev > "$LOG_DIR/admin-frontend.log" 2>&1 &
    sleep 3
    if check_port 11310; then
        log_success "Admin Frontend started on port 11310"
    else
        log_warning "Admin Frontend not started (optional)"
    fi
}

# Start API (port 11400)
start_api() {
    log_info "Checking API (port 11400)..."
    if check_port 11400; then
        log_success "API already running on port 11400"
    else
        log_warning "API not running on port 11400 - start it separately"
    fi
}

# Start all services
start_all() {
    log_info "=========================================="
    log_info "Starting Public Analytics Platform"
    log_info "=========================================="
    
    start_api
    start_public
    start_moderator
    start_user
    start_admin
    
    echo ""
    log_info "=========================================="
    log_info "Deployment Complete!"
    log_info "=========================================="
    echo ""
    echo "Services:"
    echo "  - Public Catalog:    http://127.0.0.1:11320  (analyticbot.org)"
    echo "  - User App:          http://127.0.0.1:11300  (app.analyticbot.org)"
    echo "  - Moderator:         http://127.0.0.1:11330  (moderator.analyticbot.org)"
    echo "  - Admin:             http://127.0.0.1:11310  (admin.analyticbot.org)"
    echo "  - API:               http://127.0.0.1:11400  (api.analyticbot.org)"
    echo ""
}

# Stop all services
stop_all() {
    log_info "Stopping all frontend services..."
    
    kill_port 11320
    kill_port 11300
    kill_port 11330
    kill_port 11310
    
    pkill -f "vite" 2>/dev/null || true
    
    log_success "All frontend services stopped"
}

# Check status
check_status() {
    echo ""
    log_info "Service Status:"
    echo "=========================================="
    
    if check_port 11400; then
        echo -e "  API (11400):        ${GREEN}RUNNING${NC}"
    else
        echo -e "  API (11400):        ${RED}STOPPED${NC}"
    fi
    
    if check_port 11320; then
        echo -e "  Public (11320):     ${GREEN}RUNNING${NC}"
    else
        echo -e "  Public (11320):     ${RED}STOPPED${NC}"
    fi
    
    if check_port 11300; then
        echo -e "  User (11300):       ${GREEN}RUNNING${NC}"
    else
        echo -e "  User (11300):       ${YELLOW}STOPPED${NC}"
    fi
    
    if check_port 11330; then
        echo -e "  Moderator (11330):  ${GREEN}RUNNING${NC}"
    else
        echo -e "  Moderator (11330):  ${RED}STOPPED${NC}"
    fi
    
    if check_port 11310; then
        echo -e "  Admin (11310):      ${GREEN}RUNNING${NC}"
    else
        echo -e "  Admin (11310):      ${YELLOW}STOPPED${NC}"
    fi
    
    echo "=========================================="
    echo ""
}

# Update nginx configuration
update_nginx() {
    log_info "Updating Nginx configuration..."
    
    local NGINX_DIR="$PROJECT_DIR/infra/nginx"
    local SITES_AVAILABLE="/etc/nginx/sites-available"
    
    # Deploy individual configs
    for conf in public app moderator; do
        local SRC="${NGINX_DIR}/${conf}.analyticbot.conf"
        local DEST="${SITES_AVAILABLE}/${conf}.analyticbot.conf"
        
        if [ ! -f "$SRC" ]; then
            log_warning "Config not found: $SRC"
            continue
        fi
        
        log_info "Deploying ${conf}.analyticbot.conf..."
        sudo cp "$SRC" "$DEST"
    done
    
    log_info "Testing nginx configuration..."
    if sudo nginx -t; then
        log_info "Reloading nginx..."
        sudo systemctl reload nginx
        log_success "Nginx configuration updated and reloaded"
    else
        log_error "Nginx configuration test failed!"
        exit 1
    fi
}

# Show logs
show_logs() {
    local service=$1
    case $service in
        public)
            tail -f "$LOG_DIR/public-frontend.log"
            ;;
        user)
            tail -f "$LOG_DIR/user-frontend.log"
            ;;
        moderator)
            tail -f "$LOG_DIR/moderator-frontend.log"
            ;;
        admin)
            tail -f "$LOG_DIR/admin-frontend.log"
            ;;
        *)
            echo "Available logs: public, user, moderator, admin"
            ;;
    esac
}

# Main
case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    status)
        check_status
        ;;
    nginx)
        update_nginx
        ;;
    logs)
        show_logs $2
        ;;
    *)
        echo "Public Analytics Platform Deployment Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|nginx|logs [service]}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Check status of all services"
        echo "  nginx    - Update nginx configuration (requires sudo)"
        echo "  logs     - Show logs (public|user|moderator|admin)"
        echo ""
        exit 1
        ;;
esac
