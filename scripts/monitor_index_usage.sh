#!/bin/bash

# Database Index Usage Monitoring Script
# Analyzes which indexes are being used and identifies candidates for removal

set -e

CONTAINER="analyticbot-db"
DB_USER="analytic"
DB_NAME="analytic_bot"

echo "========================================"
echo "Database Index Usage Analysis"
echo "Database: $DB_NAME"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

# 1. Overall Statistics
echo "=== Overall Index Statistics ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    COUNT(*) as total_indexes,
    COUNT(*) FILTER (WHERE idx_scan = 0) as unused_indexes,
    COUNT(*) FILTER (WHERE idx_scan > 0) as used_indexes,
    pg_size_pretty(SUM(pg_relation_size(indexrelid))) as total_index_size,
    pg_size_pretty(SUM(pg_relation_size(indexrelid)) FILTER (WHERE idx_scan = 0)) as unused_index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public';
"
echo ""

# 2. Top 10 Most Over-Indexed Tables
echo "=== Top 10 Most Over-Indexed Tables ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    relname as table_name,
    COUNT(*) as total_indexes,
    COUNT(*) FILTER (WHERE idx_scan = 0) as unused_indexes,
    COUNT(*) FILTER (WHERE idx_scan > 0) as used_indexes,
    pg_size_pretty(SUM(pg_relation_size(indexrelid))) as total_index_size,
    pg_size_pretty(SUM(pg_relation_size(indexrelid)) FILTER (WHERE idx_scan = 0)) as unused_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
GROUP BY relname
ORDER BY COUNT(*) DESC, COUNT(*) FILTER (WHERE idx_scan = 0) DESC
LIMIT 10;
"
echo ""

# 3. Unused Indexes by Table (Zero Scans)
echo "=== Unused Indexes (Zero Scans) ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    relname as table_name,
    indexrelname as index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND idx_scan = 0
ORDER BY relname, indexrelname
LIMIT 50;
"
echo ""

# 4. Low-Usage Indexes (< 10 Scans)
echo "=== Low-Usage Indexes (< 10 scans) ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    relname as table_name,
    indexrelname as index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan > 0
  AND idx_scan < 10
ORDER BY idx_scan, relname
LIMIT 30;
"
echo ""

# 5. Most Heavily Used Indexes
echo "=== Top 20 Most Used Indexes ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    relname as table_name,
    indexrelname as index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE
        WHEN idx_scan > 0 THEN ROUND((idx_tup_fetch::numeric / idx_scan), 2)
        ELSE 0
    END as avg_tuples_per_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND idx_scan > 0
ORDER BY idx_scan DESC
LIMIT 20;
"
echo ""

# 6. Duplicate Index Detection (Same Column Combinations)
echo "=== Potential Duplicate/Redundant Indexes ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
WITH index_columns AS (
    SELECT
        schemaname,
        tablename,
        indexname,
        array_agg(attname ORDER BY attnum) as columns
    FROM pg_indexes
    JOIN pg_class ON pg_class.relname = indexname
    JOIN pg_index ON pg_index.indexrelid = pg_class.oid
    JOIN pg_attribute ON pg_attribute.attrelid = pg_index.indrelid
        AND pg_attribute.attnum = ANY(pg_index.indkey)
    WHERE schemaname = 'public'
    GROUP BY schemaname, tablename, indexname
)
SELECT
    tablename,
    array_agg(indexname ORDER BY indexname) as duplicate_indexes,
    columns::text as indexed_columns
FROM index_columns
GROUP BY schemaname, tablename, columns
HAVING COUNT(*) > 1
ORDER BY tablename;
"
echo ""

# 7. Index Efficiency Report
echo "=== Index Efficiency Report ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    relname as table_name,
    indexrelname as index_name,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    CASE
        WHEN idx_scan = 0 THEN 'UNUSED - Remove'
        WHEN idx_scan < 10 THEN 'LOW USAGE - Review'
        WHEN idx_scan < 100 THEN 'MODERATE'
        ELSE 'HIGH USAGE - Keep'
    END as recommendation
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY
    CASE
        WHEN idx_scan = 0 THEN 0
        WHEN idx_scan < 10 THEN 1
        WHEN idx_scan < 100 THEN 2
        ELSE 3
    END,
    idx_scan,
    relname;
"
echo ""

# 8. Table Row Counts vs Index Counts
echo "=== Table Size vs Index Count ==="
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    t.tablename,
    pg_size_pretty(pg_total_relation_size(t.tablename::regclass)) as table_size,
    (SELECT reltuples::bigint FROM pg_class WHERE relname = t.tablename) as estimated_rows,
    COUNT(i.indexname) as index_count,
    pg_size_pretty(SUM(pg_relation_size(i.indexname::regclass))) as total_index_size
FROM pg_tables t
LEFT JOIN pg_indexes i ON t.tablename = i.tablename AND i.schemaname = 'public'
WHERE t.schemaname = 'public'
GROUP BY t.tablename
ORDER BY index_count DESC
LIMIT 15;
"
echo ""

# 9. Recommendations Summary
echo "========================================"
echo "=== RECOMMENDATIONS SUMMARY ==="
echo "========================================"
echo ""
echo "Run this query to get specific DROP INDEX commands:"
echo ""
echo "docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c \""
echo "SELECT 'DROP INDEX CONCURRENTLY ' || indexrelname || ';' as drop_command"
echo "FROM pg_stat_user_indexes"
echo "WHERE schemaname = 'public' AND idx_scan = 0"
echo "ORDER BY relname, indexrelname;"
echo "\""
echo ""
echo "NOTE: Review each index before dropping. Some may be needed for:"
echo "  - Enforcing UNIQUE constraints (keep these!)"
echo "  - Foreign key constraints (check FK definitions)"
echo "  - Recently deployed features (stats may not reflect usage yet)"
echo "  - Background jobs or scheduled tasks"
echo ""
echo "To reset statistics and start fresh monitoring:"
echo "  docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c 'SELECT pg_stat_reset();'"
echo ""
