#!/bin/bash
# Quick Setup Script for Resource Management System

set -e

echo "=========================================="
echo "AnalyticBot Resource Management Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root for systemd setup
if [ "$EUID" -eq 0 ]; then
    CAN_SETUP_SYSTEMD=true
else
    CAN_SETUP_SYSTEMD=false
fi

echo -e "${YELLOW}Step 1: Testing Scripts${NC}"
echo "Testing cleanup script..."
/home/abcdeveloper/projects/analyticbot/scripts/cleanup_orphaned_processes.sh
echo -e "${GREEN}✓ Cleanup script working${NC}"

echo ""
echo "Testing monitoring script..."
python3 /home/abcdeveloper/projects/analyticbot/scripts/monitor_resources.py
echo -e "${GREEN}✓ Monitoring script working${NC}"

echo ""
if [ "$CAN_SETUP_SYSTEMD" = true ]; then
    echo -e "${YELLOW}Step 2: Installing Systemd Services${NC}"

    # Copy service files
    cp /home/abcdeveloper/projects/analyticbot/scripts/systemd/analyticbot-cleanup.service /etc/systemd/system/
    cp /home/abcdeveloper/projects/analyticbot/scripts/systemd/analyticbot-cleanup.timer /etc/systemd/system/

    # Reload and enable
    systemctl daemon-reload
    systemctl enable analyticbot-cleanup.timer
    systemctl start analyticbot-cleanup.timer

    echo -e "${GREEN}✓ Systemd services installed and started${NC}"
    echo ""
    systemctl status analyticbot-cleanup.timer --no-pager
else
    echo -e "${YELLOW}Step 2: Systemd Setup (Requires Root)${NC}"
    echo "Run these commands as root to install systemd services:"
    echo ""
    echo "  sudo cp scripts/systemd/analyticbot-cleanup.service /etc/systemd/system/"
    echo "  sudo cp scripts/systemd/analyticbot-cleanup.timer /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable analyticbot-cleanup.timer"
    echo "  sudo systemctl start analyticbot-cleanup.timer"
    echo ""
fi

echo ""
echo -e "${YELLOW}Step 3: Optional - Setup Cron for Monitoring${NC}"
echo "Add this to crontab (runs every 30 minutes):"
echo "  */30 * * * * /home/abcdeveloper/projects/analyticbot/scripts/monitor_resources.py"
echo ""
echo "Run: crontab -e"
echo ""

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "What's configured:"
echo "  ✓ Cleanup script: /home/abcdeveloper/projects/analyticbot/scripts/cleanup_orphaned_processes.sh"
echo "  ✓ Monitoring script: /home/abcdeveloper/projects/analyticbot/scripts/monitor_resources.py"
echo "  ✓ Graceful shutdown: apps/shared/graceful_shutdown.py"
if [ "$CAN_SETUP_SYSTEMD" = true ]; then
    echo "  ✓ Systemd timer: Runs cleanup every hour"
fi
echo ""
echo "Logs:"
echo "  Cleanup:    /tmp/analyticbot_cleanup.log"
echo "  Monitoring: /tmp/analyticbot_monitor.log"
echo ""
echo "Manual commands:"
echo "  Test cleanup:    ./scripts/cleanup_orphaned_processes.sh"
echo "  Test monitoring: python3 scripts/monitor_resources.py"
if [ "$CAN_SETUP_SYSTEMD" = true ]; then
    echo "  Check timer:     systemctl status analyticbot-cleanup.timer"
    echo "  View logs:       journalctl -u analyticbot-cleanup.service"
fi
echo ""
echo "Next steps:"
echo "  1. Read: docs/RESOURCE_MANAGEMENT.md"
echo "  2. Integrate graceful shutdown into MTProto worker"
echo "  3. Setup monitoring cron (optional)"
echo ""
