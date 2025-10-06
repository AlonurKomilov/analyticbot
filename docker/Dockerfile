# Unified Dockerfile for AnalyticBot - Alpine Optimized
# Multi-stage build supporting all services: API, Bot, Workers, and Frontend
# Optimized for production with minimal image sizes using Alpine Linux

# ---------- Python Base Stage (Alpine) ----------
FROM python:3.11-alpine AS python-base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

# Install system dependencies for Python services (Alpine packages)
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    && apk add --no-cache \
    curl \
    git \
    postgresql-client \
    tini \
    ca-certificates

WORKDIR /app

# ---------- Python Dependencies Stage ----------
FROM python-base AS python-deps
# Copy only dependency files for optimal caching
COPY requirements.prod.txt pyproject.toml ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.prod.txt \
    # Clean up build dependencies and Python cache
    && apk del .build-deps \
    && find /opt/venv -type f -name "*.py[co]" -delete \
    && find /opt/venv -type d -name "__pycache__" -delete

# ---------- Node.js Base Stage (Alpine) ----------
FROM node:20-alpine AS node-base
WORKDIR /app

# Set environment to reduce warnings
ENV NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

# Install dependencies for building native modules
RUN apk add --no-cache --virtual .node-build-deps \
    python3 \
    make \
    g++ \
    && apk add --no-cache \
    git \
    curl \
    ca-certificates

# ---------- Frontend Dependencies Stage ----------
FROM node-base AS frontend-deps
# Copy package files and install production dependencies only
COPY apps/frontend/package*.json ./
RUN rm -rf node_modules package-lock.json \
    && npm ci --omit=dev --no-audit --no-fund \
    && npm cache clean --force

# ---------- Frontend Builder Stage ----------
FROM node-base AS frontend-builder
# Copy package files first for optimal caching
COPY apps/frontend/package*.json ./

# Install all dependencies (including dev)
RUN rm -rf node_modules package-lock.json \
    && npm ci --no-audit --no-fund

# Copy source code only after dependencies are installed
COPY apps/frontend/src/ ./src/
COPY apps/frontend/public/ ./public/
COPY apps/frontend/index.html apps/frontend/vite.config.* apps/frontend/tsconfig.* ./

# Build the application and clean up
RUN npm run build \
    && apk del .node-build-deps \
    && rm -rf node_modules src public *.json *.config.* \
    && npm cache clean --force

# ---------- Python Runtime Stage (Alpine) ----------
FROM python:3.11-alpine AS python-runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

# Install runtime dependencies only
RUN apk add --no-cache \
    postgresql-libs \
    libgomp \
    curl \
    ca-certificates \
    tini

WORKDIR /app

# Use tini as PID 1 for proper signal handling
ENTRYPOINT ["tini", "--"]

# Copy Python environment from deps stage
COPY --from=python-deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Create non-root user for security (Alpine syntax)
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser

# Create entrypoint script
RUN echo '#!/bin/sh\nset -e\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Copy application code in strategic order for better caching
# 1. Copy core/shared modules first (changes less frequently)
COPY core/ ./core/
COPY infra/ ./infra/
COPY config/ ./config/

# 2. Copy application-specific code (changes more frequently)
COPY apps/ ./apps/

# 3. Copy configuration files and scripts
COPY alembic.ini pyproject.toml requirements*.txt ./
COPY scripts/ ./scripts/

# Set ownership after copying all files
RUN chown -R appuser:appuser /app /opt/venv /entrypoint.sh

# Switch to non-root user
USER appuser

# ---------- API Service ----------
FROM python-runtime AS api
EXPOSE 10400
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:10400/health | grep -o '"status":"[^"]*"' | grep -q '"status":"ok"' || exit 1
CMD ["/entrypoint.sh", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "10400"]

# ---------- Bot Service ----------
FROM python-runtime AS bot
CMD ["/entrypoint.sh", "python", "-m", "apps.bot.run_bot"]

# ---------- Celery Worker ----------
FROM python-runtime AS worker
CMD ["/entrypoint.sh", "celery", "-A", "apps.celery.celery_app", "worker", "--loglevel=info", "--concurrency=4"]

# ---------- Celery Beat ----------
FROM python-runtime AS beat
CMD ["/entrypoint.sh", "celery", "-A", "apps.celery.celery_app", "beat", "--loglevel=info", "--scheduler=celery.beat:PersistentScheduler"]

# ---------- MTProto Service ----------
FROM python-runtime AS mtproto
EXPOSE 8091
HEALTHCHECK --interval=60s --timeout=15s --start-period=30s --retries=3 \
    CMD python -c "import asyncio; from apps.mtproto.health import HealthCheck; hc = HealthCheck(); print(asyncio.run(hc.get_liveness_status()))" || exit 1
CMD ["/entrypoint.sh", "python", "-m", "apps.mtproto.tasks.poll_updates"]

# ---------- Frontend Production (Alpine Nginx) ----------
FROM nginx:alpine AS frontend
# Copy custom nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Create non-root user for nginx (Alpine syntax)
RUN addgroup -g 1001 -S nextjs && \
    adduser -S nextjs -u 1001 -G nextjs && \
    chown -R nextjs:nextjs /usr/share/nginx/html \
    && chown -R nextjs:nextjs /var/run \
    && chown -R nextjs:nextjs /var/log/nginx \
    && chown -R nextjs:nextjs /etc/nginx

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 10300

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# ---------- Frontend Development ----------
FROM node-base AS frontend-dev
# Copy package files and install all dependencies
COPY apps/frontend/package*.json ./
RUN npm ci --no-optional

# Copy source code
COPY apps/frontend/ ./

# Create non-root user (Alpine syntax)
RUN addgroup -g 1001 -S devuser && \
    adduser -u 1001 -S devuser -G devuser && \
    chown -R devuser:devuser /app

# Clean up build dependencies for dev image
RUN apk del .node-build-deps

USER devuser

# Expose development port
EXPOSE 11300

# Health check for development
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:11300/ || exit 1

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "11300"]
