# Analyticbot v2 — Telegram Channel & Group Analytics

Simplified analytics platform: paste a channel link → get a full analysis report.

## Features

- **One-time channel analysis** — provide a channel link, get instant analytics
- **PDF reports** via Telegram bot
- **Web dashboard** via FastAPI
- **Metrics**: engagement rate, posting patterns, growth trends, top posts, content mix

## Architecture

```
src/
├── analyzer/       # Core analysis engine (fetcher + metrics + insights)
├── api/            # FastAPI web backend + dashboard
├── bot/            # Aiogram Telegram bot (simple: receive link → send PDF)
├── reports/        # PDF/chart generation (Plotly + ReportLab)
└── db/             # PostgreSQL models + repositories
```

## Quick Start

```bash
cp .env.example .env        # Add BOT_TOKEN, API_ID, API_HASH
pip install -e ".[dev]"
python -m src.bot.main       # Run the bot
uvicorn src.api.main:app     # Run the web API
```

## Flow

1. User sends channel link to bot (or submits via web)
2. System resolves channel info via Bot API
3. Telethon fetches last N posts on-demand
4. Analyzer computes metrics (views, engagement, patterns, top posts)
5. Report generated (PDF with charts)
6. Delivered via bot message or web download
