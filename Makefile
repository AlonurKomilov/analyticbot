.PHONY: help db-start db-stop db-restart start stop restart bot api logs status install init-db

# ============================================================================
# Analyticbot v2 — Development Commands
# ============================================================================

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Infrastructure (Docker) ────────────────────────────────────────────────

COMPOSE = docker-compose --env-file .env -f docker/docker-compose.yml

db-start: ## Start DB and Redis (Docker)
	$(COMPOSE) up -d
	@echo "✅ DB (port 10100) and Redis (port 10200) started"

db-stop: ## Stop DB and Redis
	$(COMPOSE) down
	@echo "✅ DB and Redis stopped"

db-restart: ## Restart DB and Redis
	$(COMPOSE) down
	$(COMPOSE) up -d
	@echo "✅ DB and Redis restarted"

db-logs: ## Show DB and Redis logs
	$(COMPOSE) logs -f

# ── Application ────────────────────────────────────────────────────────────

PID_DIR = .pids
BOT_PID = $(PID_DIR)/bot.pid
API_PID = $(PID_DIR)/api.pid

$(PID_DIR):
	@mkdir -p $(PID_DIR)

bot: $(PID_DIR) ## Start bot (foreground)
	python -m src.bot.main

api: $(PID_DIR) ## Start API (foreground)
	uvicorn src.api.main:app --host 0.0.0.0 --port $${API_PORT:-11400} --reload

start: $(PID_DIR) ## Start bot + API in background
	@echo "Starting bot..."
	@nohup python -m src.bot.main > logs/bot.log 2>&1 & echo $$! > $(BOT_PID)
	@echo "Starting API on port $${API_PORT:-11400}..."
	@nohup uvicorn src.api.main:app --host 0.0.0.0 --port $${API_PORT:-11400} > logs/api.log 2>&1 & echo $$! > $(API_PID)
	@echo "✅ Bot (PID $$(cat $(BOT_PID))) and API (PID $$(cat $(API_PID))) started"
	@echo "   Logs: logs/bot.log, logs/api.log"

stop: ## Stop bot + API
	@if [ -f $(BOT_PID) ]; then \
		kill $$(cat $(BOT_PID)) 2>/dev/null && echo "✅ Bot stopped" || echo "⚠️  Bot not running"; \
		rm -f $(BOT_PID); \
	else echo "⚠️  No bot PID file"; fi
	@if [ -f $(API_PID) ]; then \
		kill $$(cat $(API_PID)) 2>/dev/null && echo "✅ API stopped" || echo "⚠️  API not running"; \
		rm -f $(API_PID); \
	else echo "⚠️  No API PID file"; fi

restart: stop start ## Restart bot + API

status: ## Show status of all services
	@echo "=== Docker Services ==="
	@$(COMPOSE) ps 2>/dev/null || echo "Docker services not running"
	@echo ""
	@echo "=== Bot ==="
	@if [ -f $(BOT_PID) ] && kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then \
		echo "✅ Running (PID $$(cat $(BOT_PID)))"; \
	else echo "❌ Not running"; fi
	@echo ""
	@echo "=== API ==="
	@if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
		echo "✅ Running (PID $$(cat $(API_PID)))"; \
	else echo "❌ Not running"; fi

logs: ## Tail bot and API logs
	@tail -f logs/bot.log logs/api.log 2>/dev/null || echo "No log files yet. Run 'make start' first."

# ── Setup ──────────────────────────────────────────────────────────────────

install: ## Install dependencies
	pip install -e ".[dev]"

init-db: ## Create database tables
	python -c "import asyncio; from src.db.session import init_db; asyncio.run(init_db())"
	@echo "✅ Database tables created"

clean: ## Remove PID files, logs, and Python cache files
	rm -rf $(PID_DIR) logs/*.log
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Cleaned"
