# Database Backup Strategy - AnalyticBot
**Date:** November 26, 2025
**Current Database Size:** 1.66 GB
**Current Server:** VPS with 96GB disk (38GB used, 58GB available)

---

## 📋 Executive Summary

This document outlines a comprehensive **3-tier backup strategy** for the AnalyticBot PostgreSQL database:

1. **🔄 Automated Local Backups** - Daily snapshots on server (fast recovery)
2. **☁️ Cloud Storage Backups** - Off-site storage for disaster recovery
3. **👑 Owner Dashboard** - Web interface for backup management & monitoring (Owner-only access)

**Key Features:**
- ✅ One-click backup from owner dashboard
- ✅ Automated daily backups (3 AM)
- ✅ Real-time database size monitoring
- ✅ Cloud storage with multiple providers (S3/Backblaze/Google Cloud)
- ✅ Point-in-time recovery (PITR)
- ✅ Backup verification & integrity checks
- ✅ Email alerts on backup failures
- ✅ 30-day retention policy
- ✅ Encrypted backups

---

## 🔐 Access Control - Owner Only

**IMPORTANT:** All database backup features are restricted to the **OWNER role only**.

### User Role Hierarchy:
```
viewer (Level 0)    - Public read-only access
user (Level 1)      - Your customers (paying users)
moderator (Level 2) - Support team
admin (Level 3)     - Platform administrators
owner (Level 4)     - PROJECT OWNER (YOU) ← Only role with backup access
```

### Why Owner-Only?
- 🔒 **Security:** Database backups contain ALL customer data
- 👥 **Separation:** Regular users/admins are customers, not system operators
- 🛡️ **Compliance:** Minimize access to sensitive data dumps
- 🎯 **Responsibility:** Only project owner should manage system-level operations

### Access Matrix:
| Role | Backup Access | Reason |
|------|--------------|--------|
| **owner** | ✅ FULL ACCESS | Project owner, system administrator |
| admin | ❌ NO ACCESS | Platform admin, manages users not infrastructure |
| moderator | ❌ NO ACCESS | Support team, content moderation only |
| user | ❌ NO ACCESS | Your customers using the application |
| viewer | ❌ NO ACCESS | Public/demo users |

---

## 🎯 Backup Strategy Overview

### Current State Analysis
```
✓ Database Size: 1.66 GB (manageable)
✓ Disk Space: 58 GB available
✓ Growth Rate: ~100 MB/week (estimated)
✓ Tables: 39 tables, 2,772 posts
✓ Owner Dashboard: Available in SuperAdmin panel (owner role only)
```

### Strategy Tiers

#### **Tier 1: Local Automated Backups** (Fast Recovery)
- **Location:** `/home/abcdeveloper/backups/database/`
- **Frequency:** Daily at 3 AM
- **Retention:** Last 7 days (rolling)
- **Format:** Compressed SQL dumps (`.sql.gz`)
- **Size:** ~200-300 MB per backup (with compression)
- **Recovery Time:** 5-10 minutes
- **Use Case:** Quick rollback for recent issues

#### **Tier 2: Cloud Storage Backups** (Disaster Recovery)
- **Location:** AWS S3 / Backblaze B2 / Google Cloud Storage
- **Frequency:** Daily (after local backup)
- **Retention:** 30 days
- **Format:** Encrypted compressed SQL dumps
- **Cost:** $0.50-2.00/month (for 1.66 GB × 30 days)
- **Recovery Time:** 30-60 minutes (download + restore)
- **Use Case:** Server failure, data center issues

#### **Tier 3: Point-in-Time Recovery (PITR)** (Advanced)
- **Location:** Local + Cloud WAL archives
- **Frequency:** Continuous (Write-Ahead Logs)
- **Retention:** 7 days
- **Format:** PostgreSQL WAL files
- **Recovery Time:** 10-20 minutes
- **Use Case:** Restore to exact moment before corruption

---

## 🏗️ Implementation Plan

### Phase 1: Local Backup System (Week 1)
**Priority:** HIGH | **Effort:** 4 hours

#### 1.1 Create Backup Script
```bash
# Location: scripts/backup_database.sh
- Automated pg_dump with compression
- Backup validation
- Old backup cleanup
- Email notifications
```

#### 1.2 Setup Cron Job
```bash
# Daily backups at 3 AM
0 3 * * * /home/abcdeveloper/projects/analyticbot/scripts/backup_database.sh
```

#### 1.3 Create Restore Script
```bash
# Location: scripts/restore_database.sh
- List available backups
- Validate backup before restore
- Create pre-restore snapshot
- Restore with progress
```

**Deliverables:**
- ✅ `scripts/backup_database.sh`
- ✅ `scripts/restore_database.sh`
- ✅ `scripts/verify_backup.sh`
- ✅ Cron configuration
- ✅ Email alerting

---

### Phase 2: Owner Dashboard (Week 2)
**Priority:** HIGH | **Effort:** 8 hours

#### 2.1 Database Monitoring Dashboard
**Location:** SuperAdmin Panel → Database Management (Owner Role Only)
**Access Control:** Only users with 'owner' role can access this section

**Features:**
```typescript
interface DatabaseStats {
  size: string;              // "1.66 GB"
  tables: number;            // 39
  totalRecords: number;      // ~100K
  growth: {
    daily: string;           // "+50 MB"
    weekly: string;          // "+350 MB"
    monthly: string;         // "+1.4 GB"
  };
  lastBackup: {
    timestamp: Date;
    size: string;
    status: "success" | "failed";
    location: "local" | "cloud";
  };
}
```

**UI Components:**
1. **Database Size Chart** - Real-time size tracking
2. **Backup History Table** - Last 30 backups
3. **Storage Usage Gauge** - Local disk space
4. **Quick Actions Panel**:
   - 🔄 Backup Now (manual trigger)
   - 📥 Download Backup
   - ♻️ Restore from Backup
   - ☁️ Upload to Cloud
   - 🧪 Verify Backup Integrity

#### 2.2 Backend API Endpoints
```python
# Location: apps/api/routers/superadmin_router.py
# ALL endpoints require 'owner' role

@router.get("/database/stats")
@require_role("owner")  # Owner-only access
async def get_database_stats()
    # Returns database size, table count, growth metrics

@router.post("/database/backup")
@require_role("owner")  # Owner-only access
@require_2fa()  # Two-factor authentication required
async def trigger_backup()
    # Triggers manual backup, returns job ID

@router.get("/database/backups")
@require_role("owner")  # Owner-only access
async def list_backups()
    # Lists all available backups (local + cloud)

@router.post("/database/restore/{backup_id}")
@require_role("owner")  # Owner-only access
@require_2fa()  # Two-factor authentication required
@require_confirmation("RESTORE")  # Must type "RESTORE" to confirm
async def restore_backup()
    # Restores database from backup (requires confirmation)

@router.post("/database/verify/{backup_id}")
@require_role("owner")  # Owner-only access
async def verify_backup()
    # Tests backup integrity without restoring

@router.delete("/database/backups/{backup_id}")
@require_role("owner")  # Owner-only access
@require_confirmation("DELETE")  # Must type "DELETE" to confirm
async def delete_backup()
    # Deletes specific backup (local or cloud)
```

#### 2.3 Celery Background Tasks
```python
# Location: apps/celery/tasks/backup_tasks.py

@celery_app.task(name="backup.create_snapshot")
async def create_backup_snapshot()
    # Creates backup, uploads to cloud, sends notification

@celery_app.task(name="backup.verify_integrity")
async def verify_backup_integrity()
    # Tests backup can be restored

@celery_app.task(name="backup.cleanup_old")
async def cleanup_old_backups()
    # Removes backups older than retention period

@celery_app.task(name="backup.sync_to_cloud")
async def sync_backup_to_cloud()
    # Uploads local backup to cloud storage
```

**Deliverables:**
- ✅ Owner dashboard database management page (owner role only)
- ✅ API endpoints with owner-role authentication
- ✅ Celery tasks for background operations
- ✅ Real-time backup progress tracking
- ✅ Email/Telegram notifications to owner

---

### Phase 3: Cloud Storage Integration (Week 3)
**Priority:** MEDIUM | **Effort:** 6 hours

#### 3.1 Cloud Provider Selection

**Option A: AWS S3** (Recommended for Production)
```
✓ Pros: Industry standard, 99.999999999% durability
✓ Cost: $0.023/GB/month = ~$0.92/month (40 GB total)
✓ Features: Versioning, lifecycle policies, encryption
✗ Cons: Requires AWS account setup
```

**Option B: Backblaze B2** (Best Cost/Performance)
```
✓ Pros: 75% cheaper than S3, S3-compatible API
✓ Cost: $0.005/GB/month = ~$0.20/month (40 GB total)
✓ Features: Free 10 GB, no egress fees for first 3x storage
✓ Integration: Drop-in replacement for S3 (boto3 compatible)
✗ Cons: Smaller company, less geographic redundancy
```

**Option C: Google Cloud Storage**
```
✓ Pros: Good integration with Google services
✓ Cost: $0.020/GB/month = ~$0.80/month (40 GB total)
✓ Features: Nearline/Coldline tiers for cheaper long-term storage
✗ Cons: Complex pricing, requires Google Cloud account
```

**Recommendation:** **Backblaze B2** for cost-effectiveness, fallback to **AWS S3** for enterprises.

#### 3.2 Implementation Components

```python
# Location: core/services/backup_cloud_service.py

class CloudBackupService:
    """Unified interface for cloud backup providers"""

    async def upload_backup(self, file_path: str) -> str:
        # Upload to configured cloud provider

    async def download_backup(self, backup_id: str) -> bytes:
        # Download backup from cloud

    async def list_backups(self) -> List[BackupMetadata]:
        # List all cloud backups

    async def delete_backup(self, backup_id: str):
        # Delete cloud backup

    async def verify_backup(self, backup_id: str) -> bool:
        # Verify backup integrity in cloud
```

**Configuration:**
```env
# .env additions
BACKUP_CLOUD_PROVIDER=backblaze  # or 'aws', 'gcs'
BACKUP_CLOUD_ENABLED=true

# Backblaze B2
BACKBLAZE_KEY_ID=your_key_id
BACKBLAZE_APPLICATION_KEY=your_app_key
BACKBLAZE_BUCKET_NAME=analyticbot-backups

# AWS S3 (alternative)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=analyticbot-backups
AWS_REGION=us-east-1

# Backup settings
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_ENABLED=true
BACKUP_ENCRYPTION_KEY=<generate-with-openssl>
```

**Deliverables:**
- ✅ Cloud storage integration service
- ✅ Backup encryption (AES-256)
- ✅ Automated cloud sync
- ✅ Download/restore from cloud
- ✅ Cost monitoring dashboard

---

### Phase 4: Point-in-Time Recovery (Week 4)
**Priority:** LOW-MEDIUM | **Effort:** 8 hours

#### 4.1 WAL Archiving Setup

**PostgreSQL Configuration:**
```sql
-- postgresql.conf additions
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /home/abcdeveloper/backups/wal_archive/%f && cp %p /home/abcdeveloper/backups/wal_archive/%f'
archive_timeout = 300  # Force WAL switch every 5 minutes
max_wal_size = 2GB
```

**Benefits:**
- 📍 Restore to exact timestamp (e.g., 5 minutes before bug)
- 🔄 Continuous backup (no data loss window)
- ⚡ Fast incremental backups (only WAL files)

**Trade-offs:**
- 💾 More disk space (WAL files ~100-500 MB/day)
- 🔧 More complex setup
- ⚠️ Requires PostgreSQL restart

**Deliverables:**
- ✅ WAL archiving configuration
- ✅ WAL cleanup script
- ✅ PITR restore script
- ✅ Documentation

---

## 📊 Monitoring & Alerting

### Metrics to Track

```python
class BackupMetrics:
    backup_size: float          # Backup file size in MB
    backup_duration: float      # Time taken for backup
    backup_success_rate: float  # % successful backups (last 30 days)
    last_backup_age: int        # Hours since last successful backup
    database_growth_rate: float # MB per day
    storage_usage: float        # % disk space used
    cloud_sync_lag: int         # Minutes delay for cloud sync
```

### Alert Rules

```yaml
alerts:
  - name: backup_failed
    condition: backup_status == "failed"
    action: email + telegram
    severity: critical

  - name: backup_overdue
    condition: last_backup_age > 28 hours
    action: email + telegram
    severity: high

  - name: disk_space_low
    condition: storage_usage > 85%
    action: email
    severity: warning

  - name: backup_size_anomaly
    condition: backup_size > 2x avg_backup_size
    action: log + email
    severity: info

  - name: cloud_sync_failed
    condition: cloud_sync_status == "failed"
    action: email
    severity: high
```

### Admin Notifications

**Email Template:**
```
Subject: ⚠️ AnalyticBot - Backup Alert

Database: analytic_bot
Status: ❌ FAILED
Time: 2025-11-26 03:00:00 UTC
Error: Connection timeout to cloud storage

Last Successful Backup: 24 hours ago
Database Size: 1.68 GB (+20 MB since last backup)

Action Required: Check backup logs and cloud connection

View Details: https://admin.analyticbot.com/database/backups
```

**Telegram Alert:**
```
🚨 Backup Failed - AnalyticBot DB

Status: ❌ Failed
Time: 03:00 UTC
Age: Last backup 24h ago

Check: /admin/database/backups
```

---

## 🔐 Security Considerations

### 1. Backup Encryption
```bash
# Encrypt backup before cloud upload
openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in backup.sql.gz \
  -out backup.sql.gz.enc \
  -pass env:BACKUP_ENCRYPTION_KEY

# Decrypt for restore
openssl enc -aes-256-cbc -d -pbkdf2 \
  -in backup.sql.gz.enc \
  -out backup.sql.gz \
  -pass env:BACKUP_ENCRYPTION_KEY
```

### 2. Access Control
```python
# Only OWNER role can:
- Trigger manual backups
- Download backups
- Restore from backups (requires 2FA)
- Delete backups (requires confirmation)
- Configure backup settings
- View all backup history
- Configure cloud storage

# All other roles (admin, moderator, user, viewer):
- NO ACCESS to database backups
- Database operations are owner-only for security
```

### 3. Audit Logging
```python
# Log all backup operations
@audit_log(action="database.backup.created")
async def create_backup():
    # Creates audit trail for compliance
```

### 4. Safe Restore Process
```python
# Restore workflow with safety checks:
1. Create pre-restore snapshot
2. Require 2FA confirmation for SuperAdmin
3. Show backup age and size
4. Test backup integrity first
5. Stop application services
6. Perform restore
7. Verify restore success
8. Restart services
9. Send completion notification
```

---

## 💰 Cost Analysis

### Storage Costs (Based on 1.66 GB database)

#### Local Storage
```
Daily backups (7 days): 1.66 GB × 7 = 11.62 GB
Cost: $0 (using existing server disk)
```

#### Cloud Storage (Backblaze B2)
```
Daily backups (30 days): 1.66 GB × 30 = 49.8 GB
Cost: 49.8 GB × $0.005 = $0.25/month
Egress: First 50 GB free
Total: ~$0.25-0.50/month
```

#### WAL Archives (Optional)
```
WAL files: ~100-200 MB/day × 7 days = ~1.4 GB
Cost: Included in above
```

### **Total Monthly Cost: $0.25 - 2.00/month** (depending on provider)

### Growth Projections
```
Current: 1.66 GB
6 months: ~2.5 GB
1 year: ~3.5 GB
2 years: ~7 GB

Estimated cost in 1 year: $1.00-4.00/month
```

---

## 🚀 Quick Start Implementation

### Minimal Setup (30 minutes)
```bash
# 1. Create backup script
./scripts/backup_database.sh

# 2. Setup cron
crontab -e
# Add: 0 3 * * * /path/to/backup_database.sh

# 3. Test backup
./scripts/backup_database.sh --test

# 4. Done! You have basic backup protection
```

### Full Setup (2-3 days)
```
Week 1: Local backups + Admin panel
Week 2: Cloud integration + Monitoring
Week 3: Testing + Documentation
Week 4: PITR (optional)
```

---

## 📝 Recommended Implementation Order

### **Priority 1: IMMEDIATE (This Week)**
1. ✅ Create local backup script
2. ✅ Setup automated cron job
3. ✅ Create restore script
4. ✅ Test backup/restore cycle

**Why:** Protects against immediate data loss risks. Takes 2-4 hours.

### **Priority 2: HIGH (Next Week)**
5. ✅ Add backup management to SuperAdmin panel (owner-only section)
6. ✅ Implement database monitoring dashboard with owner role guards
7. ✅ Setup email alerts to owner
8. ✅ Create Celery background tasks

**Why:** Gives project owner control and visibility. Takes 1-2 days.

### **Priority 3: MEDIUM (Week 3-4)**
9. ✅ Integrate cloud storage (Backblaze B2)
10. ✅ Setup encryption
11. ✅ Configure retention policies
12. ✅ Test disaster recovery

**Why:** Protects against server failure. Takes 1-2 days.

### **Priority 4: LOW (Future)**
13. ⏳ Implement PITR with WAL archiving
14. ⏳ Add multi-region cloud replication
15. ⏳ Create automated restore testing
16. ⏳ Setup backup performance optimization

**Why:** Advanced features for enterprise needs. Can wait.

---

## 🎯 Success Metrics

After full implementation, you should achieve:

```
✓ RPO (Recovery Point Objective): < 24 hours (daily backups)
✓ RTO (Recovery Time Objective): < 30 minutes (local restore)
✓ Backup Success Rate: > 99.5%
✓ Cloud Sync Success Rate: > 99%
✓ Disk Space Usage: < 70%
✓ Admin Visibility: Real-time dashboard
✓ Alert Response Time: < 5 minutes
✓ Disaster Recovery Tested: Quarterly
```

---

## 🔍 Testing & Validation

### Monthly Backup Test Checklist
```
□ Create test backup
□ Verify backup file integrity (checksum)
□ Test restore to temporary database
□ Verify restored data accuracy
□ Test cloud download/restore
□ Measure backup/restore times
□ Check disk space trends
□ Review alert functionality
□ Update documentation
```

### Quarterly Disaster Recovery Drill
```
□ Simulate server failure
□ Download backup from cloud
□ Restore on clean system
□ Verify all services work
□ Measure total recovery time
□ Document lessons learned
□ Update DR procedures
```

---

## 📚 Documentation to Create

1. **Admin User Guide** - How to use backup panel
2. **Restore Procedures** - Step-by-step restore guide
3. **Disaster Recovery Plan** - What to do if server fails
4. **Backup Troubleshooting** - Common issues and fixes
5. **Cloud Setup Guide** - Backblaze/S3 configuration

---

## 🤔 Questions to Decide

Before implementation, please decide:

### 1. Cloud Provider Choice
- [ ] **Backblaze B2** ($0.25/month) - Recommended for startups
- [ ] **AWS S3** ($1.00/month) - Recommended for enterprises
- [ ] **Google Cloud** ($0.80/month) - If using Google ecosystem
- [ ] **No cloud** (local only) - Not recommended for production

### 2. Retention Policy
- [ ] **7 days local + 30 days cloud** - Recommended
- [ ] **14 days local + 60 days cloud** - More conservative
- [ ] **30 days local + 90 days cloud** - Enterprise grade
- [ ] **Custom** (specify)

### 3. Notification Preferences
- [ ] Email only (simple)
- [ ] Email + Telegram (recommended)
- [ ] Slack integration
- [ ] Discord integration

### 4. PITR Implementation
- [ ] **Not now** - Start with daily backups only
- [ ] **Later** - Add after cloud backups working
- [ ] **Yes, include** - Need < 5 minute recovery

### 5. Budget Approval
- [ ] **$0.25-0.50/month** - Basic cloud backup
- [ ] **$1-2/month** - Premium cloud + encryption
- [ ] **$5-10/month** - Multi-region + PITR

---

## ✅ My Recommendations

Based on your setup (1.66 GB database, growing startup):

### **Start Simple, Scale Up:**
1. **Week 1:** Implement local backups (Priority 1) ← **START HERE**
2. **Week 2:** Add admin panel for visibility
3. **Week 3:** Add Backblaze B2 for cloud backup
4. **Week 4:** Test and document everything

### **Recommended Stack:**
- Local: Daily backups, 7-day retention
- Cloud: Backblaze B2, 30-day retention, encrypted
- Monitoring: Owner dashboard in SuperAdmin panel (owner role only)
- Alerts: Email + Telegram to project owner
- Cost: $0.25-0.50/month
- PITR: Skip for now, add later if needed
- Access: Owner role only (no admin/moderator/user access)

### **Why This Approach:**
✅ Low cost ($0.25/month)
✅ Quick to implement (1 week for basic protection)
✅ Scales with growth
✅ Admin-friendly interface
✅ Cloud-safe for disasters
✅ No PostgreSQL config changes needed

---

## 📞 Next Steps

**Ready to proceed?** I recommend starting with **Priority 1** (local backups):

1. I'll create `scripts/backup_database.sh` (with compression, validation, cleanup)
2. I'll create `scripts/restore_database.sh` (with safety checks)
3. I'll create `scripts/verify_backup.sh` (for testing)
4. We'll test the backup/restore cycle
5. We'll setup the cron job

**Time estimate:** 30-60 minutes to implement and test

Then we can move to Phase 2 (admin panel) and Phase 3 (cloud storage).

**What do you think? Any questions or changes to the strategy?**
