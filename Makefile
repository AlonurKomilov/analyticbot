.PHONY: help db-start db-stop db-restart start stop restart bot api logs status install init-db clean health _ensure_log_dir

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

PYTHON = .venv/bin/python
UVICORN = .venv/bin/uvicorn
PID_DIR = .pids
LOG_DIR = logs
BOT_PID = $(PID_DIR)/bot.pid
API_PID = $(PID_DIR)/api.pid

$(PID_DIR):
	@mkdir -p $(PID_DIR)

_ensure_log_dir:
	@mkdir -p $(LOG_DIR)

bot: $(PID_DIR) _ensure_log_dir ## Start bot (foreground)
	$(PYTHON) -m src.bot.main

api: $(PID_DIR) _ensure_log_dir ## Start API (foreground)
	$(UVICORN) src.api.main:app --host 0.0.0.0 --port $${API_PORT:-11400} --reload

start: $(PID_DIR) _ensure_log_dir ## Start bot + API in background
	@# ── Stop stale processes first ──
	@if [ -f $(BOT_PID) ]; then \
		if kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then \
			echo "⚠️  Bot already running (PID $$(cat $(BOT_PID))), stopping first..."; \
			kill $$(cat $(BOT_PID)) 2>/dev/null; sleep 1; \
		fi; \
		rm -f $(BOT_PID); \
	fi
	@if [ -f $(API_PID) ]; then \
		if kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
			echo "⚠️  API already running (PID $$(cat $(API_PID))), stopping first..."; \
			kill $$(cat $(API_PID)) 2>/dev/null; sleep 1; \
		fi; \
		rm -f $(API_PID); \
	fi
	@# ── Start services ──
	@echo "Starting bot..."
	@nohup $(PYTHON) -m src.bot.main > $(LOG_DIR)/bot.log 2>&1 & echo $$! > $(BOT_PID)
	@echo "Starting API on port $${API_PORT:-11400}..."
	@nohup $(UVICORN) src.api.main:app --host 0.0.0.0 --port $${API_PORT:-11400} > $(LOG_DIR)/api.log 2>&1 & echo $$! > $(API_PID)
	@sleep 2
	@# ── Verify they actually started ──
	@BOT_OK=0; API_OK=0; \
	if [ -f $(BOT_PID) ] && kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then BOT_OK=1; fi; \
	if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then API_OK=1; fi; \
	if [ $$BOT_OK -eq 1 ] && [ $$API_OK -eq 1 ]; then \
		echo "✅ Bot (PID $$(cat $(BOT_PID))) and API (PID $$(cat $(API_PID))) started"; \
		echo "   Logs: $(LOG_DIR)/bot.log, $(LOG_DIR)/api.log"; \
	else \
		if [ $$BOT_OK -eq 0 ]; then \
			echo "❌ Bot failed to start! Check $(LOG_DIR)/bot.log:"; \
			tail -5 $(LOG_DIR)/bot.log 2>/dev/null || echo "   (no log output)"; \
			rm -f $(BOT_PID); \
		fi; \
		if [ $$API_OK -eq 0 ]; then \
			echo "❌ API failed to start! Check $(LOG_DIR)/api.log:"; \
			tail -5 $(LOG_DIR)/api.log 2>/dev/null || echo "   (no log output)"; \
			rm -f $(API_PID); \
		fi; \
		exit 1; \
	fi

stop: ## Stop bot + API
	@if [ -f $(BOT_PID) ]; then \
		if kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then \
			kill $$(cat $(BOT_PID)) && echo "✅ Bot stopped (PID $$(cat $(BOT_PID)))"; \
		else \
			echo "⚠️  Bot was not running (stale PID file removed)"; \
		fi; \
		rm -f $(BOT_PID); \
	else echo "⚠️  No bot PID file — bot not managed by make"; fi
	@if [ -f $(API_PID) ]; then \
		if kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
			kill $$(cat $(API_PID)) && echo "✅ API stopped (PID $$(cat $(API_PID)))"; \
		else \
			echo "⚠️  API was not running (stale PID file removed)"; \
		fi; \
		rm -f $(API_PID); \
	else echo "⚠️  No API PID file — API not managed by make"; fi

restart: stop start ## Restart bot + API

status: ## Show status of all services
	@echo "=== Docker Services ==="
	@$(COMPOSE) ps 2>/dev/null || echo "Docker services not running"
	@echo ""
	@echo "=== Bot ==="
	@if [ -f $(BOT_PID) ] && kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then \
		UPTIME=$$(ps -o etime= -p $$(cat $(BOT_PID)) 2>/dev/null | xargs); \
		echo "✅ Running (PID $$(cat $(BOT_PID)), uptime: $${UPTIME:-unknown})"; \
	elif [ -f $(BOT_PID) ]; then \
		echo "❌ Not running (stale PID file — run 'make clean' to remove)"; \
	else \
		echo "❌ Not running"; \
	fi
	@echo ""
	@echo "=== API ==="
	@if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
		UPTIME=$$(ps -o etime= -p $$(cat $(API_PID)) 2>/dev/null | xargs); \
		echo "✅ Running (PID $$(cat $(API_PID)), uptime: $${UPTIME:-unknown})"; \
	elif [ -f $(API_PID) ]; then \
		echo "❌ Not running (stale PID file — run 'make clean' to remove)"; \
	else \
		echo "❌ Not running"; \
	fi

health: ## Check if bot + API + DB + Redis are all healthy
	@echo "=== Health Check ==="
	@ERRORS=0; \
	if [ -f $(BOT_PID) ] && kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then \
		echo "✅ Bot: running"; \
	else echo "❌ Bot: not running"; ERRORS=$$((ERRORS+1)); fi; \
	if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
		echo "✅ API: running"; \
	else echo "❌ API: not running"; ERRORS=$$((ERRORS+1)); fi; \
	if $(COMPOSE) ps 2>/dev/null | grep -q "analyticbot-db.*Up"; then \
		echo "✅ DB: running"; \
	else echo "❌ DB: not running"; ERRORS=$$((ERRORS+1)); fi; \
	if $(COMPOSE) ps 2>/dev/null | grep -q "analyticbot-redis.*Up"; then \
		echo "✅ Redis: running"; \
	else echo "❌ Redis: not running"; ERRORS=$$((ERRORS+1)); fi; \
	echo ""; \
	if [ $$ERRORS -eq 0 ]; then echo "All services healthy ✅"; \
	else echo "$$ERRORS service(s) down ❌"; exit 1; fi

logs: ## Tail bot and API logs
	@tail -f $(LOG_DIR)/bot.log $(LOG_DIR)/api.log 2>/dev/null || echo "No log files yet. Run 'make start' first."

# ── Setup ──────────────────────────────────────────────────────────────────

install: ## Install dependencies
	$(PYTHON) -m pip install -e ".[dev]"

init-db: ## Create database tables
	$(PYTHON) -c "import asyncio; from src.db.session import init_db; asyncio.run(init_db())"
	@echo "✅ Database tables created"

clean: ## Remove PID files, stale processes and logs
	@# Kill any processes still tracked by PID files
	@if [ -f $(BOT_PID) ] && kill -0 $$(cat $(BOT_PID)) 2>/dev/null; then \
		kill $$(cat $(BOT_PID)) 2>/dev/null; echo "Stopped lingering bot process"; fi
	@if [ -f $(API_PID) ] && kill -0 $$(cat $(API_PID)) 2>/dev/null; then \
		kill $$(cat $(API_PID)) 2>/dev/null; echo "Stopped lingering API process"; fi
	rm -rf $(PID_DIR) $(LOG_DIR)/*.log
	@echo "✅ Cleaned (PID files + logs removed)"
