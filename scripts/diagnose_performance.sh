#!/bin/bash

###############################################################################
# Performance Diagnosis Script
# Identifies why recommendation API is slow (4+ minutes)
###############################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }

DB_URL="postgresql://analytic:change_me@localhost:10100/analytic_bot"
CHANNEL_ID="-1002000495734"
DAYS=30

echo "════════════════════════════════════════════════════════"
echo "  Performance Diagnosis Report"
echo "════════════════════════════════════════════════════════"
echo ""

# 1. Check database connection
log_info "1. Testing database connection..."
if psql "$DB_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    log_success "Database connection OK"
else
    log_error "Cannot connect to database"
    exit 1
fi
echo ""

# 2. Check table sizes
log_info "2. Checking table sizes..."
psql "$DB_URL" -c "
SELECT
    relname as table,
    pg_size_pretty(pg_total_relation_size(relname::regclass)) AS size,
    n_live_tup as rows
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname IN ('posts', 'post_metrics')
ORDER BY pg_total_relation_size(relname::regclass) DESC;
"
echo ""

# 3. Check index usage
log_info "3. Checking index usage statistics..."
psql "$DB_URL" -c "
SELECT
    schemaname,
    relname as table,
    indexrelname as index,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND relname IN ('posts', 'post_metrics')
  AND indexrelname LIKE 'idx_%'
ORDER BY idx_scan DESC
LIMIT 10;
"
echo ""

# 4. Check for locks
log_info "4. Checking for database locks..."
LOCKS=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM pg_locks WHERE NOT granted;")
if [ "$LOCKS" -gt 0 ]; then
    log_warning "Found $LOCKS ungranted locks"
    psql "$DB_URL" -c "SELECT * FROM pg_locks WHERE NOT granted;"
else
    log_success "No blocking locks"
fi
echo ""

# 5. Check connection count
log_info "5. Checking active connections..."
psql "$DB_URL" -c "
SELECT
    state,
    COUNT(*) as connections,
    MAX(EXTRACT(EPOCH FROM (NOW() - query_start))) as max_duration_seconds
FROM pg_stat_activity
WHERE datname = 'analytic_bot'
GROUP BY state
ORDER BY connections DESC;
"
echo ""

# 6. Test simple query performance
log_info "6. Testing simple aggregation query..."
START=$(date +%s%N)
COUNT=$(psql "$DB_URL" -t -c "
SELECT COUNT(*)
FROM posts p
WHERE p.channel_id = $CHANNEL_ID
  AND p.date >= NOW() - INTERVAL '$DAYS days'
  AND p.is_deleted = FALSE;
")
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))
log_success "Simple COUNT query: ${DURATION}ms (${COUNT} posts)"
echo ""

# 7. Test with JOIN
log_info "7. Testing JOIN query performance..."
START=$(date +%s%N)
psql "$DB_URL" -t -c "
SELECT
    EXTRACT(HOUR FROM p.date) as hour,
    COUNT(*) as post_count,
    AVG(pm.views) as avg_views
FROM posts p
LEFT JOIN post_metrics pm ON p.channel_id = pm.channel_id AND p.msg_id = pm.msg_id
WHERE p.channel_id = $CHANNEL_ID
  AND p.date >= NOW() - INTERVAL '$DAYS days'
  AND p.is_deleted = FALSE
GROUP BY hour
ORDER BY hour
LIMIT 5;
" > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

if [ $DURATION -lt 1000 ]; then
    log_success "JOIN query: ${DURATION}ms (GOOD)"
elif [ $DURATION -lt 3000 ]; then
    log_warning "JOIN query: ${DURATION}ms (ACCEPTABLE)"
else
    log_error "JOIN query: ${DURATION}ms (SLOW)"
fi
echo ""

# 8. Test EXTRACT performance
log_info "8. Testing EXTRACT() performance..."
START=$(date +%s%N)
psql "$DB_URL" -t -c "
SELECT
    EXTRACT(DOW FROM date) as dow,
    EXTRACT(HOUR FROM date) as hour,
    COUNT(*) as cnt
FROM posts
WHERE channel_id = $CHANNEL_ID
  AND date >= NOW() - INTERVAL '$DAYS days'
  AND is_deleted = FALSE
GROUP BY dow, hour
LIMIT 10;
" > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

if [ $DURATION -lt 2000 ]; then
    log_success "EXTRACT query: ${DURATION}ms (GOOD)"
else
    log_error "EXTRACT query: ${DURATION}ms (SLOW - missing functional indexes)"
fi
echo ""

# 9. Check statistics freshness
log_info "9. Checking table statistics freshness..."
psql "$DB_URL" -c "
SELECT
    schemaname,
    relname as table,
    last_analyze,
    last_autoanalyze,
    n_mod_since_analyze as mods
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname IN ('posts', 'post_metrics')
ORDER BY relname;
"
echo ""

# 10. Recommendations
echo "════════════════════════════════════════════════════════"
echo "  Recommendations"
echo "════════════════════════════════════════════════════════"

if [ $DURATION -gt 2000 ]; then
    echo "1. ⚠️  EXTRACT() queries are slow - create IMMUTABLE wrapper functions"
    echo "2. 🔧 Run VACUUM ANALYZE on posts and post_metrics tables"
    echo "3. 📊 Consider simplifying CTE query structure"
fi

echo "4. 🧪 Test with ENABLE_ADVANCED_RECOMMENDATIONS=false"
echo "5. 🔍 Run EXPLAIN ANALYZE on full recommendation query"
echo ""

log_info "Diagnosis complete. Check results above."
