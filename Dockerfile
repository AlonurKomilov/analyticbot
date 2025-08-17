# ---------- Base (build) ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# build deps for psycopg2, orjson, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install deps inside a venv (cached layer)
COPY requirements.txt ./
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

ENV PATH="/opt/venv/bin:${PATH}"

# ---------- Final (runtime) ----------
FROM python:3.11-slim AS final
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
WORKDIR /app

COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# project code
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# --- API image ---
FROM final AS api
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# --- Bot image ---
FROM final AS bot
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "run_bot.py"]

# --- Celery worker image ---
FROM final AS celery_worker
ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "bot.celery_app", "worker", "--loglevel=info"]

# --- Celery beat image ---
FROM final AS celery_beat
ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "bot.celery_app", "beat", "--loglevel=info"]
