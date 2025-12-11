# System Scripts - CRITICAL INFRASTRUCTURE

These scripts are essential for running and maintaining the AnalyticBot platform.
DO NOT DELETE these files.

## Contents

### Core Services
- `dev-start.sh` - Main development environment startup script
- `api-watchdog.sh` - Auto-restarts API if it crashes
- `cleanup_orphaned_processes.sh` - Cleans up zombie/orphan processes
- `health-check.sh` - System health monitoring

### Database
- `backup_database.sh` - Database backup script
- `restore_database.sh` - Database restore script

### Deployment
- `deploy-frontend.sh` - Frontend deployment
- `setup-cloudflare-tunnel.sh` - CloudFlare tunnel setup
- `setup-domain.sh` - Domain configuration

### Monitoring
- `monitor_resources.py` - Resource monitoring
- `monitor_query_performance.sh` - DB query performance

## Usage

These scripts are symlinked from the parent `scripts/` directory.
Always use the symlinks to ensure the system folder stays organized.

## Warning

⚠️ Deleting any of these files may break the platform!

