# Makefile for AnalyticBot

# Ensure environment files exist - Two-File Clean Architecture
ifeq (,$(wildcard ./.env.development))
    $(shell echo "⚠️  Creating .env.development from template...")
    $(shell cp .env.development.example .env.development)
endif
ifeq (,$(wildcard ./.env.production))
    $(shell echo "⚠️  Creating .env.production from template...")
    $(shell cp .env.production.example .env.production)
endif

# Include development commands
include Makefile.dev

.PHONY: help up down logs ps migrate lint typecheck test test-all export-reqs

help:
	@echo "🚀 AnalyticBot - Hybrid Development Environment"
	@echo "=============================================="
	@echo ""
	@echo "🔥 DEVELOPMENT (Fast, venv-based):"
	@echo "  dev-start   - Start development servers (ports 8001, 5174)"
	@echo "  dev-stop    - Stop development services"
	@echo "  dev-status  - Check development status"
	@echo "  dev-logs    - Show development logs"
	@echo "  dev-test    - Run tests in venv"
	@echo "  dev-install - Install dependencies"
	@echo ""
	@echo "🐳 PRODUCTION (Docker-based):"
	@echo "  up          - Start Docker services (ports 8000, 3000)"
	@echo "  down        - Stop and remove Docker services"
	@echo "  logs        - Follow Docker logs"
	@echo "  ps          - List running Docker services"
	@echo "  migrate     - Run database migrations"
	@echo ""
	@echo "🔄 SYNC & DEPLOY:"
	@echo "  sync        - Sync dev changes to Docker"
	@echo "  lint        - Run code linting"
	@echo "  typecheck   - Run type checking"
	@echo ""
	@echo "💡 Workflow: dev-start → code → test → sync → deploy"

# Production Docker commands
up:
	@echo "🐳 Starting Docker services..."
	docker-compose -f docker/docker-compose.yml up -d
	@echo "✅ Services available at:"
	@echo "   • API: http://localhost:10300"
	@echo "   • Frontend: http://localhost:10400"

down:
	@echo "🛑 Stopping Docker services..."
	docker-compose -f docker/docker-compose.yml down

logs:
	@echo "📋 Following Docker logs..."
	docker-compose -f docker/docker-compose.yml logs -f

ps:
	@echo "📊 Docker services status:"
	docker-compose -f docker/docker-compose.yml ps

migrate:
	@echo "🔄 Running database migrations..."
	docker-compose -f docker/docker-compose.yml run --rm migrate

# Sync development changes to Docker
sync:
	@echo "🔄 Syncing development changes to Docker..."
	./scripts/sync-to-docker.sh

# Code quality
lint:
	@echo "🔍 Running linter..."
	ruff check .

typecheck:
	@echo "🏷️ Running type checker..."
	mypy .

# Testing
test:
	@echo "🧪 Running unit tests..."
	pytest -q -m "not integration" --maxfail=1 --disable-warnings --cov=bot --cov-report=term-missing

test-all:
	@echo "🧪 Running all tests..."
	pytest -q --maxfail=1 --disable-warnings --cov=bot --cov-report=term-missing

# Dependency management
.PHONY: export-reqs
export-reqs:
	@echo "📦 Exporting requirements..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements.prod.txt --without-hashes --only=main
	@echo "✅ Requirements exported to requirements.txt and requirements.prod.txt"

# Additional Docker development commands
.PHONY: build shell clean-docker dev-setup backup restore

build:
	docker-compose -f docker/docker-compose.yml build --no-cache

shell:
	docker-compose -f docker/docker-compose.yml exec api bash

clean-docker:
	docker-compose -f docker/docker-compose.yml down -v --remove-orphans
	docker system prune -f
	@echo "✅ Docker environment cleaned"

dev-setup:
	@echo "🚀 Setting up development environment..."
	@echo "📁 Environment files are managed automatically (see Makefile setup at top)"
	docker-compose -f docker/docker-compose.yml up --build -d
	@echo "✅ Development environment ready!"
	@echo "📊 Services running:"
	@echo "   • API: http://localhost:10300"
	@echo "   • Frontend: http://localhost:10400"
	@echo "   • Docs: http://localhost:10300/docs"
	docker-compose -f docker/docker-compose.yml logs -f api

backup:
	@mkdir -p backups
	@echo "📦 Creating database backup..."
	docker-compose -f docker/docker-compose.yml exec db pg_dump -U analytic analytic_bot > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up to backups/"

restore:
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make restore BACKUP_FILE=backups/backup_file.sql"; exit 1; fi
	@echo "📦 Restoring from $(BACKUP_FILE)..."
	docker-compose -f docker/docker-compose.yml exec -T db psql -U analytic analytic_bot < $(BACKUP_FILE)
	@echo "✅ Database restored from $(BACKUP_FILE)"

# Enhanced Docker operations
.PHONY: rebuild restart status

rebuild:
	docker-compose -f docker/docker-compose.yml down
	docker-compose -f docker/docker-compose.yml build --no-cache
	docker-compose -f docker/docker-compose.yml up -d
	@echo "✅ Services rebuilt and restarted"

restart:
	docker-compose -f docker/docker-compose.yml restart
	@echo "✅ All services restarted"

status:
	@echo "📊 Docker Services Status:"
	@docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "💾 Resource Usage:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Production deployment commands
.PHONY: prod-up prod-down prod-logs prod-status

prod-up:
	@echo "🚀 Starting production environment..."
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d
	@echo "✅ Production environment started!"
	@echo "📊 Production services:"
	@echo "   • API: http://localhost:10300"
	@echo "   • Frontend: http://localhost:10400"
	@echo "   • No external database ports (secure)"

prod-down:
	@echo "🛑 Stopping production environment..."
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml down
	@echo "✅ Production environment stopped"

prod-logs:
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs -f

prod-status:
	@echo "📊 Production Services Status:"
	@docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "💾 Production Resource Usage:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
