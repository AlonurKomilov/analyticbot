# Unified Dockerfile for AnalyticBot
# Multi-stage build for production-ready images

# ---------- Base (build) ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
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

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python environment
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Copy application code
COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\nset -e\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# ---------- API Service ----------
FROM final AS api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---------- Bot Service ----------  
FROM final AS bot
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "apps.bot.run_bot"]

# ---------- Celery Worker ----------
FROM final AS worker
ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "infra.celery.celery_app", "worker", "--loglevel=info", "--concurrency=4"]

# ---------- Celery Beat ----------
FROM final AS beat
ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "infra.celery.celery_app", "beat", "--loglevel=info", "--scheduler=celery.beat:PersistentScheduler"]
