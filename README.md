# AnalyticBot

AnalyticBot is a FastAPI-based Telegram bot.

## Development Setup

Install dependencies (includes testing packages):

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```

## Quick Start (Docker)

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
```
