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

# ============================================================================
# Worker Process Cleanup
# ============================================================================
cleanup_workers() {
    local service_type=$1
    echo -e "${BLUE}🧹 Cleaning up old ${service_type} processes...${NC}"

    case $service_type in
        "mtproto")
            # Kill MTProto workers
            pkill -9 -f "apps.mtproto.worker" 2>/dev/null && echo -e "${GREEN}  ✅ Killed old MTProto workers${NC}" || true
            pkill -9 -f "multiprocessing.spawn" 2>/dev/null && echo -e "${GREEN}  ✅ Killed orphan spawn processes${NC}" || true
            ;;
        "bot")
            # Kill bot processes
            pkill -9 -f "apps.bot.run_bot" 2>/dev/null && echo -e "${GREEN}  ✅ Killed old bot processes${NC}" || true
            ;;
        "all")
            # Kill all workers
            pkill -9 -f "apps.mtproto.worker" 2>/dev/null && echo -e "${GREEN}  ✅ Killed old MTProto workers${NC}" || true
            pkill -9 -f "apps.bot.run_bot" 2>/dev/null && echo -e "${GREEN}  ✅ Killed old bot processes${NC}" || true
            pkill -9 -f "multiprocessing.spawn" 2>/dev/null && echo -e "${GREEN}  ✅ Killed orphan spawn processes${NC}" || true
            ;;
    esac

    # Give processes time to die
    sleep 2

    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

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
        # Clean up old bot processes first
        cleanup_workers "bot"

        # Start Bot
        start_service "bot" 'python -m apps.bot.run_bot' ""
        ;;
    "mtproto")
        # Clean up old MTProto processes first
        cleanup_workers "mtproto"

        # Start MTProto worker with lifecycle management
        start_service "mtproto" 'python -m apps.mtproto.worker --interval 10 --max-runtime 24 --memory-limit 2048 --cpu-limit 80 --health-port 9091' ""
        ;;
    "workers")
        # Start both bot and mtproto workers
        cleanup_workers "all"

        start_service "bot" 'python -m apps.bot.run_bot' ""
        start_service "mtproto" 'python -m apps.mtproto.worker --interval 10 --max-runtime 24 --memory-limit 2048 --cpu-limit 80 --health-port 9091' ""
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
        # Tunnel disabled - Using production domain analyticbot.org
        echo -e "${BLUE}🌐 Tunnel mode disabled - Using production domain${NC}"
        echo -e "${GREEN}✅ Production domain configured: https://analyticbot.org${NC}"
        echo -e "${GREEN}✅ API subdomain: https://api.analyticbot.org${NC}"
        echo -e "${BLUE}💡 Frontend uses relative URLs via Vite proxy${NC}"
        echo ""
        echo -e "${YELLOW}📝 Domain configuration:${NC}"
        echo -e "   Frontend: https://analyticbot.org or https://dev.analyticbot.org"
        echo -e "   API: https://api.analyticbot.org"
        echo -e "   All services accessible through your CloudFlare domain"
        echo ""
        return 0

        # Legacy tunnel support (commented out)
        # Check if permanent Cloudflare tunnel is configured
        if false && [ -f ".tunnel-info" ]; then
            source .tunnel-info
            echo -e "${BLUE}🌐 Starting PERMANENT Cloudflare Tunnel: ${TUNNEL_NAME}${NC}"

            # Stop any existing tunnel
            pkill -f "cloudflared tunnel" || true
            sleep 2

            # Start named tunnel
            nohup cloudflared tunnel run $TUNNEL_NAME > logs/dev_tunnel.log 2>&1 &
            tunnel_pid=$!
            echo $tunnel_pid > "logs/dev_tunnel.pid"

            echo -e "${GREEN}✅ Permanent tunnel started!${NC}"
            echo -e "${GREEN}🌐 Your PERMANENT URL: ${TUNNEL_URL}${NC}"
            echo -e "${BLUE}💡 This URL never changes!${NC}"
            echo ""
            echo -e "${YELLOW}📝 Your frontend should already have:${NC}"
            echo -e "   VITE_API_BASE_URL=${TUNNEL_URL}"

        # Check if ngrok is configured
        elif [ -f ".ngrok-config" ]; then
            source .ngrok-config
            echo -e "${BLUE}🌐 Starting ngrok tunnel...${NC}"

            # Stop any existing ngrok
            pkill ngrok || true
            sleep 2

            # Start ngrok in background
            nohup $NGROK_CMD > logs/dev_tunnel.log 2>&1 &
            tunnel_pid=$!
            echo $tunnel_pid > "logs/dev_tunnel.pid"

            sleep 3

            # Get URL from ngrok API
            TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*ngrok[^"]*' | head -1)

            if [ ! -z "$TUNNEL_URL" ]; then
                echo -e "${GREEN}✅ ngrok tunnel started!${NC}"
                echo -e "${GREEN}🌐 Public URL: ${TUNNEL_URL}${NC}"
                echo ""
                echo -e "${YELLOW}📝 Update frontend .env.local:${NC}"
                echo -e "   sed -i 's|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=${TUNNEL_URL}|g' apps/frontend/.env.local"
            else
                echo -e "${YELLOW}⚠️  Tunnel URL not found yet. Check: http://localhost:4040${NC}"
            fi

        # Fallback to random Cloudflare tunnel (TEMPORARY URL)
        else
            echo -e "${YELLOW}⚠️  No permanent tunnel configured${NC}"
            echo -e "${BLUE}💡 Setup permanent tunnel:${NC}"
            echo -e "   Cloudflare: ./scripts/setup-cloudflare-tunnel.sh (FREE, RECOMMENDED)"
            echo -e "   ngrok:      ./scripts/setup-ngrok.sh (Paid for permanent URL)"
            echo ""
            echo -e "${BLUE}🌐 Starting temporary CloudFlare Tunnel (URL changes every restart)...${NC}"

            if ! command -v cloudflared &> /dev/null; then
                echo -e "${RED}❌ cloudflared not installed${NC}"
                echo -e "${BLUE}💡 Install with: wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared-linux-amd64.deb${NC}"
                exit 1
            fi

            # Stop any existing tunnel
            pkill -f "cloudflared tunnel" || true
            sleep 2

            # Start tunnel with retry logic (CloudFlare API can be slow)
            tunnel_started=false
            for attempt in {1..3}; do
                echo -e "${BLUE}🔄 Starting tunnel (attempt $attempt/3)...${NC}"
                nohup cloudflared tunnel --url http://localhost:11300 > logs/dev_tunnel.log 2>&1 &
                tunnel_pid=$!
                echo $tunnel_pid > "logs/dev_tunnel.pid"

                echo -e "${BLUE}⏳ Waiting for tunnel URL (10 seconds)...${NC}"
                sleep 10

                # Check if tunnel actually started successfully
                if [ -f "logs/dev_tunnel.log" ]; then
                    TUNNEL_URL=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" logs/dev_tunnel.log | head -1)
                    if [ ! -z "$TUNNEL_URL" ] && kill -0 $tunnel_pid 2>/dev/null; then
                        tunnel_started=true
                        echo -e "${GREEN}✅ CloudFlare Tunnel started successfully!${NC}"
                        echo -e "${YELLOW}⚠️  TEMPORARY URL (changes every restart): ${TUNNEL_URL}${NC}"
                        break
                    fi
                fi

                echo -e "${YELLOW}⚠️  Tunnel failed to start (attempt $attempt/3)${NC}"
                kill $tunnel_pid 2>/dev/null || true
                sleep 5
            done

            # Extract tunnel URL
            if [ "$tunnel_started" = true ] && [ ! -z "$TUNNEL_URL" ]; then
                    echo ""
                    echo -e "${BLUE}ℹ️  Temporary tunnel URL available: ${TUNNEL_URL}${NC}"
                    echo -e "${YELLOW}⚠️  Using production domain (analyticbot.org) - NOT updating .env.local${NC}"
                    echo -e "${GREEN}✅ Frontend configured for production domain with proxy${NC}"
                    echo ""
                    echo -e "${BLUE}💡 Frontend will use relative URLs via Vite proxy${NC}"
                    echo -e "   Frontend: https://analyticbot.org${NC}"
                    echo -e "   API: https://analyticbot.org/health, /channels, etc.${NC}"

                    # Save tunnel info for reference only (not used by frontend)
                    echo "TUNNEL_URL=$TUNNEL_URL" > ".tunnel-current"
                    echo "UPDATED_AT=$(date -Iseconds)" >> ".tunnel-current"
                    echo "NOTE=Tunnel available but frontend uses production domain" >> ".tunnel-current"
            else
                echo -e "${RED}❌ Failed to start CloudFlare Tunnel after 3 attempts${NC}"
                echo -e "${YELLOW}💡 Check logs/dev_tunnel.log for details${NC}"
                echo -e "${YELLOW}💡 Possible causes: CloudFlare API timeout, network issues${NC}"
                echo -e "${YELLOW}💡 You can try again with: make dev-tunnel${NC}"
            fi
        fi
        ;;
    "all")
        # Domain configured - Skip tunnel generation
        echo ""
        echo -e "${BLUE}🌐 Using production domain configuration...${NC}"
        echo -e "${GREEN}✅ Domain: https://analyticbot.org${NC}"
        echo -e "${GREEN}✅ API: https://api.analyticbot.org${NC}"
        echo -e "${BLUE}💡 Temporary tunnel generation disabled${NC}"
        echo -e "${BLUE}💡 Frontend uses relative URLs via Vite proxy${NC}"
        echo ""

        echo ""
        echo -e "${BLUE}🚀 Starting backend services...${NC}"

        # Now start all services with the updated tunnel URL in .env.local
        start_service "api" 'uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --reload --log-level debug --reload-exclude venv --reload-exclude .venv --reload-exclude "*/__pycache__/*"' 11400
        sleep 2
        start_service "bot" 'python -m apps.bot.run_bot' ""
        sleep 2

        echo ""
        echo -e "${BLUE}🚀 Starting MTProto data collection worker...${NC}"

        # Clean up any zombie processes holding the health port
        if lsof -ti:9091 >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Port 9091 already in use - cleaning up zombie process...${NC}"
            ZOMBIE_PID=$(lsof -ti:9091)
            if ps -p $ZOMBIE_PID > /dev/null 2>&1; then
                echo -e "${YELLOW}🧟 Killing zombie process (PID: ${ZOMBIE_PID})${NC}"
                kill -9 $ZOMBIE_PID 2>/dev/null || true
                sleep 2
            fi
        fi

        start_service "mtproto_worker" 'python -m apps.mtproto.worker --interval 10' ""
        sleep 1

        echo ""
        echo -e "${BLUE}🚀 Starting frontend with updated tunnel URL...${NC}"
        cd apps/frontend && start_service "frontend" 'npm run dev -- --port 11300 --host 0.0.0.0' 11300 && cd ../..
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

        # Check for mtproto worker processes
        if pgrep -f "apps.mtproto.worker" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping remaining mtproto worker processes${NC}"
            pkill -f "apps.mtproto.worker" || true
        fi

        # Check for multiprocessing spawn/resource_tracker (orphaned child processes)
        if pgrep -f "multiprocessing" > /dev/null; then
            echo -e "${YELLOW}🔄 Stopping orphaned multiprocessing processes${NC}"
            pkill -f "multiprocessing.spawn" || true
            pkill -f "multiprocessing.resource_tracker" || true
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

        # Check MTProto Worker (by PID file and health endpoint)
        if [ -f "logs/dev_mtproto_worker.pid" ] && kill -0 $(cat logs/dev_mtproto_worker.pid) 2>/dev/null; then
            # Check health endpoint
            MTPROTO_HEALTH=$(curl -s http://localhost:9091/health 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', ''))" 2>/dev/null)
            if [ "$MTPROTO_HEALTH" = "healthy" ]; then
                echo -e "MTProto Worker:     ${GREEN}✅ Running & Healthy${NC}"
            elif [ "$MTPROTO_HEALTH" = "unhealthy" ]; then
                REASON=$(curl -s http://localhost:9091/health 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('reason', 'unknown'))" 2>/dev/null)
                echo -e "MTProto Worker:     ${YELLOW}⚠️  Running but unhealthy (${REASON})${NC}"
            elif [ ! -z "$MTPROTO_HEALTH" ]; then
                echo -e "MTProto Worker:     ${YELLOW}⚠️  Running (status: ${MTPROTO_HEALTH})${NC}"
            else
                echo -e "MTProto Worker:     ${GREEN}✅ Running${NC} (health check unavailable)"
            fi
        else
            echo -e "MTProto Worker:     ${RED}❌ Stopped${NC}"
        fi

        echo ""
        echo -e "${BLUE}🏥 Service Health Details:${NC}"

        # API Health
        if curl -s http://localhost:11400/health >/dev/null 2>&1; then
            API_HEALTH=$(curl -s http://localhost:11400/health 2>/dev/null)
            DB_STATUS=$(echo "$API_HEALTH" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
            REDIS_STATUS=$(echo "$API_HEALTH" | grep -o '"redis":"[^"]*"' | cut -d'"' -f4)
            if [ ! -z "$DB_STATUS" ]; then
                echo -e "  Database:         ${GREEN}✅ ${DB_STATUS}${NC}"
            fi
            if [ ! -z "$REDIS_STATUS" ]; then
                echo -e "  Redis:            ${GREEN}✅ ${REDIS_STATUS}${NC}"
            fi
        fi

        # MTProto Metrics
        if curl -s http://localhost:9091/metrics >/dev/null 2>&1; then
            MTPROTO_METRICS=$(curl -s http://localhost:9091/metrics 2>/dev/null)
            CPU=$(echo "$MTPROTO_METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['metrics'].get('cpu_percent', 0))" 2>/dev/null)
            MEM=$(echo "$MTPROTO_METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['metrics'].get('memory_mb', 0))" 2>/dev/null)
            UPTIME=$(echo "$MTPROTO_METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(int(data['metrics'].get('uptime_seconds', 0)))" 2>/dev/null)
            if [ ! -z "$CPU" ] && [ "$CPU" != "0" ]; then
                echo -e "  MTProto CPU:      ${GREEN}${CPU}%${NC}"
                echo -e "  MTProto Memory:   ${GREEN}${MEM} MB${NC}"
                if [ ! -z "$UPTIME" ] && [ "$UPTIME" != "0" ]; then
                    UPTIME_MIN=$((UPTIME / 60))
                    echo -e "  MTProto Uptime:   ${GREEN}${UPTIME_MIN} minutes${NC}"
                fi
            fi
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
