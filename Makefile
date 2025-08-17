# Makefile for AnalyticBot

# Ensure .env file exists
ifeq (,$(wildcard ./.env))
    $(shell cp .env.example .env)
endif

.PHONY: help up down logs ps migrate lint typecheck test

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
