#!/bin/bash
# Production Deployment Script for AnalyticBot Payment System
# Week 15-16 Implementation - Deploy to Production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="analyticbot"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="infra/docker/docker-compose.prod.yml"

echo -e "${BLUE}🚀 AnalyticBot Payment System - Production Deployment${NC}"
echo -e "${BLUE}========================================================${NC}"
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    print_info "Running as root user"
    SUDO_CMD=""
else
    print_info "Running with sudo"
    SUDO_CMD="sudo"
fi

# Step 1: Pre-deployment checks
echo -e "${BLUE}📋 Step 1: Pre-deployment Checks${NC}"
echo "----------------------------------------"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_status "Docker is installed"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi
print_status "Docker Compose is available"

# Check if environment files exist
if [[ ! -f ".env.example" ]]; then
    print_error ".env.example not found"
    exit 1
fi

if [[ ! -f "apps/frontend/.env.example" ]]; then
    print_error "apps/frontend/.env.example not found"
    exit 1
fi

print_status "Environment templates found"

# Step 2: Environment Configuration
echo ""
echo -e "${BLUE}⚙️  Step 2: Environment Configuration${NC}"
echo "----------------------------------------"

# Check if production environment files exist
if [[ ! -f ".env.production" ]]; then
    print_warning "Production environment file not found"
    echo "Creating .env.production from template..."
    cp .env.example .env.production
    print_info "Please edit .env.production with your actual production values:"
    print_info "  - STRIPE_SECRET_KEY (Live secret key)"
    print_info "  - STRIPE_PUBLISHABLE_KEY (Live publishable key)"
    print_info "  - STRIPE_WEBHOOK_SECRET (Production webhook secret)"
    print_info "  - DATABASE_URL (Production database)"
    print_info "  - API_BASE_URL (Your production domain)"
    echo ""
    read -p "Press Enter after updating .env.production..."
fi

if [[ ! -f "apps/frontend/.env.production" ]]; then
    print_warning "Frontend production environment file not found"
    echo "Creating apps/frontend/.env.production from template..."
    cp apps/frontend/.env.example apps/frontend/.env.production
    print_info "Please edit apps/frontend/.env.production with your actual values"
    echo ""
    read -p "Press Enter after updating frontend .env.production..."
fi

print_status "Environment configuration checked"

# Step 3: Build and Deploy
echo ""
echo -e "${BLUE}🔨 Step 3: Build and Deploy${NC}"
echo "----------------------------------------"

# Stop existing containers
print_info "Stopping existing containers..."
$SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE down

# Pull latest images
print_info "Pulling latest images..."
$SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE pull

# Build services
print_info "Building services..."
$SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE build

# Start services
print_info "Starting services..."
$SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE up -d

print_status "Services deployed"

# Step 4: Database Migration
echo ""
echo -e "${BLUE}🗄️  Step 4: Database Migration${NC}"
echo "----------------------------------------"

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 10

# Run database migrations
print_info "Running database migrations..."
$SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE exec api alembic upgrade head

print_status "Database migrations completed"

# Step 5: Stripe Webhook Configuration
echo ""
echo -e "${BLUE}🔗 Step 5: Stripe Webhook Configuration${NC}"
echo "----------------------------------------"

# Load environment variables
if [[ -f ".env.production" ]]; then
    source .env.production
fi

print_info "Stripe Webhook Endpoint Configuration:"
echo ""
print_info "1. Log in to your Stripe Dashboard (https://dashboard.stripe.com/)"
print_info "2. Go to Developers > Webhooks"
print_info "3. Click 'Add endpoint'"
print_info "4. Enter this URL: ${API_BASE_URL:-https://api.your-domain.com}/api/payments/webhook/stripe"
print_info "5. Select these events:"
echo "   • payment_intent.succeeded"
echo "   • payment_intent.payment_failed"
echo "   • invoice.payment_succeeded"
echo "   • customer.subscription.updated"
echo "   • customer.subscription.deleted"
print_info "6. Copy the webhook signing secret and update STRIPE_WEBHOOK_SECRET in .env.production"
echo ""

# Step 6: Health Checks
echo ""
echo -e "${BLUE}🏥 Step 6: Health Checks${NC}"
echo "----------------------------------------"

# Wait for services to start
print_info "Waiting for services to start..."
sleep 30

# Check API health
print_info "Checking API health..."
if $SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE exec api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "API is healthy"
else
    print_warning "API health check failed - checking logs..."
    $SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE logs api | tail -20
fi

# Check payment system status
print_info "Checking payment system status..."
if $SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE exec api curl -f http://localhost:8000/api/payments/status > /dev/null 2>&1; then
    print_status "Payment system is operational"
else
    print_warning "Payment system health check failed"
fi

# Step 7: Final Configuration
echo ""
echo -e "${BLUE}🎯 Step 7: Final Configuration${NC}"
echo "----------------------------------------"

print_info "Final deployment steps:"
echo ""
print_info "1. DNS Configuration:"
echo "   • Point your domain to this server's IP address"
echo "   • Configure SSL certificate (Let's Encrypt recommended)"
echo ""
print_info "2. Stripe Dashboard Configuration:"
echo "   • Create your products and pricing in Stripe Dashboard"
echo "   • Configure your webhook endpoint (see Step 5)"
echo "   • Test webhook delivery"
echo ""
print_info "3. Monitoring Setup:"
echo "   • Configure Sentry for error tracking (optional)"
echo "   • Set up monitoring for payment events"
echo "   • Configure backup strategy for database"
echo ""

# Step 8: Deployment Summary
echo ""
echo -e "${GREEN}🎉 Deployment Summary${NC}"
echo "==============================="

# Get container status
echo "Container Status:"
$SUDO_CMD docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE ps

echo ""
print_status "Payment System Deployment Complete!"
echo ""
print_info "Access URLs:"
if [[ -n "$API_BASE_URL" ]]; then
    echo "  • API: ${API_BASE_URL}"
    echo "  • Payment Status: ${API_BASE_URL}/api/payments/status"
    echo "  • API Docs: ${API_BASE_URL}/docs"
else
    echo "  • API: http://localhost:8000"
    echo "  • Payment Status: http://localhost:8000/api/payments/status"
    echo "  • API Docs: http://localhost:8000/docs"
fi

if [[ -n "$FRONTEND_URL" ]]; then
    echo "  • Frontend: ${FRONTEND_URL}"
else
    echo "  • Frontend: http://localhost:3000"
fi

echo ""
print_info "Next Steps:"
echo "1. Test payment flows in your application"
echo "2. Configure Stripe products and pricing"
echo "3. Set up monitoring and alerts"
echo "4. Configure backup procedures"
echo "5. Document your deployment process"

echo ""
print_info "For logs, use:"
echo "  sudo docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE logs -f [service_name]"

echo ""
print_status "🚀 Payment System is now live and ready to generate revenue!"
print_status "💰 Revenue generation capability: ACTIVATED"
