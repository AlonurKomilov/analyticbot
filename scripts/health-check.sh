#!/bin/bash
# Comprehensive Health Check Script for AnalyticBot Services
# Provides detailed health monitoring for all services and dependencies

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_HOST=${API_HOST:-"localhost"}
API_PORT=${API_PORT:-"10400"}
BOT_PORT=${BOT_PORT:-"10500"}
MTPROTO_PORT=${MTPROTO_PORT:-"8091"}
FRONTEND_PORT=${FRONTEND_PORT:-"10300"}

# Default timeout for health checks
TIMEOUT=${TIMEOUT:-10}
VERBOSE=${VERBOSE:-false}

echo -e "${BLUE}🏥 AnalyticBot Comprehensive Health Check${NC}"
echo "=========================================="
echo

# Function to make HTTP requests with timeout
make_request() {
    local url="$1"
    local timeout="${2:-$TIMEOUT}"
    
    if command -v curl >/dev/null 2>&1; then
        curl -s --max-time "$timeout" --connect-timeout 5 "$url" 2>/dev/null || echo '{"error": "connection_failed"}'
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- --timeout="$timeout" "$url" 2>/dev/null || echo '{"error": "connection_failed"}'
    else
        echo '{"error": "no_http_client"}'
    fi
}

# Function to check if a port is open
check_port() {
    local host="$1"
    local port="$2"
    local timeout="${3:-5}"
    
    if command -v nc >/dev/null 2>&1; then
        nc -z -w"$timeout" "$host" "$port" >/dev/null 2>&1
    elif command -v timeout >/dev/null 2>&1; then
        timeout "$timeout" bash -c "</dev/tcp/$host/$port" >/dev/null 2>&1
    else
        # Fallback using Python if available
        python3 -c "
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout($timeout)
    result = sock.connect_ex(('$host', $port))
    sock.close()
    sys.exit(0 if result == 0 else 1)
except:
    sys.exit(1)
" >/dev/null 2>&1
    fi
}

# Function to parse JSON status
parse_status() {
    local json="$1"
    local field="${2:-status}"
    
    if command -v jq >/dev/null 2>&1; then
        echo "$json" | jq -r ".$field // \"unknown\""
    else
        # Simple grep-based parsing
        echo "$json" | grep -o "\"$field\":\"[^\"]*\"" | cut -d'"' -f4 || echo "unknown"
    fi
}

# Function to display service status
show_service_status() {
    local service_name="$1"
    local status="$2"
    local details="$3"
    local response_time="$4"
    
    case "$status" in
        "ok"|"healthy"|"ready"|"alive")
            echo -e "  ${GREEN}✅ $service_name${NC} - $status"
            ;;
        "degraded"|"warning")
            echo -e "  ${YELLOW}⚠️  $service_name${NC} - $status"
            ;;
        "error"|"unhealthy"|"not_ready"|"dead")
            echo -e "  ${RED}❌ $service_name${NC} - $status"
            ;;
        *)
            echo -e "  ${PURPLE}❓ $service_name${NC} - $status"
            ;;
    esac
    
    if [[ "$VERBOSE" == "true" && -n "$details" ]]; then
        echo "    Response time: ${response_time}ms"
        echo "    Details: $details"
    fi
}

# API Service Health Check
echo -e "${CYAN}🚀 API Service Health Check${NC}"
echo "----------------------------"

start_time=$(date +%s%3N)
if check_port "$API_HOST" "$API_PORT"; then
    api_response=$(make_request "http://$API_HOST:$API_PORT/health")
    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))
    
    api_status=$(parse_status "$api_response" "status")
    api_env=$(parse_status "$api_response" "environment")
    api_version=$(parse_status "$api_response" "version")
    
    show_service_status "API Server" "$api_status" "Environment: $api_env, Version: $api_version" "$response_time"
    
    # Check API dependencies
    if [[ "$VERBOSE" == "true" ]]; then
        echo "  📊 Dependencies:"
        db_status=$(parse_status "$api_response" "dependencies.database.healthy")
        if [[ "$db_status" == "true" ]]; then
            echo -e "    ${GREEN}✅ Database${NC}"
        else
            echo -e "    ${RED}❌ Database${NC}"
        fi
    fi
else
    echo -e "  ${RED}❌ API Server${NC} - port $API_PORT not accessible"
fi

echo

# Bot Service Health Check
echo -e "${CYAN}🤖 Bot Service Health Check${NC}"
echo "----------------------------"

# Check if bot health endpoint exists (assuming it's added to a health router)
start_time=$(date +%s%3N)
bot_health_response=$(make_request "http://$API_HOST:$API_PORT/bot/health" 2>/dev/null)
end_time=$(date +%s%3N)
response_time=$((end_time - start_time))

if [[ "$bot_health_response" != *"error"* ]]; then
    bot_status=$(parse_status "$bot_health_response" "status")
    show_service_status "Bot Service" "$bot_status" "Health endpoint available" "$response_time"
else
    # Fallback: Check if bot process is running
    if pgrep -f "apps.bot" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Bot Service${NC} - process running"
    else
        echo -e "  ${YELLOW}⚠️  Bot Service${NC} - process not detected"
    fi
fi

echo

# MTProto Service Health Check
echo -e "${CYAN}📡 MTProto Service Health Check${NC}"
echo "--------------------------------"

start_time=$(date +%s%3N)
if check_port "$API_HOST" "$MTPROTO_PORT"; then
    mtproto_response=$(make_request "http://$API_HOST:$MTPROTO_PORT/health")
    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))
    
    mtproto_status=$(parse_status "$mtproto_response" "status")
    show_service_status "MTProto Service" "$mtproto_status" "Port accessible" "$response_time"
else
    # Check if MTProto process is running
    if pgrep -f "mtproto" >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠️  MTProto Service${NC} - process running but port not accessible"
    else
        echo -e "  ${RED}❌ MTProto Service${NC} - not running"
    fi
fi

echo

# Frontend Service Health Check
echo -e "${CYAN}🌐 Frontend Service Health Check${NC}"
echo "--------------------------------"

start_time=$(date +%s%3N)
if check_port "$API_HOST" "$FRONTEND_PORT"; then
    frontend_response=$(make_request "http://$API_HOST:$FRONTEND_PORT/")
    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))
    
    if [[ "$frontend_response" == *"html"* ]] || [[ "$frontend_response" == *"<!DOCTYPE"* ]]; then
        show_service_status "Frontend Service" "healthy" "Serving content" "$response_time"
    else
        show_service_status "Frontend Service" "degraded" "Responding but may have issues" "$response_time"
    fi
else
    echo -e "  ${RED}❌ Frontend Service${NC} - port $FRONTEND_PORT not accessible"
fi

echo

# Database Health Check
echo -e "${CYAN}🗃️  Database Health Check${NC}"
echo "---------------------------"

# Check database connectivity via API
start_time=$(date +%s%3N)
db_response=$(make_request "http://$API_HOST:$API_PORT/health")
end_time=$(date +%s%3N)
response_time=$((end_time - start_time))

if [[ "$db_response" != *"error"* ]]; then
    db_healthy=$(parse_status "$db_response" "dependencies.database.healthy")
    if [[ "$db_healthy" == "true" ]]; then
        show_service_status "Database" "healthy" "Connected via API" "$response_time"
    else
        show_service_status "Database" "unhealthy" "Connection issues detected" "$response_time"
    fi
else
    echo -e "  ${RED}❌ Database${NC} - unable to check via API"
fi

echo

# System Resources Check
echo -e "${CYAN}💻 System Resources Check${NC}"
echo "---------------------------"

# Check disk space
disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [[ "$disk_usage" -lt 80 ]]; then
    echo -e "  ${GREEN}✅ Disk Space${NC} - ${disk_usage}% used"
elif [[ "$disk_usage" -lt 90 ]]; then
    echo -e "  ${YELLOW}⚠️  Disk Space${NC} - ${disk_usage}% used"
else
    echo -e "  ${RED}❌ Disk Space${NC} - ${disk_usage}% used (critical)"
fi

# Check memory usage
if command -v free >/dev/null 2>&1; then
    memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [[ "$memory_usage" -lt 80 ]]; then
        echo -e "  ${GREEN}✅ Memory Usage${NC} - ${memory_usage}%"
    elif [[ "$memory_usage" -lt 90 ]]; then
        echo -e "  ${YELLOW}⚠️  Memory Usage${NC} - ${memory_usage}%"
    else
        echo -e "  ${RED}❌ Memory Usage${NC} - ${memory_usage}% (high)"
    fi
fi

# Check load average
if command -v uptime >/dev/null 2>&1; then
    load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    echo -e "  ${BLUE}📊 Load Average${NC} - $load_avg"
fi

echo

# Docker Services Check (if running in Docker)
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo -e "${CYAN}🐳 Docker Services Check${NC}"
    echo "---------------------------"
    
    # Check if any AnalyticBot containers are running
    if docker ps --format "table {{.Names}}\\t{{.Status}}" | grep -q analyticbot; then
        echo "  Docker containers:"
        docker ps --format "  {{.Names}} - {{.Status}}" | grep analyticbot || true
    else
        echo -e "  ${YELLOW}⚠️  No AnalyticBot Docker containers detected${NC}"
    fi
    echo
fi

# Summary
echo -e "${BLUE}📋 Health Check Summary${NC}"
echo "========================"

# Count services by status (simplified)
total_checks=4  # API, Bot, MTProto, Frontend
echo "Total services checked: $total_checks"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"

echo
echo -e "${GREEN}✅ Health check completed!${NC}"
echo
echo "💡 Tips:"
echo "  • Run with VERBOSE=true for detailed output"
echo "  • Use TIMEOUT=X to adjust request timeouts"
echo "  • Check logs if services show unhealthy status"
echo "  • Ensure all required environment variables are set"