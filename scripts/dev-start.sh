#!/bin/bash
# 🚀 Development Environment Startup Script
# Starts services in venv with hot-reload for rapid development

set -e

echo "🔥 STARTING VENV DEVELOPMENT ENVIRONMENT"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv .venv${NC}"
    exit 1
fi

# Activate venv
echo -e "${BLUE}🐍 Activating virtual environment...${NC}"
source .venv/bin/activate

# Load development environment variables - Clean Architecture (Two-File System)
if [ -f ".env.development" ]; then
    echo -e "${BLUE}⚙️  Loading development environment (.env.development)...${NC}"
    set -a  # automatically export all variables
    source .env.development
    # Two-file architecture: only .env.development and .env.production
    set +a  # turn off automatic export
else
    echo -e "${RED}❌ .env.development not found!${NC}"
    echo -e "${BLUE}💡 Please create .env.development from .env.development.example${NC}"
    echo -e "${BLUE}   cp .env.development.example .env.development${NC}"
    exit 1
fi

# Check if required infrastructure is running
echo -e "${BLUE}🔍 Checking infrastructure...${NC}"

# Check PostgreSQL (Docker exposes on port 10100)
if ! nc -z localhost 10100 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL not running on port 10100${NC}"
    echo -e "${BLUE}🐳 Starting PostgreSQL container...${NC}"
    docker-compose -f docker/docker-compose.yml up -d db
    echo -e "${BLUE}⏳ Waiting for PostgreSQL to be ready...${NC}"
    sleep 5
    # Wait for healthy status
    for i in {1..30}; do
        if nc -z localhost 10100 2>/dev/null; then
            echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
else
    echo -e "${GREEN}✅ PostgreSQL already running${NC}"
fi

# Check Redis (Docker exposes on port 10200)
if ! nc -z localhost 10200 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Redis not running on port 10200${NC}"
    echo -e "${BLUE}🐳 Starting Redis container...${NC}"
    docker-compose -f docker/docker-compose.yml up -d redis
    echo -e "${BLUE}⏳ Waiting for Redis to be ready...${NC}"
    sleep 3
    # Wait for healthy status
    for i in {1..15}; do
        if nc -z localhost 10200 2>/dev/null; then
            echo -e "${GREEN}✅ Redis is ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
else
    echo -e "${GREEN}✅ Redis already running${NC}"
fi

echo -e "${GREEN}✅ Infrastructure ready!${NC}"
echo ""

# Function to start a service in background
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local log_file="logs/dev_${service_name}.log"
    local skip_if_running=${4:-false}  # Optional: skip restart if already running

    # Create logs directory
    mkdir -p logs

    # Check if service is already running and healthy (optional)
    if [ "$skip_if_running" = "true" ] && lsof -ti:${port} >/dev/null 2>&1; then
        echo -e "${GREEN}✅ ${service_name} already running on port ${port} - skipping restart${NC}"
        return 0
    fi

    echo -e "${BLUE}🚀 Starting ${service_name} on port ${port}...${NC}"

    # Gracefully stop any existing process on the port
    if lsof -ti:${port} >/dev/null 2>&1; then
        echo -e "${YELLOW}🔄 Stopping existing process on port ${port}${NC}"
        # First try graceful shutdown (SIGTERM)
        kill $(lsof -ti:${port}) 2>/dev/null || true
        sleep 2
        # If still running, force kill
        if lsof -ti:${port} >/dev/null 2>&1; then
            echo -e "${YELLOW}⚡ Force stopping process on port ${port}${NC}"
            kill -9 $(lsof -ti:${port}) 2>/dev/null || true
            sleep 1
        fi
    fi

    # Start the service
    nohup bash -c "${command}" > ${log_file} 2>&1 &
    local pid=$!
    echo $pid > "logs/dev_${service_name}.pid"

    # Wait a moment and check if it started
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✅ ${service_name} started (PID: ${pid})${NC}"
        echo -e "${BLUE}   Log: ${log_file}${NC}"
        echo -e "${BLUE}   URL: http://localhost:${port}${NC}"
    else
        echo -e "${RED}❌ Failed to start ${service_name}${NC}"
        cat ${log_file}
    fi
}

# Parse command line arguments
SERVICE=""
if [ $# -gt 0 ]; then
    SERVICE=$1
fi

case $SERVICE in
    "api"|"")
        # Start API with 2 workers - Development Environment Port 11400
        # Note: --reload is disabled when using multiple workers
        start_service "api" 'uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --workers 2 --log-level debug' 11400
        ;;
    "bot")
        # Start Bot
        start_service "bot" 'python -m apps.bot.run_bot' ""
        ;;
    "frontend")
        # Start Frontend (in frontend directory) - Development Environment Port 11300
        cd apps/frontend
        if [ ! -d "node_modules" ]; then
            echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
            npm install
        fi
        start_service "frontend" 'npm run dev -- --port 11300 --host 0.0.0.0' 11300
        cd ../..
        ;;
    "tunnel")
        # Start CloudFlare Tunnel for public access (3-10x faster than DevTunnel)
        if ! command -v cloudflared &> /dev/null; then
            echo -e "${RED}❌ cloudflared not installed${NC}"
            echo -e "${BLUE}💡 Install with: wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb${NC}"
            exit 1
        fi

        # Stop any existing CloudFlare tunnel first
        if pgrep -f "cloudflared tunnel --url" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping existing CloudFlare Tunnel...${NC}"
            pkill -f "cloudflared tunnel --url" || true
            sleep 2
        fi

        echo -e "${BLUE}🌐 Starting CloudFlare Tunnel...${NC}"
        nohup cloudflared tunnel --url http://localhost:11400 > logs/dev_tunnel.log 2>&1 &
        local tunnel_pid=$!
        echo $tunnel_pid > "logs/dev_tunnel.pid"

        echo -e "${BLUE}⏳ Waiting for tunnel URL...${NC}"
        sleep 5

        # Extract tunnel URL
        if [ -f "logs/dev_tunnel.log" ]; then
            TUNNEL_URL=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" logs/dev_tunnel.log | head -1)
            if [ ! -z "$TUNNEL_URL" ]; then
                echo -e "${GREEN}✅ CloudFlare Tunnel started!${NC}"
                echo -e "${GREEN}🌐 Public URL: ${TUNNEL_URL}${NC}"
                echo -e "${BLUE}💡 Update apps/frontend/.env.local with:${NC}"
                echo -e "   VITE_API_BASE_URL=${TUNNEL_URL}"
                echo ""
                echo -e "${YELLOW}📝 Run this command to update .env.local automatically:${NC}"
                echo -e "   sed -i 's|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=${TUNNEL_URL}|g' apps/frontend/.env.local"
                echo -e "   sed -i 's|VITE_API_URL=.*|VITE_API_URL=${TUNNEL_URL}|g' apps/frontend/.env.local"
            else
                echo -e "${YELLOW}⚠️  Tunnel URL not found yet. Check logs/dev_tunnel.log${NC}"
            fi
        fi
        ;;
    "all")
        # Start all services - Development Environment Ports 11xxx
        start_service "api" 'uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --reload --log-level debug --reload-exclude venv --reload-exclude .venv --reload-exclude "*/__pycache__/*"' 11400
        sleep 2
        start_service "bot" 'python -m apps.bot.run_bot' ""
        sleep 2
        cd apps/frontend && start_service "frontend" 'npm run dev -- --port 11300 --host 0.0.0.0' 11300 && cd ../..
        sleep 2

        # Start CloudFlare Tunnel for public access
        echo ""
        echo -e "${BLUE}🌐 Starting CloudFlare Tunnel for public access...${NC}"

        # Stop any existing CloudFlare tunnel first
        if pgrep -f "cloudflared tunnel --url" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping existing CloudFlare Tunnel...${NC}"
            pkill -f "cloudflared tunnel --url" || true
            sleep 2
        fi

        if command -v cloudflared &> /dev/null; then
            nohup cloudflared tunnel --url http://localhost:11400 > logs/dev_tunnel.log 2>&1 &
            tunnel_pid=$!
            echo $tunnel_pid > "logs/dev_tunnel.pid"

            echo -e "${BLUE}⏳ Waiting for tunnel URL...${NC}"
            sleep 5

            # Extract tunnel URL
            if [ -f "logs/dev_tunnel.log" ]; then
                TUNNEL_URL=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" logs/dev_tunnel.log | head -1)
                if [ ! -z "$TUNNEL_URL" ]; then
                    echo -e "${GREEN}✅ CloudFlare Tunnel started!${NC}"
                    echo -e "${GREEN}🌐 Public URL: ${TUNNEL_URL}${NC}"
                    echo ""
                    echo -e "${YELLOW}📝 To use this tunnel, update your frontend:${NC}"
                    echo -e "   sed -i 's|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=${TUNNEL_URL}|g' apps/frontend/.env.local"
                    echo -e "   sed -i 's|VITE_API_URL=.*|VITE_API_URL=${TUNNEL_URL}|g' apps/frontend/.env.local"
                    echo -e "   Then restart frontend: ./scripts/dev-start.sh stop && make dev-start"
                else
                    echo -e "${YELLOW}⚠️  Tunnel URL not found yet. Check logs/dev_tunnel.log${NC}"
                fi
            fi
        else
            echo -e "${YELLOW}⚠️  cloudflared not installed - skipping tunnel${NC}"
            echo -e "${BLUE}💡 Install with: wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb${NC}"
        fi
        ;;
    "stop")
        # Stop all development services
        echo -e "${YELLOW}🛑 Stopping all development services...${NC}"

        # Stop services by PID file (safer approach)
        for pid_file in logs/dev_*.pid; do
            if [ -f "$pid_file" ]; then
                pid=$(cat "$pid_file")
                service_name=$(basename "$pid_file" .pid | sed 's/dev_//')
                if kill -0 $pid 2>/dev/null; then
                    echo -e "${YELLOW}🔄 Stopping ${service_name} (PID: ${pid})${NC}"
                    kill $pid
                    # Wait for graceful shutdown
                    sleep 2
                    # Force kill if still running
                    if kill -0 $pid 2>/dev/null; then
                        echo -e "${YELLOW}⚡ Force stopping ${service_name}${NC}"
                        kill -9 $pid 2>/dev/null || true
                    fi
                else
                    echo -e "${BLUE}ℹ️  ${service_name} already stopped${NC}"
                fi
                rm -f "$pid_file"
            fi
        done

        # More selective port cleanup - only kill our specific processes
        echo -e "${BLUE}🔍 Checking for remaining development processes...${NC}"

        # Check for uvicorn (API) processes specifically
        if pgrep -f "uvicorn.*11400" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping remaining API processes${NC}"
            pkill -f "uvicorn.*11400" || true
        fi

        # Check for npm/vite (Frontend) processes specifically
        if pgrep -f "vite.*11300" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping remaining frontend processes${NC}"
            pkill -f "vite.*11300" || true
        fi

        # Check for bot processes
        if pgrep -f "apps.bot.run_bot" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping remaining bot processes${NC}"
            pkill -f "apps.bot.run_bot" || true
        fi

        # Check for CloudFlare Tunnel processes (NOT VS Code tunnel!)
        if pgrep -f "cloudflared tunnel --url" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping CloudFlare Tunnel${NC}"
            pkill -f "cloudflared tunnel --url" || true
        fi

        echo -e "${GREEN}✅ All development services stopped${NC}"
        exit 0
        ;;
    "status")
        # Check status of all services
        echo -e "${BLUE}📊 Development Services Status:${NC}"
        echo "=================================="
        echo ""
        echo -e "${BLUE}🐳 Infrastructure (Docker):${NC}"

        # Check PostgreSQL (port 10100)
        if nc -z localhost 10100 2>/dev/null; then
            echo -e "PostgreSQL (10100): ${GREEN}✅ Running${NC}"
        else
            echo -e "PostgreSQL (10100): ${RED}❌ Stopped${NC}"
        fi

        # Check Redis (port 10200)
        if nc -z localhost 10200 2>/dev/null; then
            echo -e "Redis (10200):      ${GREEN}✅ Running${NC}"
        else
            echo -e "Redis (10200):      ${RED}❌ Stopped${NC}"
        fi

        echo ""
        echo -e "${BLUE}🔥 Development Services (venv):${NC}"

        # Check API - Development Environment Port 11400
        if curl -s http://localhost:11400/health >/dev/null 2>&1; then
            echo -e "API (11400):        ${GREEN}✅ Running${NC}"
        else
            echo -e "API (11400):        ${RED}❌ Stopped${NC}"
        fi

        # Check Frontend - Development Environment Port 11300
        if curl -s http://localhost:11300 >/dev/null 2>&1; then
            echo -e "Frontend (11300):   ${GREEN}✅ Running${NC}"
        else
            echo -e "Frontend (11300):   ${RED}❌ Stopped${NC}"
        fi

        # Check Bot (by PID file)
        if [ -f "logs/dev_bot.pid" ] && kill -0 $(cat logs/dev_bot.pid) 2>/dev/null; then
            echo -e "Bot:                ${GREEN}✅ Running${NC}"
        else
            echo -e "Bot:                ${RED}❌ Stopped${NC}"
        fi

        echo ""
        echo -e "${BLUE}🌐 Public Access (CloudFlare Tunnel):${NC}"

        # Check CloudFlare Tunnel
        if [ -f "logs/dev_tunnel.pid" ] && kill -0 $(cat logs/dev_tunnel.pid) 2>/dev/null; then
            TUNNEL_URL=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" logs/dev_tunnel.log 2>/dev/null | head -1)
            if [ ! -z "$TUNNEL_URL" ]; then
                echo -e "Tunnel:             ${GREEN}✅ Running${NC}"
                echo -e "Public URL:         ${GREEN}${TUNNEL_URL}${NC}"
            else
                echo -e "Tunnel:             ${YELLOW}⚠️  Starting (no URL yet)${NC}"
            fi
        else
            echo -e "Tunnel:             ${RED}❌ Stopped${NC}"
            echo -e "${BLUE}💡 Start with: make dev-tunnel${NC}"
        fi

        echo ""
        echo -e "${BLUE}💡 Tip: Use 'make dev-start' to start all services${NC}"
        exit 0
        ;;
    "logs")
        # Show logs for a service
        if [ $# -gt 1 ]; then
            service_name=$2
            log_file="logs/dev_${service_name}.log"
            if [ -f "$log_file" ]; then
                echo -e "${BLUE}📋 Showing logs for ${service_name}:${NC}"
                tail -f "$log_file"
            else
                echo -e "${RED}❌ Log file not found: ${log_file}${NC}"
            fi
        else
            echo -e "${YELLOW}Available logs:${NC}"
            ls -la logs/dev_*.log 2>/dev/null || echo "No log files found"
        fi
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Usage: $0 [service]${NC}"
        echo ""
        echo "Services:"
        echo "  api       - Start API server with hot reload (port 11400)"
        echo "  bot       - Start Telegram bot"
        echo "  frontend  - Start frontend development server (port 11300)"
        echo "  tunnel    - Start CloudFlare Tunnel for public access (3-10x faster)"
        echo "  all       - Start all services including tunnel"
        echo "  stop      - Stop all services"
        echo "  status    - Check service status"
        echo "  logs [service] - Show logs for a service"
        echo ""
        echo "Examples:"
        echo "  $0 api        # Start only API"
        echo "  $0 tunnel     # Start CloudFlare Tunnel"
        echo "  $0 all        # Start everything (recommended)"
        echo "  $0 status     # Check what's running"
        echo "  $0 logs api   # Show API logs"
        exit 1
        ;;
esac

if [ "$SERVICE" != "stop" ] && [ "$SERVICE" != "status" ] && [ "$SERVICE" != "logs" ]; then
    echo ""
    echo -e "${GREEN}🎉 Development environment ready!${NC}"
    echo "=================================="
    echo -e "${BLUE}💡 Quick commands:${NC}"
    echo "  • $0 status    - Check service status"
    echo "  • $0 logs api  - Show API logs"
    echo "  • $0 stop      - Stop all services"
    echo ""
    echo -e "${BLUE}🌐 Development URLs:${NC}"
    echo "  • API:      http://localhost:11400"
    echo "  • API Docs: http://localhost:11400/docs"
    echo "  • Frontend: http://localhost:11300"
    echo ""
    echo -e "${YELLOW}📝 Note: Services run in background. Use '$0 stop' to stop them.${NC}"
fi
