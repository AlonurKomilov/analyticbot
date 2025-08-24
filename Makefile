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
