#!/bin/bash
set -e

# AnalyticBot Full Stack Deployment Script
# This script sets up and runs the complete system:
# - API Backend (FastAPI)
# - Bot Service (Aiogram)
# - Frontend (React/Vite)
# - Database (PostgreSQL/SQLite)
# - Cache (Redis - optional)

echo "🚀 AnalyticBot Full Stack Deployment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEVELOPMENT_MODE=${DEVELOPMENT_MODE:-true}
USE_DOCKER=${USE_DOCKER:-false}
SETUP_FRONTEND=${SETUP_FRONTEND:-true}
PORT_API=${PORT_API:-8000}
PORT_FRONTEND=${PORT_FRONTEND:-3000}

echo -e "${BLUE}Configuration:${NC}"
echo "  Development Mode: $DEVELOPMENT_MODE"
echo "  Use Docker: $USE_DOCKER"
echo "  Setup Frontend: $SETUP_FRONTEND"
echo "  API Port: $PORT_API"
echo "  Frontend Port: $PORT_FRONTEND"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running in project directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Project root directory confirmed"

# Set up environment variables for development
export DATABASE_URL="sqlite:///data/analytics.db"
export ADMIN_IDS="8034732332"
export BOT_TOKEN=${BOT_TOKEN:-"your_bot_token_here"}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-"dev_secret_key_123"}
export TWA_HOST_URL=${TWA_HOST_URL:-"http://localhost:3000"}
export POSTGRES_USER=${POSTGRES_USER:-"analytic"}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"change_me"}
export POSTGRES_DB=${POSTGRES_DB:-"analytic_bot"}

print_status "Environment variables set for development"

# Create data directory
mkdir -p data logs pids
print_status "Data directory created"

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1

    echo -n "Waiting for $url "
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo ""
            print_status "Service at $url is ready"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo ""
    print_error "Service at $url failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Python virtual environment setup
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found, creating one..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
.venv/bin/pip install -r requirements.txt > /dev/null 2>&1

# Database setup
if [ "$DATABASE_URL" = "sqlite:///data/analytics.db" ]; then
    print_status "Using SQLite database for development"
    if [ ! -f "data/analytics.db" ]; then
        # Run migrations
        .venv/bin/python -m alembic upgrade head
        print_status "Database migrations applied"
    fi
else
    print_status "Database configuration detected, skipping SQLite setup"
fi

# Frontend setup
if [ "$SETUP_FRONTEND" = "true" ]; then
    echo -e "${BLUE}Setting up Frontend...${NC}"

    if [ -d "apps/frontend" ]; then
        cd apps/frontend

        # Check if node is available
        if command -v node > /dev/null 2>&1; then
            print_status "Node.js found: $(node --version)"

            # Install dependencies
            if [ -f "package.json" ]; then
                if [ ! -d "node_modules" ]; then
                    print_status "Installing frontend dependencies..."
                    npm install > /dev/null 2>&1
                fi
                print_status "Frontend dependencies ready"
            fi
        else
            print_warning "Node.js not found, frontend will not be built"
            SETUP_FRONTEND=false
        fi

        cd ../..
    else
        print_warning "Frontend directory not found"
        SETUP_FRONTEND=false
    fi
fi

# Docker deployment
if [ "$USE_DOCKER" = "true" ]; then
    echo -e "${BLUE}Starting Docker services...${NC}"

    # Check if Docker is available
    if command -v docker > /dev/null 2>&1 && command -v docker-compose > /dev/null 2>&1; then
        # Stop existing containers
        docker-compose down > /dev/null 2>&1 || true

        # Start services
        docker-compose up -d db redis
        print_status "Database and Redis started"

        # Wait for database
        sleep 10

        # Start application services
        docker-compose up -d api bot
        print_status "API and Bot services started"

        # Wait for API to be ready
        if wait_for_service "http://localhost:$PORT_API/health"; then
            print_status "Docker deployment successful"
        else
            print_error "Docker deployment failed"
            exit 1
        fi
    else
        print_error "Docker or docker-compose not available"
        exit 1
    fi

# Local development deployment
else
    echo -e "${BLUE}Starting local development services...${NC}"

    # Check ports
    if ! check_port $PORT_API; then
        print_error "API port $PORT_API is in use. Please stop other services or change the port."
        exit 1
    fi

    if [ "$SETUP_FRONTEND" = "true" ]; then
        if ! check_port $PORT_FRONTEND; then
            print_warning "Frontend port $PORT_FRONTEND is in use"
        fi
    fi

    # Start API service
    echo -e "${BLUE}Starting API service...${NC}"
    .venv/bin/python -m uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT_API > logs/api.log 2>&1 &
    API_PID=$!
    echo "API PID: $API_PID" > pids/api.pid

    # Wait for API to be ready
    if wait_for_service "http://localhost:$PORT_API/health"; then
        print_status "API service started successfully"
    else
        print_error "API service failed to start"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi

    # Start Bot service
    echo -e "${BLUE}Starting Bot service...${NC}"
    .venv/bin/python apps/bot/run_bot.py > logs/bot.log 2>&1 &
    BOT_PID=$!
    echo "Bot PID: $BOT_PID" > pids/bot.pid
    sleep 3

    if ps -p $BOT_PID > /dev/null; then
        print_status "Bot service started successfully"
    else
        print_error "Bot service failed to start"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi

    # Start Frontend service
    if [ "$SETUP_FRONTEND" = "true" ]; then
        echo -e "${BLUE}Starting Frontend service...${NC}"
        cd apps/frontend
        VITE_API_URL="http://localhost:$PORT_API" npm run dev -- --port $PORT_FRONTEND --host > ../../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo "Frontend PID: $FRONTEND_PID" > ../../pids/frontend.pid
        cd ../..

        sleep 5
        if ps -p $FRONTEND_PID > /dev/null; then
            print_status "Frontend service started successfully"
        else
            print_warning "Frontend service may have issues, check logs/frontend.log"
        fi
    fi
fi

# Create directories for logs and PIDs
mkdir -p logs pids

# Service status check
echo ""
echo -e "${BLUE}Service Status Check:${NC}"
echo "===================="

# Check API
if curl -s "http://localhost:$PORT_API/health" > /dev/null 2>&1; then
    API_STATUS=$(curl -s "http://localhost:$PORT_API/health" | grep -o '"status":"[^"]*"' || echo '"status":"unknown"')
    print_status "API: $API_STATUS - http://localhost:$PORT_API"
else
    print_error "API: Not responding - http://localhost:$PORT_API"
fi

# Check Bot (by checking if process is running)
if [ -f "pids/bot.pid" ] && ps -p $(cat pids/bot.pid) > /dev/null 2>&1; then
    print_status "Bot: Running - Check logs/bot.log for details"
else
    if [ "$USE_DOCKER" = "true" ]; then
        if docker ps | grep -q "analyticbot-bot"; then
            print_status "Bot: Running (Docker)"
        else
            print_error "Bot: Not running (Docker)"
        fi
    else
        print_error "Bot: Not running"
    fi
fi

# Check Frontend
if [ "$SETUP_FRONTEND" = "true" ]; then
    if curl -s "http://localhost:$PORT_FRONTEND" > /dev/null 2>&1; then
        print_status "Frontend: Running - http://localhost:$PORT_FRONTEND"
    else
        print_warning "Frontend: Not responding - http://localhost:$PORT_FRONTEND"
    fi
fi

# Summary
echo ""
echo -e "${GREEN}🎉 Deployment Summary:${NC}"
echo "======================"
echo "API Endpoint:      http://localhost:$PORT_API"
echo "API Health:        http://localhost:$PORT_API/health"
echo "API Docs:          http://localhost:$PORT_API/docs"
if [ "$SETUP_FRONTEND" = "true" ]; then
    echo "Frontend:          http://localhost:$PORT_FRONTEND"
    echo "TWA URL:           http://localhost:$PORT_FRONTEND (for Telegram Web App)"
fi
echo "Database:          $DATABASE_URL"
echo "Logs Directory:    ./logs/"
echo ""

# Management commands
echo -e "${YELLOW}Management Commands:${NC}"
echo "==================="
if [ "$USE_DOCKER" = "true" ]; then
    echo "Stop all services: docker-compose down"
    echo "View logs:         docker-compose logs -f"
    echo "Restart services:  docker-compose restart"
else
    echo "Stop all services: ./scripts/stop_services.sh"
    echo "View logs:         tail -f logs/*.log"
    echo "API logs:          tail -f logs/api.log"
    echo "Bot logs:          tail -f logs/bot.log"
    if [ "$SETUP_FRONTEND" = "true" ]; then
        echo "Frontend logs:     tail -f logs/frontend.log"
    fi
fi
echo ""

print_status "Full stack deployment completed successfully!"
echo ""
echo -e "${GREEN}Ready for testing and development! 🚀${NC}"
