#!/bin/bash

# Monitor VACUUM Activity Script
# Provides comprehensive vacuum and table health monitoring
# Created: 2025-11-27 (Issue #9)

set -e

POSTGRES_USER="analytic"
DB_NAME="analytic_bot"
CONTAINER_NAME="analyticbot-db"

echo "============================================"
echo "VACUUM & TABLE HEALTH MONITOR"
echo "============================================"
echo ""

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: PostgreSQL container '$CONTAINER_NAME' is not running"
    exit 1
fi

echo "📊 AUTOVACUUM CONFIGURATION"
echo "-------------------------------------------"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "
SELECT 
    name, 
    setting, 
    unit,
    short_desc
FROM pg_settings 
WHERE name IN (
    'autovacuum',
    'autovacuum_max_workers',
    'autovacuum_naptime',
    'autovacuum_vacuum_threshold',
    'autovacuum_vacuum_scale_factor',
    'autovacuum_analyze_threshold',
    'autovacuum_analyze_scale_factor',
    'autovacuum_vacuum_cost_delay',
    'autovacuum_vacuum_cost_limit'
)
ORDER BY name;
" -x

echo ""
echo "📋 TABLE HEALTH STATUS (Dead Tuples & Bloat)"
echo "-------------------------------------------"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    relname AS table_name,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_percent,
    n_mod_since_analyze AS modifications_since_analyze,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total_size,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_live_tup > 0
ORDER BY n_dead_tup DESC, n_live_tup DESC
LIMIT 20;
"

echo ""
echo "🔧 RECENT VACUUM ACTIVITY (Last 24 Hours)"
echo "-------------------------------------------"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    relname AS table_name,
    last_vacuum,
    last_autovacuum,
    vacuum_count AS manual_vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
WHERE last_autovacuum IS NOT NULL 
   OR last_vacuum IS NOT NULL
   OR vacuum_count > 0
   OR autovacuum_count > 0
ORDER BY GREATEST(last_vacuum, last_autovacuum) DESC NULLS LAST
LIMIT 15;
"

echo ""
echo "⚠️  TABLES NEEDING ATTENTION"
echo "-------------------------------------------"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    relname AS table_name,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_percent,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total_size,
    CASE 
        WHEN last_autovacuum IS NULL AND last_vacuum IS NULL THEN 'NEVER VACUUMED'
        WHEN n_dead_tup > 1000 AND ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 10 THEN 'HIGH BLOAT'
        WHEN n_dead_tup > 500 AND ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 5 THEN 'MODERATE BLOAT'
        ELSE 'OK'
    END AS status
FROM pg_stat_user_tables
WHERE n_live_tup > 0
  AND (
    (n_dead_tup > 500) OR
    (ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 5) OR
    (last_autovacuum IS NULL AND last_vacuum IS NULL)
  )
ORDER BY n_dead_tup DESC
LIMIT 10;
"

echo ""
echo "📈 TABLE-SPECIFIC AUTOVACUUM SETTINGS"
echo "-------------------------------------------"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "
SELECT 
    nspname AS schema,
    relname AS table_name,
    (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_vacuum_threshold') AS vacuum_threshold,
    (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_vacuum_scale_factor') AS vacuum_scale_factor,
    (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_analyze_threshold') AS analyze_threshold,
    (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_analyze_scale_factor') AS analyze_scale_factor,
    (SELECT option_value FROM pg_options_to_table(reloptions) WHERE option_name = 'autovacuum_vacuum_cost_delay') AS vacuum_cost_delay
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE nspname = 'public'
  AND relkind = 'r'
  AND reloptions IS NOT NULL
ORDER BY relname;
"

echo ""
echo "💾 DATABASE SIZE & BLOAT ESTIMATE"
echo "-------------------------------------------"
docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DB_NAME" -c "
SELECT 
    pg_size_pretty(pg_database_size(current_database())) AS database_size,
    COUNT(*) AS total_tables,
    SUM(n_live_tup) AS total_live_tuples,
    SUM(n_dead_tup) AS total_dead_tuples,
    ROUND(100.0 * SUM(n_dead_tup) / NULLIF(SUM(n_live_tup + n_dead_tup), 0), 2) AS overall_dead_percent
FROM pg_stat_user_tables;
"

echo ""
echo "✅ Monitoring complete!"
echo "============================================"
