# Unified Dockerfile for AnalyticBot
# Multi-stage build for production-ready images

# ---------- Base (build) ----------
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.prod.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.prod.txt

ENV PATH="/opt/venv/bin:${PATH}"

# ---------- Final (runtime) ----------
FROM python:3.11-slim AS final
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python environment
COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app /opt/venv

# Create entrypoint script
RUN echo '#!/bin/bash\nset -e\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    chown appuser:appuser /entrypoint.sh

# Switch to non-root user
USER appuser

# ---------- API Service ----------
FROM final AS api
EXPOSE 10300
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10300/health || exit 1
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "10300"]

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
