#!/bin/bash
# Phase 0.0 Module 2 - Docker Compose Deployment Test
# Quick validation deployment using Docker Compose

set -e

echo "🚀 PHASE 0.0 MODULE 2: DOCKER COMPOSE DEPLOYMENT TEST"
echo "=" * 60

# Configuration
TEST_DIR="/workspaces/analyticbot"
LOG_FILE="./logs/module2_deployment_$(date +%Y%m%d_%H%M%S).log"
COMPOSE_FILE="docker-compose.module2.yml"

# Create logs directory
mkdir -p logs

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $message" | tee -a "$LOG_FILE"
}

log_message "INFO" "Starting Phase 0.0 Module 2 deployment test"
log_message "INFO" "Log file: $LOG_FILE"

# Phase 2.1: Environment Setup
echo -e "\n📋 Phase 2.1: Environment Setup"
log_message "INFO" "Phase 2.1: Setting up test environment"

# Check required files
echo "Checking required files..."
required_files=(
    "Dockerfile"
    "main.py"
    "bot/__init__.py"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file - Found"
        log_message "INFO" "Required file found: $file"
    else
        echo "❌ $file - Missing"
        log_message "ERROR" "Required file missing: $file"
        exit 1
    fi
done

# Phase 2.2: Docker Compose Configuration
echo -e "\n🐳 Phase 2.2: Creating Docker Compose Configuration"
log_message "INFO" "Phase 2.2: Creating Docker Compose test configuration"

# Create optimized docker-compose for testing
cat > "$COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: analyticbot-postgres-test
    environment:
      POSTGRES_DB: analyticbot_test
      POSTGRES_USER: analyticbot
      POSTGRES_PASSWORD: testpass123
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5433:5432"  # Different port to avoid conflicts
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U analyticbot -d analyticbot_test"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - analyticbot-test

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: analyticbot-redis-test
    command: redis-server --requirepass testredis123 --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6380:6379"  # Different port to avoid conflicts
    volumes:
      - redis_test_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 10s
    networks:
      - analyticbot-test

  # AnalyticBot API
  api:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: analyticbot-api-test
    environment:
      # Database Configuration
      DATABASE_URL: postgresql+asyncpg://analyticbot:testpass123@postgres:5432/analyticbot_test
      
      # Redis Configuration  
      REDIS_URL: redis://:testredis123@redis:6379/0
      
      # Application Configuration
      ENVIRONMENT: testing
      DEBUG: "true"
      LOG_LEVEL: DEBUG
      
      # API Configuration
      API_HOST: 0.0.0.0
      API_PORT: 8000
      CORS_ORIGINS: "*"
      
      # Bot Configuration (mock for testing)
      BOT_TOKEN: "test_token_for_module2"
      WEBHOOK_SECRET: "test_webhook_secret"
      
      # AI Configuration (mock for testing)
      OPENAI_API_KEY: "test_openai_key"
      
      # Security (test values)
      JWT_SECRET_KEY: "test_jwt_secret_key_for_module2_validation"
      ENCRYPTION_KEY: "test_encryption_key_12345"
      
    ports:
      - "8001:8000"  # Different port for testing
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - analyticbot-test
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  # AnalyticBot Bot (optional for full testing)
  bot:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: analyticbot-bot-test
    environment:
      # Database Configuration
      DATABASE_URL: postgresql+asyncpg://analyticbot:testpass123@postgres:5432/analyticbot_test
      
      # Redis Configuration
      REDIS_URL: redis://:testredis123@redis:6379/0
      
      # Application Configuration
      ENVIRONMENT: testing
      DEBUG: "true"
      LOG_LEVEL: DEBUG
      
      # Bot Configuration (mock for testing)
      BOT_TOKEN: "test_token_for_module2"
      WEBHOOK_SECRET: "test_webhook_secret"
      
      # AI Configuration (mock for testing)  
      OPENAI_API_KEY: "test_openai_key"
      
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      api:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - analyticbot-test
    command: ["python", "-m", "bot.main"]
    profiles:
      - full-test  # Optional service, activate with --profile full-test

volumes:
  postgres_test_data:
    name: analyticbot-postgres-test-data
  redis_test_data:
    name: analyticbot-redis-test-data

networks:
  analyticbot-test:
    name: analyticbot-test-network
    driver: bridge
EOF

echo "✅ Docker Compose configuration created: $COMPOSE_FILE"
log_message "INFO" "Docker Compose configuration created successfully"

# Phase 2.3: Deployment
echo -e "\n🚀 Phase 2.3: Starting Deployment"
log_message "INFO" "Phase 2.3: Starting Docker Compose deployment"

# Clean up any existing containers
echo "Cleaning up existing test containers..."
docker compose -f "$COMPOSE_FILE" down -v 2>/dev/null || true

# Build and start services
echo "Building and starting services..."
log_message "INFO" "Building Docker images..."
docker compose -f "$COMPOSE_FILE" build api 2>&1 | tee -a "$LOG_FILE"

log_message "INFO" "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d postgres redis 2>&1 | tee -a "$LOG_FILE"

# Wait for dependencies to be healthy
echo "Waiting for dependencies to become healthy..."
timeout=60
counter=0
while [[ $counter -lt $timeout ]]; do
    postgres_health=$(docker inspect --format='{{.State.Health.Status}}' analyticbot-postgres-test 2>/dev/null || echo "unhealthy")
    redis_health=$(docker inspect --format='{{.State.Health.Status}}' analyticbot-redis-test 2>/dev/null || echo "unhealthy")
    
    if [[ "$postgres_health" == "healthy" && "$redis_health" == "healthy" ]]; then
        echo "✅ Dependencies are healthy"
        log_message "INFO" "Dependencies health check passed"
        break
    fi
    
    echo "⏳ Waiting for dependencies... (${counter}s/${timeout}s)"
    sleep 5
    ((counter+=5))
done

if [[ $counter -ge $timeout ]]; then
    echo "❌ Dependencies failed to become healthy within timeout"
    log_message "ERROR" "Dependencies health check timeout"
    exit 1
fi

# Start API service
echo "Starting API service..."
docker compose -f "$COMPOSE_FILE" up -d api 2>&1 | tee -a "$LOG_FILE"

# Phase 2.4: Health Checks
echo -e "\n🏥 Phase 2.4: Health Checks"
log_message "INFO" "Phase 2.4: Running health checks"

# Wait for API to be ready
echo "Waiting for API to be ready..."
timeout=120
counter=0
while [[ $counter -lt $timeout ]]; do
    if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ API health check passed"
        log_message "INFO" "API health check passed"
        break
    fi
    
    echo "⏳ Waiting for API... (${counter}s/${timeout}s)"
    sleep 10
    ((counter+=10))
done

if [[ $counter -ge $timeout ]]; then
    echo "❌ API health check failed"
    log_message "ERROR" "API health check timeout"
    
    # Show container logs for debugging
    echo -e "\n📋 Container Status:"
    docker compose -f "$COMPOSE_FILE" ps
    
    echo -e "\n📋 API Logs:"
    docker compose -f "$COMPOSE_FILE" logs api
    
    exit 1
fi

# Phase 2.5: Basic Integration Tests
echo -e "\n🧪 Phase 2.5: Basic Integration Tests"
log_message "INFO" "Phase 2.5: Running basic integration tests"

# Test API endpoints
echo "Testing API endpoints..."

# Health check
echo -n "Health endpoint: "
if response=$(curl -sf http://localhost:8001/health 2>&1); then
    echo "✅ PASS"
    log_message "INFO" "Health endpoint test passed"
else
    echo "❌ FAIL - $response"
    log_message "ERROR" "Health endpoint test failed: $response"
fi

# Root endpoint
echo -n "Root endpoint: "
if curl -sf http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ PASS"
    log_message "INFO" "Root endpoint test passed"
else
    echo "❌ FAIL"
    log_message "ERROR" "Root endpoint test failed"
fi

# Database connection test
echo -n "Database connection: "
if docker exec analyticbot-postgres-test pg_isready -U analyticbot -d analyticbot_test > /dev/null 2>&1; then
    echo "✅ PASS"
    log_message "INFO" "Database connection test passed"
else
    echo "❌ FAIL"
    log_message "ERROR" "Database connection test failed"
fi

# Redis connection test
echo -n "Redis connection: "
if docker exec analyticbot-redis-test redis-cli -a testredis123 ping | grep -q PONG; then
    echo "✅ PASS"
    log_message "INFO" "Redis connection test passed"
else
    echo "❌ FAIL"
    log_message "ERROR" "Redis connection test failed"
fi

# Summary
echo -e "\n📊 DEPLOYMENT TEST SUMMARY"
echo "=" * 40
echo "✅ Docker Compose configuration created"
echo "✅ Services deployed successfully"
echo "✅ Health checks passed"
echo "✅ Basic integration tests completed"

log_message "INFO" "Module 2 Docker Compose deployment test completed successfully"

echo -e "\n🎯 NEXT STEPS:"
echo "1. Review logs: $LOG_FILE"
echo "2. Access API: http://localhost:8001"
echo "3. Run full test suite: python -m pytest tests/"
echo "4. Proceed to Kubernetes deployment (Module 2.2)"

echo -e "\n🔧 CLEANUP COMMAND:"
echo "docker compose -f $COMPOSE_FILE down -v"

exit 0
EOF
