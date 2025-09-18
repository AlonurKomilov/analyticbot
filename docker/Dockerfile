# Unified Dockerfile for AnalyticBot
# Multi-stage build supporting all services: API, Bot, Workers, and Frontend
# Optimized for production with minimal image sizes and enhanced security

# ---------- Python Base Stage ----------
FROM python:3.11-slim AS python-base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Python services
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------- Python Dependencies Stage ----------
FROM python-base AS python-deps
# Install Python dependencies
COPY requirements.prod.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.prod.txt

# ---------- Node.js Base Stage ----------
FROM node:20-slim AS node-base
WORKDIR /app

# Set environment to reduce warnings
ENV DEBIAN_FRONTEND=noninteractive \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

# Install dependencies for building native modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------- Frontend Dependencies Stage ----------
FROM node-base AS frontend-deps
# Copy package files and install dependencies
COPY apps/frontend/package*.json ./
RUN rm -rf node_modules package-lock.json && npm install --omit=dev && npm cache clean --force

# ---------- Frontend Builder Stage ----------
FROM node-base AS frontend-builder
# Copy package files and install all dependencies (including dev)
COPY apps/frontend/package*.json ./
RUN rm -rf node_modules package-lock.json && npm install

# Copy source code and build
COPY apps/frontend/ ./
RUN npm run build

# ---------- Python Runtime Stage ----------
FROM python:3.11-slim AS python-runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python environment from deps stage
COPY --from=python-deps /opt/venv /opt/venv
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
FROM python-runtime AS api
EXPOSE 10300
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10300/health || exit 1
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "10300"]

# ---------- Bot Service ----------  
FROM python-runtime AS bot
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "apps.bot.run_bot"]

# ---------- Celery Worker ----------
FROM python-runtime AS worker
ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "infra.celery.celery_app", "worker", "--loglevel=info", "--concurrency=4"]

# ---------- Celery Beat ----------
FROM python-runtime AS beat
ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "infra.celery.celery_app", "beat", "--loglevel=info", "--scheduler=celery.beat:PersistentScheduler"]

# ---------- MTProto Service ----------
FROM python-runtime AS mtproto
EXPOSE 8091
HEALTHCHECK --interval=60s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8091/health || exit 1
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "apps.mtproto.tasks.poll_updates"]

# ---------- Frontend Production ----------
FROM nginx:alpine AS frontend
# Copy custom nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Create non-root user for nginx
RUN addgroup -g 1001 -S nextjs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nextjs /usr/share/nginx/html \
    && chown -R nextjs:nextjs /var/run \
    && chown -R nextjs:nextjs /var/log/nginx \
    && chown -R nextjs:nextjs /etc/nginx

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 10400

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

# Create non-root user
RUN groupadd -r devuser && useradd -r -g devuser -u 1001 devuser \
    && chown -R devuser:devuser /app

USER devuser

# Expose development port
EXPOSE 11400

# Health check for development
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:11400/ || exit 1

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "11400"]