#!/bin/bash
# Frontend Development Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    echo "Frontend Development Helper Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup               Install dependencies and setup frontend"
    echo "  dev                 Start development server"
    echo "  build               Build for production"
    echo "  preview             Preview production build"
    echo "  test                Run tests"
    echo "  test-watch          Run tests in watch mode"
    echo "  test-a11y           Run accessibility tests"
    echo "  lint                Run ESLint"
    echo "  lint-fix            Run ESLint with auto-fix"
    echo "  typecheck           Run TypeScript type checking"
    echo "  analyze             Analyze bundle size"
    echo "  clean               Clean build artifacts"
    echo ""
    echo "Docker Commands:"
    echo "  docker-dev          Start frontend in Docker development mode (hot reload)"
    echo "  docker-prod         Start frontend in Docker production mode"
    echo "  docker-build        Build Docker images (dev + prod)"
    echo "  docker-stop         Stop Docker containers"
    echo "  docker-logs         Show Docker container logs"
    echo "  docker-status       Show Docker container status"
    echo "  test                Run comprehensive frontend tests"
    echo ""
}

# Navigate to frontend directory
cd "$(dirname "$0")/../apps/frontend"

case "${1:-help}" in
    "setup")
        print_info "Installing frontend dependencies..."
        npm install
        print_success "Dependencies installed successfully"
        ;;
        
    "dev")
        print_info "Starting development server..."
        print_info "Available at: http://localhost:5173"
        npm run dev
        ;;
        
    "build")
        print_info "Building for production..."
        npm run build
        print_success "Build completed successfully"
        print_info "Files are in dist/ directory"
        ;;
        
    "preview")
        print_info "Starting preview server..."
        print_info "Available at: http://localhost:4173"
        npm run preview
        ;;
        
    "test")
        print_info "Running tests..."
        npm run test
        ;;
        
    "test-watch")
        print_info "Running tests in watch mode..."
        npm run test:watch
        ;;
        
    "test-a11y")
        print_info "Running accessibility tests..."
        npm run test:a11y
        ;;
        
    "lint")
        print_info "Running ESLint..."
        npm run lint
        ;;
        
    "lint-fix")
        print_info "Running ESLint with auto-fix..."
        npm run lint:fix
        ;;
        
    "typecheck")
        print_info "Running TypeScript type checking..."
        npm run typecheck
        ;;
        
    "analyze")
        print_info "Analyzing bundle size..."
        npm run analyze
        ;;
        
    "clean")
        print_info "Cleaning build artifacts..."
        rm -rf dist node_modules/.vite
        print_success "Cleanup completed"
        ;;
        
    "docker-dev")
        print_info "Starting frontend in Docker development mode..."
        cd ../..
        sudo docker-compose --profile dev up -d frontend-dev
        print_success "Frontend development container started"
        print_info "Available at: http://localhost:5173 (Hot reload enabled)"
        print_info "Container logs: sudo docker logs -f analyticbot-frontend-dev"
        ;;
        
    "docker-prod")
        print_info "Starting frontend in Docker production mode..."
        cd ../..
        sudo docker-compose up -d frontend
        print_success "Frontend production container started"
        print_info "Available at: http://localhost:3000"
        print_info "Container logs: sudo docker logs -f analyticbot-frontend"
        ;;
        
    "docker-build")
        print_info "Building Docker images..."
        cd ../..
        sudo docker-compose build frontend frontend-dev
        print_success "Docker images built successfully"
        ;;
        
    "docker-stop")
        print_info "Stopping Docker containers..."
        cd ../..
        sudo docker-compose down frontend frontend-dev
        print_success "Docker containers stopped"
        ;;
        
    "docker-logs")
        print_info "Showing frontend Docker logs..."
        cd ../..
        echo "=== Development Logs ==="
        sudo docker logs analyticbot-frontend-dev --tail 20 2>/dev/null || echo "Development container not running"
        echo ""
        echo "=== Production Logs ==="
        sudo docker logs analyticbot-frontend --tail 20 2>/dev/null || echo "Production container not running"
        ;;
        
    "docker-status")
        print_info "Docker frontend status..."
        cd ../..
        sudo docker ps | grep frontend || echo "No frontend containers running"
        ;;
        
    "test")
        print_info "Running comprehensive frontend tests..."
        cd ../..
        ./scripts/test-frontend.sh
        ;;
        
    "help"|"--help"|"-h")
        show_help
        ;;
        
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
