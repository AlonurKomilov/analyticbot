# Base
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --upgrade pip && /opt/venv/bin/pip install -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

# Final runtime (common)
FROM python:3.11-slim AS final
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

# Targets
FROM final AS api
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

FROM final AS bot
CMD ["python", "run_bot.py"]

FROM final AS celery_worker
CMD ["celery", "-A", "bot.celery_app", "worker", "--loglevel=info"]

FROM final AS celery_beat
CMD ["celery", "-A", "bot.celery_app", "beat", "--loglevel=info"]
