# AnalyticBot

AnalyticBot is a FastAPI-based Telegram bot.

## Features
- Aiogram v3 bot with Redis FSM & asyncpg
- Subscription & plan limits (channels/posts)
- Scheduled posting with Celery
- Post analytics (views tracking) + basic PNG chart generation
- Guard (word blacklist) per channel (regex tokenization)
- i18n (English / Uzbek) with safe fallbacks
- Automated CI: lint, type-check, security scan (Bandit), dependency audit (pip-audit)
- AI assisted & deterministic CI autofix workflows

## Development Setup

Install dependencies (includes testing packages):

```bash
pip install -r requirements.txt
```
If you see connection errors for the bot or worker at first startup, it may simply be Alembic migrations not yet applied inside the running containers. Run the migration container (or exec into the API) to apply them:

```bash
docker compose exec api alembic upgrade head
```

## Running Tests

```bash
pytest
pytest -q  # quiet
```

## Quick Start (Docker)
When using Docker you can instead rely on the compose services:
```bash
docker compose logs -f celery_worker
```

```bash
cp .env.example .env
```

Now, edit the `.env` file with your actual `BOT_TOKEN` and other parameters if needed.

Then, run the services:

```bash
docker compose up -d --build
```

### Health Check

To verify that the API is running, you can send a request to the health check endpoint:

```bash
curl http://localhost:8000/health
```

You should see the following response:

```json
{"status":"ok"}

## Database Migrations
Apply latest:
```bash
alembic upgrade head
```
Create new revision:
```bash
alembic revision -m "message"
```

## Celery Tasks
- `bot.tasks.update_post_views_task` updates stored Telegram post views.
- `bot.tasks.send_post_task` placeholder for dispatching due posts.

Run worker (example):
```bash
celery -A bot.celery_app.celery_app worker -l info
```

## Environment
See `bot/config.py` for required env variables. Example `.env.example` should be copied to `.env` and adjusted.

## Security Notes
- Telegram WebApp init data validated with HMAC and 1h freshness window.
- Secrets scanning & vulnerability audit included in CI.

## Roadmap (Suggestions)
- Ownership check in `get_post_views`
- Richer analytics (CTR, growth)
- Web dashboard expansion
- Rate limiting / flood control

```
