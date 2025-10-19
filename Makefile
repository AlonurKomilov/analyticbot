# Makefile for AnalyticBot

# Ensure environment files exist - Two-File Clean Architecture
ifeq (,$(wildcard ./.env.development))
	$(shell echo "Creating .env.development from template...")
	$(shell cp .env.development.example .env.development)
endif
ifeq (,$(wildcard ./.env.production))
	$(shell echo "Creating .env.production from template...")
	$(shell cp .env.production.example .env.production)
endif

# Include development commands
include Makefile.dev

.PHONY: help up down logs ps migrate lint lint-imports typecheck test test-all export-reqs

help:
	@echo "🚀 AnalyticBot - Hybrid Development Environment"
	@echo "=============================================="
	@echo ""
	@echo "🔥 DEVELOPMENT (Fast, venv-based):"
	@echo "  dev-start   - Start development servers + CloudFlare Tunnel"
	@echo "  dev-stop    - Stop development services"
	@echo "  dev-tunnel  - Start CloudFlare Tunnel for public access"
	@echo "  dev-status  - Check development status"
	@echo "  dev-logs    - Show development logs"
	@echo "  dev-test    - Run tests in venv"
	@echo "  dev-install - Install dependencies"
	@echo ""
	@echo "🐳 PRODUCTION (Docker-based):"
	@echo "  up          - Start Docker services (ports 10300, 10400)"
	@echo "  down        - Stop and remove Docker services"
	@echo "  prod-up     - Start production with security hardening"
	@echo "  prod-proxy  - Start production with reverse proxy & SSL"
	@echo "  logs        - Follow Docker logs"
	@echo "  ps          - List running Docker services"
	@echo ""
	@echo "🔒 SSL & SECURITY:"
	@echo "  ssl-dev     - Setup development SSL certificate"
	@echo "  ssl-prod    - Setup production SSL (DOMAIN=domain.com)"
	@echo "  proxy-logs  - Show reverse proxy logs"
	@echo "  proxy-status- Check SSL certificate status"
	@echo ""
	@echo "� BUILD & OPTIMIZATION:"
	@echo "  build       - Build all services (optimized caching)"
	@echo "  build-nocache - Build all services (no cache)"
	@echo "  build-api   - Build API service only"
	@echo "  build-bot   - Build Bot service only"
	@echo "  build-worker - Build Worker service only"
	@echo "  build-frontend - Build Frontend service only"
	@echo "  build-analysis - Analyze build cache and images"
	@echo ""
	@echo "�🗄️  DATABASE:"
	@echo "  migrate     - Run database migrations"
	@echo "  backup      - Create database backup"
	@echo "  prod-db-shell - Secure production DB access"
	@echo ""
	@echo "🔄 SYNC & DEPLOY:"
	@echo "  sync        - Sync dev changes to Docker"
		@echo "🔬 CODE QUALITY:"
	@echo "  lint        - Run code linting"
	@echo "  lint-imports - Validate Clean Architecture (Phase 6)"
	@echo "  typecheck   - Run type checking"
	@echo ""
	@echo "💡 Workflow: dev-start → code → test → ssl-dev → prod-proxy"

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

lint-imports:
	@echo "🔒 Validating Clean Architecture boundaries (Phase 6)..."
	lint-imports

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
	@echo "🔨 Building all services with optimized caching..."
	DOCKER_BUILDKIT=1 docker-compose -f docker/docker-compose.yml build

build-nocache:
	@echo "🔨 Building all services without cache..."
	DOCKER_BUILDKIT=1 docker-compose -f docker/docker-compose.yml build --no-cache

# Optimized individual service builds
.PHONY: build-api build-bot build-worker build-frontend build-analysis

build-api:
	@echo "🚀 Building API service with optimized caching..."
	./scripts/build-optimized.sh --target api

build-bot:
	@echo "🤖 Building Bot service with optimized caching..."
	./scripts/build-optimized.sh --target bot

build-worker:
	@echo "⚙️ Building Worker service with optimized caching..."
	./scripts/build-optimized.sh --target worker

build-frontend:
	@echo "🌐 Building Frontend service with optimized caching..."
	./scripts/build-optimized.sh --target frontend

build-analysis:
	@echo "📊 Analyzing Docker build layers and cache efficiency..."
	@echo "Docker BuildKit cache usage:"
	@docker system df --format "table {{.Type}}\t{{.Total}}\t{{.Active}}\t{{.Size}}\t{{.Reclaimable}}"
	@echo ""
	@echo "Recent images:"
	@docker images analyticbot* --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

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

# Production database management (secure access)
.PHONY: prod-db-shell prod-db-backup prod-db-restore

prod-db-shell:
	@echo "🔧 Opening secure database shell..."
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml --profile admin up -d db-admin
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml exec db-admin psql -U ${POSTGRES_USER:-analytic} -d ${POSTGRES_DB:-analytic_bot}

prod-db-backup:
	@mkdir -p backups/production
	@echo "📦 Creating production database backup..."
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml --profile admin up -d db-admin
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml exec db-admin pg_dump -U ${POSTGRES_USER:-analytic} -d ${POSTGRES_DB:-analytic_bot} > backups/production/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Production database backed up to backups/production/"

prod-db-restore:
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make prod-db-restore BACKUP_FILE=backups/production/backup_file.sql"; exit 1; fi
	@echo "📦 Restoring production database from $(BACKUP_FILE)..."
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml --profile admin up -d db-admin
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml exec -T db-admin psql -U ${POSTGRES_USER:-analytic} -d ${POSTGRES_DB:-analytic_bot} < $(BACKUP_FILE)
	@echo "✅ Production database restored from $(BACKUP_FILE)"

# Production deployment with reverse proxy and SSL
.PHONY: prod-proxy ssl-setup ssl-dev ssl-prod proxy-logs proxy-status

prod-proxy:
	@echo "🚀 Starting production environment with reverse proxy..."
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml -f docker/docker-compose.proxy.yml up -d
	@echo "✅ Production environment with proxy started!"
	@echo "📊 Services:"
	@echo "   • HTTPS: https://localhost"
	@echo "   • HTTP:  http://localhost (redirects to HTTPS)"
	@echo "   • API:   https://localhost/api/"
	@echo "   • Health: https://localhost/health"

ssl-setup:
	@echo "🔒 SSL Certificate Setup"
	@echo "Usage: make ssl-dev OR make ssl-prod DOMAIN=your-domain.com"

ssl-dev:
	@echo "🔧 Setting up development SSL certificate..."
	./scripts/setup-ssl.sh self-signed localhost
	@echo "✅ Development SSL ready! Use: make prod-proxy"

ssl-prod:
	@if [ -z "$(DOMAIN)" ]; then echo "❌ Usage: make ssl-prod DOMAIN=your-domain.com"; exit 1; fi
	@echo "🔐 Setting up production SSL certificate for $(DOMAIN)..."
	./scripts/setup-ssl.sh letsencrypt $(DOMAIN)
	@echo "✅ Production SSL ready!"

proxy-logs:
	docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml -f docker/docker-compose.proxy.yml logs -f nginx-proxy

proxy-status:
	@echo "📊 Proxy Status:"
	@docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml -f docker/docker-compose.proxy.yml ps nginx-proxy
	@echo ""
	@echo "🔒 SSL Certificate Info:"
	@if [ -f "docker/nginx/ssl/cert.pem" ]; then \
		openssl x509 -in docker/nginx/ssl/cert.pem -noout -subject -dates; \
	else \
		echo "No SSL certificate found. Run 'make ssl-dev' or 'make ssl-prod'"; \
	fi
