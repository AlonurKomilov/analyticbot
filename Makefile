# Makefile for AnalyticBot

# Ensure .env file exists
ifeq (,$(wildcard ./.env))
    $(shell cp .env.example .env)
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
	docker compose up -d
	@echo "✅ Services available at:"
	@echo "   • API: http://localhost:8000"
	@echo "   • Frontend: http://localhost:3000"

down:
	@echo "🛑 Stopping Docker services..."
	docker compose down

logs:
	@echo "📋 Following Docker logs..."
	docker compose logs -f

ps:
	@echo "📊 Docker services status:"
	docker compose ps

migrate:
	@echo "🔄 Running database migrations..."
	docker compose run --rm migrate

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
	docker compose build --no-cache

shell:
	docker compose exec api bash

clean-docker:
	docker compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Docker environment cleaned"

dev-setup:
	@echo "🚀 Setting up development environment..."
	cp .env.example .env 2>/dev/null || echo "⚠️ .env.example not found, please create .env manually"
	docker compose up --build -d
	@echo "✅ Development environment ready!"
	@echo "📊 Services running:"
	@echo "   • API: http://localhost:8000"
	@echo "   • Frontend: http://localhost:3000"
	@echo "   • Docs: http://localhost:8000/docs"
	docker compose logs -f api

backup:
	@mkdir -p backups
	@echo "📦 Creating database backup..."
	docker compose exec db pg_dump -U analytic analytic_bot > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up to backups/"

restore:
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make restore BACKUP_FILE=backups/backup_file.sql"; exit 1; fi
	@echo "📦 Restoring from $(BACKUP_FILE)..."
	docker compose exec -T db psql -U analytic analytic_bot < $(BACKUP_FILE)
	@echo "✅ Database restored from $(BACKUP_FILE)"

# Enhanced Docker operations
.PHONY: rebuild restart status

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ Services rebuilt and restarted"

restart:
	docker compose restart
	@echo "✅ All services restarted"

status:
	@echo "📊 Docker Services Status:"
	@docker compose ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "💾 Resource Usage:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Production deployment commands
.PHONY: prod-up prod-down prod-logs prod-status

prod-up:
	@echo "🚀 Starting production environment..."
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started!"
	@echo "📊 Production services:"
	@echo "   • API: http://localhost:8000"
	@echo "   • Frontend: http://localhost:3000"
	@echo "   • No external database ports (secure)"

prod-down:
	@echo "🛑 Stopping production environment..."
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down
	@echo "✅ Production environment stopped"

prod-logs:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-status:
	@echo "📊 Production Services Status:"
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "💾 Production Resource Usage:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
