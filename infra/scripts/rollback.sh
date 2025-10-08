#!/bin/bash

# 🔄 PHASE 5.0: Production Rollback Script
# Safe rollback mechanism for production deployments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/infrastructure/docker"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="/var/log/analyticbot-rollback.log"

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

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -v, --version VERSION    Rollback to specific version"
    echo "  -l, --list              List available versions"
    echo "  -b, --backup            Create backup before rollback"
    echo "  -f, --force             Force rollback without confirmation"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --list                    # List available versions"
    echo "  $0 --version abc123          # Rollback to specific version"
    echo "  $0 --version latest --backup # Rollback with backup"
    exit 1
}

# Parse command line arguments
ROLLBACK_VERSION=""
LIST_VERSIONS=false
CREATE_BACKUP=false
FORCE_ROLLBACK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            ROLLBACK_VERSION="$2"
            shift 2
            ;;
        -l|--list)
            LIST_VERSIONS=true
            shift
            ;;
        -b|--backup)
            CREATE_BACKUP=true
            shift
            ;;
        -f|--force)
            FORCE_ROLLBACK=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Header
echo -e "${PURPLE}"
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                      🔄 ANALYTICBOT PRODUCTION ROLLBACK                        ║"
echo "║                              Phase 5.0 Enterprise                             ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# List available versions
if [[ "$LIST_VERSIONS" == true ]]; then
    log "📋 Available versions:"

    # List Docker images
    echo -e "${BLUE}Docker Images:${NC}"
    docker images analyticbot --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"

    # List deployment records
    echo -e "${BLUE}Deployment Records:${NC}"
    if [[ -d "$PROJECT_ROOT" ]]; then
        find "$PROJECT_ROOT" -name "deployment_*.json" -exec basename {} \; 2>/dev/null | sort -r | head -10
    fi

    exit 0
fi

# Validate rollback version
if [[ -z "$ROLLBACK_VERSION" ]]; then
    error "Rollback version not specified. Use --version or --list to see available versions."
fi

# Check if version exists
if ! docker images -q "analyticbot:$ROLLBACK_VERSION" | grep -q .; then
    error "Version $ROLLBACK_VERSION not found in local Docker images"
fi

# Confirmation
if [[ "$FORCE_ROLLBACK" != true ]]; then
    echo -e "${YELLOW}"
    echo "⚠️  WARNING: You are about to rollback to version: $ROLLBACK_VERSION"
    echo "This will:"
    echo "  - Stop current services"
    echo "  - Rollback to previous version"
    echo "  - Restart services"
    echo -e "${NC}"

    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        info "Rollback cancelled by user"
        exit 0
    fi
fi

# Pre-rollback checks
log "🔍 Performing pre-rollback checks..."

# Check Docker availability
if ! docker info > /dev/null 2>&1; then
    error "Docker daemon is not running"
fi

# Check current deployment status
CURRENT_SERVICES=$(docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" ps -q)
if [[ -z "$CURRENT_SERVICES" ]]; then
    warning "No services are currently running"
fi

success "✅ Pre-rollback checks passed"

# Create backup if requested
if [[ "$CREATE_BACKUP" == true ]]; then
    log "💾 Creating backup..."

    mkdir -p "$BACKUP_DIR"
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

    # Database backup
    info "Creating database backup..."
    docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" exec -T postgres pg_dump \
        -U "${POSTGRES_USER:-analyticuser}" \
        -d "${POSTGRES_DB:-analyticbot}" \
        > "$BACKUP_PATH.sql" || warning "Database backup failed"

    # Configuration backup
    info "Creating configuration backup..."
    tar -czf "$BACKUP_PATH.tar.gz" \
        "$PROJECT_ROOT/.env" \
        "$PROJECT_ROOT/infrastructure" \
        2>/dev/null || warning "Configuration backup failed"

    success "✅ Backup created: $BACKUP_NAME"
fi

# Rollback process
log "🔄 Starting rollback process..."

# Stop current services
info "Stopping current services..."
docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" down --timeout 30

# Update image tags for rollback
info "Preparing rollback to version: $ROLLBACK_VERSION"

# Create temporary compose file with rollback version
TEMP_COMPOSE="$DOCKER_DIR/docker-compose.rollback.yml"
sed "s|analyticbot:latest|analyticbot:$ROLLBACK_VERSION|g" \
    "$DOCKER_DIR/docker-compose.prod.yml" > "$TEMP_COMPOSE"

# Start services with rollback version
info "Starting services with version: $ROLLBACK_VERSION"
docker-compose -f "$TEMP_COMPOSE" up -d

# Wait for services to start
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
        error "API service failed health check after rollback"
    fi
    info "Waiting for API service... (attempt $i/10)"
    sleep 10
done

# Database health check
if docker-compose -f "$TEMP_COMPOSE" exec -T postgres pg_isready -U "${POSTGRES_USER:-analyticuser}" > /dev/null; then
    success "✅ Database is healthy"
else
    error "Database health check failed after rollback"
fi

# Redis health check
if docker-compose -f "$TEMP_COMPOSE" exec -T redis redis-cli ping | grep -q "PONG"; then
    success "✅ Redis is healthy"
else
    error "Redis health check failed after rollback"
fi

# Update permanent compose file
mv "$TEMP_COMPOSE" "$DOCKER_DIR/docker-compose.prod.yml"

# Create rollback record
ROLLBACK_INFO="rollback_$(date +%Y%m%d_%H%M%S).json"
cat > "$ROLLBACK_INFO" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "rollback_to_version": "$ROLLBACK_VERSION",
  "rollback_reason": "Manual rollback",
  "backup_created": $CREATE_BACKUP,
  "health_status": "healthy"
}
EOF

success "✅ Rollback record created: $ROLLBACK_INFO"

# Cleanup
rm -f "$TEMP_COMPOSE" 2>/dev/null || true

# Success message
log "📊 Rollback Summary"
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                            ROLLBACK COMPLETED                                 ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "🔄 Rolled back to:    $ROLLBACK_VERSION"
echo "🌐 API Endpoint:      http://localhost:8000"
echo "📊 Grafana Dashboard: http://localhost:3000"
echo "📅 Completed:         $(date)"
echo ""

# Show running services
info "Running services:"
docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" ps

success "🎉 Rollback completed successfully!"

# Cleanup old images (optional)
read -p "Remove old unused Docker images? (yes/no): " -r
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    docker image prune -f
    success "✅ Old images cleaned up"
fi
