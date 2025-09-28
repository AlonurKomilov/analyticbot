#!/bin/bash
# 🔄 Sync Development to Docker
# Syncs changes from venv development to Docker containers

set -e

echo "🔄 SYNCING DEVELOPMENT TO DOCKER"
echo "================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Stop development services
echo -e "${BLUE}🛑 Stopping development services...${NC}"
./scripts/dev-start.sh stop

# Stop Docker services  
echo -e "${BLUE}🐳 Stopping Docker services...${NC}"
sudo docker-compose down

# Build fresh Docker images
echo -e "${BLUE}🔨 Building fresh Docker images...${NC}"
echo -e "${YELLOW}⏳ This may take 3-8 minutes...${NC}"

# Build with no cache to ensure fresh build
sudo docker-compose build --no-cache

# Start Docker services
echo -e "${BLUE}🚀 Starting Docker services...${NC}"
sudo docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:10300/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy${NC}"
        break
    fi
    echo -e "${YELLOW}⏳ Waiting for API... (${i}/30)${NC}"
    sleep 2
done

# Show final status
echo ""
echo -e "${GREEN}🎉 SYNC COMPLETE!${NC}"
echo "=================="
echo -e "${BLUE}🌐 Docker URLs:${NC}"
echo "  • API:      http://localhost:10300"
echo "  • API Docs: http://localhost:10300/docs"
echo "  • Frontend: http://localhost:10400"
echo ""
echo -e "${BLUE}💡 Commands:${NC}"
echo "  • make logs     - View Docker logs"
echo "  • make down     - Stop Docker services"
echo "  • make dev-start - Switch back to development mode"

# Optional: Run a quick test
if [ "$1" == "--test" ]; then
    echo ""
    echo -e "${BLUE}🧪 Running quick integration test...${NC}"
    if curl -s http://localhost:10300/health | grep -q "ok"; then
        echo -e "${GREEN}✅ Integration test passed${NC}"
    else
        echo -e "${RED}❌ Integration test failed${NC}"
        echo -e "${YELLOW}💡 Check logs: make logs${NC}"
    fi
fi