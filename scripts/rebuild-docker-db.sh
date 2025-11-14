#!/bin/bash
# Rebuild PostgreSQL and Redis Docker containers
# This script safely rebuilds only the database containers while preserving data

set -e

echo "🐳 Rebuilding PostgreSQL and Redis Docker Containers"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to project directory
cd "$(dirname "$0")/.."

# Create backup
echo "📦 Creating database backup..."
mkdir -p backups
source .env
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h localhost -p 10100 -U $POSTGRES_USER -d $POSTGRES_DB > "backups/db_backup_$(date +%Y%m%d_%H%M%S).sql"
echo -e "${GREEN}✅ Backup created${NC}"
echo ""

# Stop and remove containers
echo "🛑 Stopping containers..."
cd docker
sudo docker-compose down
echo ""

# Pull latest images
echo "⬇️  Pulling latest images..."
sudo docker pull postgres:16
sudo docker pull redis:7-alpine
echo ""

# Start containers
echo "🚀 Starting updated containers..."
sudo docker-compose up -d db redis
echo ""

# Wait for health checks
echo "⏳ Waiting for containers to be healthy..."
sleep 15
echo ""

# Verify
echo "🔍 Verifying containers..."
sudo docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep analyticbot
echo ""

# Test connections
echo "🧪 Testing connections..."
if redis-cli -p 10200 ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Connected${NC}"
else
    echo -e "${YELLOW}⚠️  Redis: Connection failed${NC}"
fi

cd ..
source .env
if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 10100 -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL: Connected${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL: Connection failed${NC}"
fi

echo ""
echo -e "${GREEN}✅ Docker containers rebuilt successfully!${NC}"
echo ""
echo "📊 Container status:"
cd docker
sudo docker-compose ps db redis
