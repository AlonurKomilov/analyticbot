#!/bin/bash
# Deploy Smart Data Retention System
# This script deploys the change detection system to reduce storage by 90-95%

set -e

echo "🚀 Deploying Smart Data Retention System"
echo "=========================================="
echo ""

# Configuration
DB_CONTAINER="analyticbot-db"
DB_USER="analytic"
DB_NAME="analytic_bot"
BACKUP_DIR="./backups/smart_retention_deployment_$(date +%Y%m%d_%H%M%S)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Create backup
echo -e "${YELLOW}Step 1: Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME -Fc -f /tmp/backup_before_smart_retention.dump
docker cp $DB_CONTAINER:/tmp/backup_before_smart_retention.dump "$BACKUP_DIR/"
echo -e "${GREEN}✓ Backup created: $BACKUP_DIR/backup_before_smart_retention.dump${NC}"
echo ""

# Step 2: Run migration to create post_metrics_checks table
echo -e "${YELLOW}Step 2: Running migration 0038 (create post_metrics_checks table)...${NC}"
docker exec analyticbot-api python -m alembic upgrade head
echo -e "${GREEN}✓ Migration applied${NC}"
echo ""

# Step 3: Analyze current storage
echo -e "${YELLOW}Step 3: Analyzing current storage usage...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
    SELECT 
        'post_metrics' as table_name,
        pg_size_pretty(pg_total_relation_size('post_metrics')) as total_size,
        COUNT(*) as row_count,
        COUNT(DISTINCT (channel_id, msg_id)) as unique_posts
    FROM post_metrics;
"
echo ""

# Step 4: Run duplicate cleanup (dry run first)
echo -e "${YELLOW}Step 4: Running duplicate detection (dry run)...${NC}"
echo "This will analyze how many duplicates can be removed."
echo ""

# Create temporary Python script for cleanup
cat > /tmp/run_cleanup.py << 'EOF'
import asyncio
from apps.celery.tasks.smart_analytics_tasks import cleanup_duplicate_post_metrics

async def main():
    result = await cleanup_duplicate_post_metrics(dry_run=True, batch_size=10000)
    print(f"\n📊 Dry Run Results:")
    print(f"   Total records: {result['total_before']:,}")
    print(f"   Duplicates found: {result['duplicates_found']:,}")
    print(f"   Potential savings: {result['duplicates_found'] / result['total_before'] * 100:.1f}%")
    print(f"   Duration: {result['duration_seconds']:.2f}s")
    return result

if __name__ == "__main__":
    asyncio.run(main())
EOF

docker cp /tmp/run_cleanup.py analyticbot-api:/app/
docker exec analyticbot-api python /tmp/run_cleanup.py
rm /tmp/run_cleanup.py
echo ""

# Step 5: Ask for confirmation
echo -e "${YELLOW}Step 5: Confirmation required${NC}"
echo ""
echo "The smart retention system is ready to deploy. This will:"
echo "  1. Keep checking posts as frequently as before (users see no change)"
echo "  2. Only save snapshots when metrics actually change"
echo "  3. Remove existing duplicate snapshots from database"
echo "  4. Reduce storage by 90-95%"
echo ""
echo -e "${YELLOW}⚠️  Do you want to proceed with cleanup? (yes/no)${NC}"
read -r response

if [[ "$response" != "yes" ]]; then
    echo -e "${RED}Deployment cancelled. Smart collection tasks are installed but not cleaning old data.${NC}"
    echo "You can manually run cleanup later with:"
    echo "  docker exec analyticbot-api python -c 'from apps.celery.tasks.smart_analytics_tasks import cleanup_duplicate_post_metrics; import asyncio; asyncio.run(cleanup_duplicate_post_metrics(dry_run=False))'"
    exit 0
fi

# Step 6: Run actual cleanup
echo ""
echo -e "${YELLOW}Step 6: Running duplicate cleanup (LIVE)...${NC}"
echo "This may take several minutes depending on data volume..."
echo ""

cat > /tmp/run_cleanup_live.py << 'EOF'
import asyncio
from apps.celery.tasks.smart_analytics_tasks import cleanup_duplicate_post_metrics

async def main():
    result = await cleanup_duplicate_post_metrics(dry_run=False, batch_size=10000)
    print(f"\n🎉 Cleanup Complete!")
    print(f"   Records before: {result['total_before']:,}")
    print(f"   Duplicates removed: {result['duplicates_removed']:,}")
    print(f"   Records after: {result['unique_kept']:,}")
    print(f"   Savings: {result['duplicates_removed'] / result['total_before'] * 100:.1f}%")
    print(f"   Duration: {result['duration_seconds']:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
EOF

docker cp /tmp/run_cleanup_live.py analyticbot-api:/app/
docker exec analyticbot-api python /tmp/run_cleanup_live.py
rm /tmp/run_cleanup_live.py
echo ""

# Step 7: Verify results
echo -e "${YELLOW}Step 7: Verifying results...${NC}"
docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "
    SELECT 
        'post_metrics' as table_name,
        pg_size_pretty(pg_total_relation_size('post_metrics')) as total_size,
        COUNT(*) as row_count,
        COUNT(DISTINCT (channel_id, msg_id)) as unique_posts,
        ROUND(COUNT(*)::numeric / COUNT(DISTINCT (channel_id, msg_id)), 1) as avg_snapshots_per_post
    FROM post_metrics;
"
echo ""

# Step 8: Restart Celery workers
echo -e "${YELLOW}Step 8: Restarting Celery workers to activate smart collection...${NC}"
docker-compose restart analyticbot-celery
echo -e "${GREEN}✓ Celery restarted${NC}"
echo ""

# Step 9: Success summary
echo ""
echo -e "${GREEN}=========================================="
echo "✅ Smart Data Retention System Deployed!"
echo "==========================================${NC}"
echo ""
echo "📊 What's happening now:"
echo "   • Smart collection tasks are running on schedule:"
echo "     - Fresh posts (<1h): Every 10 minutes"
echo "     - Recent posts (1-24h): Every 30 minutes"
echo "     - Daily posts (1-7d): Every 6 hours"
echo "     - Weekly posts (>7d): Once per day"
echo ""
echo "   • Only snapshots with changed metrics will be saved"
echo "   • Users will still see real-time updates (no change for them)"
echo "   • Storage will grow 90-95% slower"
echo ""
echo "📈 Monitoring:"
echo "   View efficiency stats:"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" https://your-api/owner/database/smart-collection/stats"
echo ""
echo "   View storage analysis:"
echo "   curl -H \"Authorization: Bearer YOUR_TOKEN\" https://your-api/owner/database/storage-analysis"
echo ""
echo "💾 Backup location: $BACKUP_DIR"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
