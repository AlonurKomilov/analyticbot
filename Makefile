# Makefile for AnalyticBot

# Ensure .env file exists
ifeq (,$(wildcard ./.env))
    $(shell cp .env.example .env)
endif

.PHONY: help up down logs ps migrate lint typecheck test test-all export-reqs

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  up          - Start all services in detached mode"
	@echo "  down        - Stop and remove all services"
	@echo "  logs        - Follow logs for all services"
	@echo "  ps          - List running services"
	@echo "  migrate     - Run database migrations"
	@echo "  lint        - Run ruff linter"
	@echo "  typecheck   - Run mypy type checker"
	@echo "  test        - Run pytest"
	@echo "  export-reqs - Export Poetry deps to requirements.txt files"


up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

migrate:
	docker compose run --rm migrate

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest -q -m "not integration" --maxfail=1 --disable-warnings --cov=bot --cov-report=term-missing

test-all:
	pytest -q --maxfail=1 --disable-warnings --cov=bot --cov-report=term-missing

# Poetry dependency management
.PHONY: export-reqs
export-reqs:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements.prod.txt --without-hashes --only=main

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
