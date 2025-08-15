# ---------- Base (build) ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# build deps (psycopg, orjson va h.k. kompilyatsiya uchun)
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kechlash uchun avval faqat requirements'ni ko'chiramiz
COPY requirements.txt ./
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

ENV PATH="/opt/venv/bin:${PATH}"

# ---------- Final (runtime) ----------
FROM python:3.11-slim AS final
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# build bosqichida tayyor bo'lgan venv'ni olib kelamiz
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# butun loyiha kodini ko'chiramiz
COPY . .

# API
FROM final AS api
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Bot
FROM final AS bot
CMD ["python", "run_bot.py"]

# Celery worker
FROM final AS celery_worker
CMD ["celery", "-A", "bot.celery_app", "worker", "--loglevel=info"]

# Celery beat
FROM final AS celery_beat
CMD ["celery", "-A", "bot.celery_app", "beat", "--loglevel=info"]
