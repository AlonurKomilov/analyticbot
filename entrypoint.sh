#!/usr/bin/env bash
set -euo pipefail

: "Wait for Postgres and Redis to become available, then run Alembic migrations and exec the CMD"

# Defaults
PG_HOST=${POSTGRES_HOST:-${POSTGRES_HOST:-postgres}}
PG_PORT=${POSTGRES_PORT:-5432}
PG_USER=${POSTGRES_USER:-analytic}
PG_DB=${POSTGRES_DB:-analytic_bot}
REDIS_HOST=${REDIS_HOST:-${REDIS_HOST:-redis}}
REDIS_PORT=${REDIS_PORT:-6379}

echo "[entrypoint] waiting for Postgres at ${PG_HOST}:${PG_PORT}..."
# Wait for Postgres
for i in {1..60}; do
  if pg_isready -h "${PG_HOST}" -p "${PG_PORT}" -U "${PG_USER}" -d "${PG_DB}" >/dev/null 2>&1; then
    echo "[entrypoint] Postgres is up"
    break
  fi
  echo "[entrypoint] still waiting for Postgres... ($i)"
  sleep 2
done

# Wait for Redis
echo "[entrypoint] waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
for i in {1..60}; do
  if redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping >/dev/null 2>&1; then
    echo "[entrypoint] Redis is up"
    break
  fi
  echo "[entrypoint] still waiting for Redis... ($i)"
  sleep 1
done

# Run migrations if alembic is present
if command -v alembic >/dev/null 2>&1; then
  echo "[entrypoint] running alembic upgrade head"
  alembic upgrade head || echo "[entrypoint] alembic failed (continuing)"
else
  echo "[entrypoint] alembic not found, skipping migrations"
fi

# Exec the passed command
exec "$@"
