#!/bin/bash

# 🚀 PHASE 5.0: Production Deployment Script
# Enterprise-grade deployment automation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/infrastructure/docker"
ENV_FILE="$PROJECT_ROOT/.env"
LOG_FILE="/var/log/analyticbot-deploy.log"

# Deployment configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
VERSION="${VERSION:-$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')}"
BUILD_DATE="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Trap function for cleanup
cleanup() {
    info "Cleaning up temporary files..."
    # Add cleanup logic here if needed
}

trap cleanup EXIT

# Header
echo -e "${PURPLE}"
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                     🏢 ANALYTICBOT ENTERPRISE DEPLOYMENT                        ║"
echo "║                              Phase 5.0 Production                              ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Pre-deployment checks
log "🔍 Starting pre-deployment checks..."

# Check if running as root (not recommended for production)
if [[ $EUID -eq 0 ]]; then
    warning "Running as root. Consider using a dedicated deployment user for better security."
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed or not in PATH"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error "Docker Compose is not installed or not in PATH"
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    error "Docker daemon is not running"
fi

success "✅ Docker checks passed"

# Check environment file
if [[ ! -f "$ENV_FILE" ]]; then
    error "Environment file not found at $ENV_FILE"
fi

# Load environment variables
if ! source "$ENV_FILE"; then
    error "Failed to load environment variables from $ENV_FILE"
fi

# Validate critical environment variables
REQUIRED_VARS=("BOT_TOKEN" "POSTGRES_PASSWORD" "STORAGE_CHANNEL_ID")
for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        error "Required environment variable $var is not set"
    fi
done

success "✅ Environment validation passed"

# Check available disk space (minimum 5GB)
AVAILABLE_SPACE=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
MIN_SPACE=5242880  # 5GB in KB

if [[ $AVAILABLE_SPACE -lt $MIN_SPACE ]]; then
    error "Insufficient disk space. Required: 5GB, Available: $((AVAILABLE_SPACE/1048576))GB"
fi

success "✅ Disk space check passed"

# Check memory (minimum 2GB recommended)
AVAILABLE_MEMORY=$(free -m | awk 'NR==2{print $7}')
MIN_MEMORY=2048

if [[ $AVAILABLE_MEMORY -lt $MIN_MEMORY ]]; then
    warning "Low available memory: ${AVAILABLE_MEMORY}MB. Recommended: 2048MB+"
fi

success "✅ System resource checks passed"

# Build phase
log "🔨 Starting build phase..."

cd "$PROJECT_ROOT"

# Create necessary directories
mkdir -p logs data temp

# Build production image
info "Building production Docker image..."
docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VCS_REF="$VERSION" \
    --build-arg VERSION="$VERSION" \
    -f "$DOCKER_DIR/Dockerfile.prod" \
    -t analyticbot:$VERSION \
    -t analyticbot:latest \
    .

success "✅ Production image built successfully"

# Database migration
log "🗄️  Preparing database..."

# Start database services first
docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" up -d postgres redis

# Wait for database to be ready
info "Waiting for database to be ready..."
sleep 10

# Run database migrations
info "Running database migrations..."
docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" run --rm api alembic upgrade head

success "✅ Database preparation completed"

# Deployment phase
log "🚀 Starting deployment phase..."

# Stop existing services gracefully
if docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" ps -q | grep -q .; then
    info "Stopping existing services..."
    docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" down --timeout 30
fi

# Start all services
info "Starting production services..."
docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" up -d

# Wait for services to be ready
info "Waiting for services to start..."
sleep 15

# Health checks
log "🏥 Performing health checks..."

# API health check
for i in {1..10}; do
    if curl -f -s http://localhost:8000/health > /dev/null; then
        success "✅ API service is healthy"
        break
    fi
    if [[ $i -eq 10 ]]; then
        error "API service failed health check"
    fi
    info "Waiting for API service... (attempt $i/10)"
    sleep 10
done

# Database health check
if docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" exec -T postgres pg_isready -U "${POSTGRES_USER:-analyticuser}" > /dev/null; then
    success "✅ Database is healthy"
else
    error "Database health check failed"
fi

# Redis health check
if docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" exec -T redis redis-cli ping | grep -q "PONG"; then
    success "✅ Redis is healthy"
else
    error "Redis health check failed"
fi

# Post-deployment tasks
log "📋 Running post-deployment tasks..."

# Create deployment record
DEPLOYMENT_INFO="deployment_$(date +%Y%m%d_%H%M%S).json"
cat > "$DEPLOYMENT_INFO" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "$VERSION",
  "environment": "$ENVIRONMENT",
  "services": [
    $(docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" ps --services | jq -R . | jq -s .)
  ],
  "health_status": "healthy"
}
EOF

success "✅ Deployment record created: $DEPLOYMENT_INFO"

# Display deployment summary
log "📊 Deployment Summary"
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                            DEPLOYMENT COMPLETED                               ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "🌐 API Endpoint:      http://localhost:8000"
echo "📊 Grafana Dashboard: http://localhost:3000 (admin/admin123)"
echo "📈 Prometheus:        http://localhost:9090"
echo "🔧 Version:           $VERSION"
echo "📅 Deployed:          $(date)"
echo ""

# Show running services
info "Running services:"
docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" ps

# Show logs location
info "Logs are available at: $LOG_FILE"
info "Service logs: docker-compose -f $DOCKER_DIR/docker-compose.prod.yml logs -f"

success "🎉 Production deployment completed successfully!"

# Optional: Send deployment notification
if command -v curl &> /dev/null && [[ -n "${WEBHOOK_URL:-}" ]]; then
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"✅ AnalyticBot deployed successfully - Version: $VERSION\"}" \
        || warning "Failed to send deployment notification"
fi
