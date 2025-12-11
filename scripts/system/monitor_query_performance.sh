#!/bin/bash
# Query Performance Monitor - Shows slowest database queries
# Uses pg_stat_statements extension to track query execution statistics

set -e

# Load database credentials
if [ -f .env.development ]; then
    export $(grep -v '^#' .env.development | grep -E '^POSTGRES_' | xargs)
    # Strip quotes from password
    export POSTGRES_PASSWORD=$(echo $POSTGRES_PASSWORD | tr -d "'\"")
fi

echo "🔍 Database Query Performance Analysis"
echo "======================================"
echo ""

# Show extension status
echo "📊 Extension Status:"
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c \
    "SELECT '✅ ' || name || ' v' || installed_version || ' installed'
     FROM pg_available_extensions
     WHERE name = 'pg_stat_statements' AND installed_version IS NOT NULL;"
echo ""

# Show top 10 slowest queries by mean execution time
echo "🐌 Top 10 Slowest Queries (by mean execution time):"
echo "---------------------------------------------------"
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" << 'EOSQL'
SELECT
    substring(query, 1, 80) as query_snippet,
    calls,
    round(mean_exec_time::numeric, 2) as avg_ms,
    round(max_exec_time::numeric, 2) as max_ms,
    round(total_exec_time::numeric, 2) as total_ms
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
  AND query NOT LIKE 'SET%'
  AND query NOT LIKE 'SHOW%'
ORDER BY mean_exec_time DESC
LIMIT 10;
EOSQL

echo ""
echo "📈 Top 10 Most Called Queries:"
echo "------------------------------"
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" << 'EOSQL'
SELECT
    substring(query, 1, 80) as query_snippet,
    calls,
    round(mean_exec_time::numeric, 2) as avg_ms,
    round(total_exec_time::numeric, 2) as total_ms
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
  AND query NOT LIKE 'SET%'
  AND query NOT LIKE 'SHOW%'
ORDER BY calls DESC
LIMIT 10;
EOSQL

echo ""
echo "⏱️  Queries Taking >100ms:"
echo "-------------------------"
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" << 'EOSQL'
SELECT
    substring(query, 1, 80) as query_snippet,
    calls,
    round(mean_exec_time::numeric, 2) as avg_ms,
    round(max_exec_time::numeric, 2) as max_ms
FROM pg_stat_statements
WHERE mean_exec_time > 100
  AND query NOT LIKE '%pg_stat%'
ORDER BY mean_exec_time DESC
LIMIT 10;
EOSQL

echo ""
echo "💡 Tips:"
echo "  - Reset stats: SELECT pg_stat_statements_reset();"
echo "  - View all: SELECT * FROM pg_stat_statements;"
echo "  - Monitor logs: tail -f logs/postgres.log"
