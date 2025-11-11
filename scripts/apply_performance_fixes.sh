#!/bin/bash
# Quick Performance Fix Script
# Applies critical performance optimizations immediately

set -e

echo "========================================"
echo "Performance Optimization Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This script will apply the following optimizations:${NC}"
echo "1. Add composite index for LATERAL join performance"
echo "2. Run ANALYZE on post_metrics table"
echo ""
echo -e "${YELLOW}Expected improvements:${NC}"
echo "- Posts API: 3-4x faster (800ms → 200ms)"
echo "- Analytics API: 3-4x faster (3s → 800ms)"
echo ""

read -p "Do you want to proceed? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo -e "${GREEN}Step 1: Creating composite index for LATERAL joins...${NC}"
echo "This may take 1-2 minutes on large datasets..."

# Apply index with CONCURRENTLY to avoid locking the table
psql analyticbot <<EOF
-- Create index for LATERAL join optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_metrics_lateral_lookup
ON post_metrics (channel_id, msg_id, snapshot_time DESC);

-- Update query planner statistics
ANALYZE post_metrics;

-- Verify index was created
\di idx_post_metrics_lateral_lookup
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Index created successfully!${NC}"
else
    echo -e "${RED}✗ Failed to create index${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 2: Checking index statistics...${NC}"
psql analyticbot -c "
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE indexname = 'idx_post_metrics_lateral_lookup';
"

echo ""
echo -e "${GREEN}Step 3: Verifying table size and row count...${NC}"
psql analyticbot -c "
SELECT
    COUNT(*) as total_metrics,
    COUNT(DISTINCT channel_id) as channels,
    COUNT(DISTINCT (channel_id, msg_id)) as unique_posts,
    pg_size_pretty(pg_total_relation_size('post_metrics')) as total_size
FROM post_metrics;
"

echo ""
echo "========================================"
echo -e "${GREEN}✓ Performance optimization complete!${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart backend API: docker-compose restart api"
echo "2. Restart frontend: npm run dev (in apps/frontend)"
echo "3. Test performance improvements"
echo ""
echo -e "${YELLOW}Monitoring:${NC}"
echo "- Watch query performance in PostgreSQL logs"
echo "- Check X-Process-Time header in API responses"
echo "- MTProto monitoring page should now refresh every 2 seconds"
echo ""
