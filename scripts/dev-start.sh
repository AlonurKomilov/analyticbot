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
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv venv${NC}"
    exit 1
fi

# Activate venv
echo -e "${BLUE}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

# Load development environment variables
if [ -f ".env.dev" ]; then
    echo -e "${BLUE}⚙️  Loading development environment...${NC}"
    set -a  # automatically export all variables
    source .env.dev
    set +a  # turn off automatic export
else
    echo -e "${YELLOW}⚠️  .env.dev not found, using default .env${NC}"
    set -a  # automatically export all variables
    source .env
    set +a  # turn off automatic export
fi

# Check if required infrastructure is running
echo -e "${BLUE}🔍 Checking infrastructure...${NC}"

    # Check PostgreSQL
    if ! nc -z localhost 5432 2>/dev/null; then
        echo "⚠️  PostgreSQL not running on port 5432"
        echo "🐳 Starting PostgreSQL container..."
        docker-compose up -d db || echo "⚠️  Could not start PostgreSQL container (Docker permission issue?)"
        sleep 3
    fi
    
    # Check Redis
    if ! nc -z localhost 6379 2>/dev/null; then
        echo "⚠️  Redis not running on port 6379"
        echo "🐳 Starting Redis container..."
        docker-compose up -d redis || echo "⚠️  Could not start Redis container (Docker permission issue?)"
        sleep 2
    fi

# Function to start a service in background
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local log_file="logs/dev_${service_name}.log"
    
    # Create logs directory
    mkdir -p logs
    
    echo -e "${BLUE}🚀 Starting ${service_name} on port ${port}...${NC}"
    
    # Kill any existing process on the port
    if lsof -ti:${port} >/dev/null 2>&1; then
        echo -e "${YELLOW}🔄 Killing existing process on port ${port}${NC}"
        kill -9 $(lsof -ti:${port}) 2>/dev/null || true
        sleep 1
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
        # Start API with hot reload
        start_service "api" 'uvicorn apps.api.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug' 8001
        ;;
    "bot")
        # Start Bot
        start_service "bot" 'python -m apps.bot.run_bot' ""
        ;;
    "frontend")
        # Start Frontend (in frontend directory)
        cd apps/frontend
        if [ ! -d "node_modules" ]; then
            echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
            npm install
        fi
        start_service "frontend" 'npm run dev -- --port 5174 --host 0.0.0.0' 5174
        cd ../..
        ;;
    "all")
        # Start all services
        start_service "api" 'uvicorn apps.api.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug' 8001
        sleep 2
        start_service "bot" 'python -m apps.bot.run_bot' ""
        sleep 2
        cd apps/frontend && start_service "frontend" 'npm run dev -- --port 5174 --host 0.0.0.0' 5174 && cd ../..
        ;;
    "stop")
        # Stop all development services
        echo -e "${YELLOW}🛑 Stopping all development services...${NC}"
        for pid_file in logs/dev_*.pid; do
            if [ -f "$pid_file" ]; then
                pid=$(cat "$pid_file")
                service_name=$(basename "$pid_file" .pid | sed 's/dev_//')
                if kill -0 $pid 2>/dev/null; then
                    echo -e "${YELLOW}🔄 Stopping ${service_name} (PID: ${pid})${NC}"
                    kill $pid
                else
                    echo -e "${BLUE}ℹ️  ${service_name} already stopped${NC}"
                fi
                rm -f "$pid_file"
            fi
        done
        # Kill any remaining processes on our dev ports
        for port in 8001 5174; do
            if lsof -ti:${port} >/dev/null 2>&1; then
                echo -e "${YELLOW}🔄 Killing remaining process on port ${port}${NC}"
                kill -9 $(lsof -ti:${port}) 2>/dev/null || true
            fi
        done
        echo -e "${GREEN}✅ All services stopped${NC}"
        exit 0
        ;;
    "status")
        # Check status of all services
        echo -e "${BLUE}📊 Development Services Status:${NC}"
        echo "=================================="
        
        # Check API
        if curl -s http://localhost:8001/health >/dev/null 2>&1; then
            echo -e "API (8001):      ${GREEN}✅ Running${NC}"
        else
            echo -e "API (8001):      ${RED}❌ Stopped${NC}"
        fi
        
        # Check Frontend
        if curl -s http://localhost:5174 >/dev/null 2>&1; then
            echo -e "Frontend (5174): ${GREEN}✅ Running${NC}"
        else
            echo -e "Frontend (5174): ${RED}❌ Stopped${NC}"
        fi
        
        # Check Bot (by PID file)
        if [ -f "logs/dev_bot.pid" ] && kill -0 $(cat logs/dev_bot.pid) 2>/dev/null; then
            echo -e "Bot:             ${GREEN}✅ Running${NC}"
        else
            echo -e "Bot:             ${RED}❌ Stopped${NC}"
        fi
        
        # Check Infrastructure
        if nc -z localhost 5432 2>/dev/null; then
            echo -e "PostgreSQL:      ${GREEN}✅ Running${NC}"
        else
            echo -e "PostgreSQL:      ${RED}❌ Stopped${NC}"
        fi
        
        if nc -z localhost 6379 2>/dev/null; then
            echo -e "Redis:           ${GREEN}✅ Running${NC}"
        else
            echo -e "Redis:           ${RED}❌ Stopped${NC}"
        fi
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
        echo "  api       - Start API server with hot reload (port 8001)"
        echo "  bot       - Start Telegram bot"
        echo "  frontend  - Start frontend development server (port 5174)"
        echo "  all       - Start all services"
        echo "  stop      - Stop all services"
        echo "  status    - Check service status"
        echo "  logs [service] - Show logs for a service"
        echo ""
        echo "Examples:"
        echo "  $0 api        # Start only API"
        echo "  $0 all        # Start everything"
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
    echo "  • API:      http://localhost:8001"
    echo "  • API Docs: http://localhost:8001/docs"
    echo "  • Frontend: http://localhost:5174"
    echo ""
    echo -e "${YELLOW}📝 Note: Services run in background. Use '$0 stop' to stop them.${NC}"
fi