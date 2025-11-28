#!/bin/bash
# Deploy Smart Retention System - Database Only
# No application containers needed

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Smart Data Retention - Database Only Deployment                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

DB_CONTAINER="analyticbot-db"
DB_USER="analytic"
DB_NAME="analytic_bot"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if database is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${RED}Error: Database container '$DB_CONTAINER' is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Database container is running${NC}"
echo ""

# Step 1: Backup
echo -e "${YELLOW}Step 1: Creating backup...${NC}"
BACKUP_FILE="backup_smart_retention_$(date +%Y%m%d_%H%M%S).sql"
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -F c -f "/tmp/$BACKUP_FILE"
docker cp "$DB_CONTAINER:/tmp/$BACKUP_FILE" "../backups/"
echo -e "${GREEN}✓ Backup created: backups/$BACKUP_FILE${NC}"
echo ""

# Step 2: Create table and indexes
echo -e "${YELLOW}Step 2: Creating post_metrics_checks table...${NC}"
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$SCRIPT_DIR/deploy_smart_retention_db_only.sql"
echo -e "${GREEN}✓ Table created successfully${NC}"
echo ""

# Step 3: Ask about cleanup
echo -e "${YELLOW}Step 3: Clean duplicate data?${NC}"
echo ""
echo "This will remove duplicate snapshots from post_metrics table."
echo "Expected: Reduce from 6.9M records to ~374K (95% reduction)"
echo ""
echo -e "${YELLOW}Do you want to proceed with cleanup? (yes/no)${NC}"
read -r response

if [[ "$response" != "yes" ]]; then
    echo -e "${YELLOW}Skipping cleanup. Table created but duplicates remain.${NC}"
    echo "You can run cleanup later with:"
    echo "  docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < scripts/cleanup_duplicates_db_only.sql"
    exit 0
fi

# Step 4: Run cleanup
echo ""
echo -e "${YELLOW}Step 4: Running cleanup (this may take 5-10 minutes)...${NC}"
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$SCRIPT_DIR/cleanup_duplicates_db_only.sql"
echo ""
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 5: Final verification
echo -e "${YELLOW}Step 5: Verifying results...${NC}"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    'FINAL RESULT' as status,
    pg_size_pretty(pg_total_relation_size('post_metrics')) as storage,
    COUNT(*) as records,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT (channel_id, msg_id)), 1) as avg_snapshots_per_post
FROM post_metrics;
"
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Deployment Complete!                                         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 What was done:"
echo "   • Created post_metrics_checks table"
echo "   • Removed duplicate snapshots"
echo "   • Reclaimed disk space (VACUUM)"
echo ""
echo "⚠️  IMPORTANT: When you start your application containers:"
echo "   • Smart collection tasks will activate automatically"
echo "   • They will only save changed metrics going forward"
echo "   • Users will see no difference in update frequency"
echo ""
echo "📚 Backup location: backups/$BACKUP_FILE"
echo ""
