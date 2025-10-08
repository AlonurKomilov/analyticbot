#!/bin/bash
# AnalyticBot Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if docker-compose is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Determine docker compose command
get_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

# Show help
show_help() {
    echo "AnalyticBot Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [SERVICE]     Start all services or specific service"
    echo "  stop [SERVICE]      Stop all services or specific service"
    echo "  restart [SERVICE]   Restart all services or specific service"
    echo "  build [SERVICE]     Build all services or specific service"
    echo "  logs [SERVICE]      Show logs for all services or specific service"
    echo "  status              Show status of all services"
    echo "  dev                 Start in development mode"
    echo "  prod                Start in production mode"
    echo "  clean               Stop and remove all containers, networks, and volumes"
    echo "  health              Check health of all services"
    echo "  shell SERVICE       Open shell in specific service"
    echo ""
    echo "Available Services:"
    echo "  - db (PostgreSQL database)"
    echo "  - redis (Redis cache)"
    echo "  - api (FastAPI backend)"
    echo "  - bot (Telegram bot)"
    echo "  - frontend (React frontend)"
    echo "  - frontend-dev (Development frontend)"
    echo "  - worker (Celery worker)"
    echo "  - beat (Celery beat)"
    echo "  - mtproto (MTProto service)"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all production services"
    echo "  $0 start frontend           # Start only frontend service"
    echo "  $0 dev                      # Start in development mode"
    echo "  $0 logs api                 # Show API service logs"
    echo "  $0 shell frontend           # Open shell in frontend container"
}

# Main function
main() {
    check_docker
    COMPOSE_CMD=$(get_compose_cmd)

    case "${1:-help}" in
        "start")
            if [ -n "$2" ]; then
                print_info "Starting service: $2"
                $COMPOSE_CMD up -d "$2"
            else
                print_info "Starting all production services..."
                $COMPOSE_CMD up -d db redis api bot frontend
            fi
            print_success "Services started successfully"
            ;;

        "stop")
            if [ -n "$2" ]; then
                print_info "Stopping service: $2"
                $COMPOSE_CMD stop "$2"
            else
                print_info "Stopping all services..."
                $COMPOSE_CMD down
            fi
            print_success "Services stopped successfully"
            ;;

        "restart")
            if [ -n "$2" ]; then
                print_info "Restarting service: $2"
                $COMPOSE_CMD restart "$2"
            else
                print_info "Restarting all services..."
                $COMPOSE_CMD restart
            fi
            print_success "Services restarted successfully"
            ;;

        "build")
            if [ -n "$2" ]; then
                print_info "Building service: $2"
                $COMPOSE_CMD build "$2"
            else
                print_info "Building all services..."
                $COMPOSE_CMD build
            fi
            print_success "Build completed successfully"
            ;;

        "logs")
            if [ -n "$2" ]; then
                print_info "Showing logs for service: $2"
                $COMPOSE_CMD logs -f "$2"
            else
                print_info "Showing logs for all services..."
                $COMPOSE_CMD logs -f
            fi
            ;;

        "status")
            print_info "Service status:"
            $COMPOSE_CMD ps
            ;;

        "dev")
            print_info "Starting development environment..."
            $COMPOSE_CMD --profile dev up -d db redis api bot frontend-dev
            print_success "Development environment started"
            print_info "Frontend development server: http://localhost:5173"
            print_info "API server: http://localhost:8000"
            ;;

        "prod")
            print_info "Starting production environment..."
            $COMPOSE_CMD up -d db redis api bot frontend
            print_success "Production environment started"
            print_info "Frontend: http://localhost:3000"
            print_info "API: http://localhost:8000"
            ;;

        "full")
            print_info "Starting full environment (including workers)..."
            $COMPOSE_CMD --profile full up -d
            print_success "Full environment started"
            ;;

        "clean")
            print_warning "This will remove all containers, networks, and volumes!"
            read -p "Are you sure? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "Cleaning up Docker environment..."
                $COMPOSE_CMD down -v --remove-orphans
                docker system prune -f
                print_success "Cleanup completed"
            else
                print_info "Cleanup cancelled"
            fi
            ;;

        "health")
            print_info "Checking service health..."
            services=("db" "redis" "api" "frontend")
            for service in "${services[@]}"; do
                if $COMPOSE_CMD ps "$service" | grep -q "Up"; then
                    print_success "$service is running"
                else
                    print_error "$service is not running"
                fi
            done
            ;;

        "shell")
            if [ -n "$2" ]; then
                print_info "Opening shell in service: $2"
                $COMPOSE_CMD exec "$2" /bin/sh
            else
                print_error "Please specify a service name"
                echo "Example: $0 shell frontend"
            fi
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
}

# Run main function with all arguments
main "$@"
