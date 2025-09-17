# 📋 DATABASE MIGRATION QUICK REFERENCE GUIDE

**Date**: September 17, 2025  
**Purpose**: Quick reference for safe database migrations and deployments

---

## 🚀 QUICK START COMMANDS

### **Immediate Production Deployment**
```bash
# Run complete safe migration with all safety checks
./scripts/safe_database_migration.sh deploy

# Check if system is ready for migration
./scripts/safe_database_migration.sh checks

# Validate existing migration state
./scripts/safe_database_migration.sh validate
```

### **Emergency Procedures**
```bash
# Emergency rollback to last backup
./scripts/safe_database_migration.sh rollback

# Check current database status
alembic current
alembic history --verbose
```

---

## 🛡️ SAFETY CHECKLIST

### **Before Every Production Migration**
```bash
☐ Run: ./scripts/safe_database_migration.sh checks
☐ Verify: All 8 safety checks pass
☐ Confirm: Recent backup exists (< 24h old)
☐ Check: No long-running transactions
☐ Ensure: Sufficient disk space (> 20% free)
☐ Validate: Migration files syntax is correct
☐ Alert: Team about upcoming deployment
☐ Schedule: Maintenance window (if needed)
```

### **During Migration**
```bash
☐ Monitor: Migration execution logs
☐ Watch: Database performance metrics
☐ Track: Application health status
☐ Prepare: Rollback procedure if needed
☐ Document: Any unexpected issues
```

### **After Migration**
```bash
☐ Validate: All post-migration checks pass
☐ Test: Critical user workflows
☐ Verify: Payment processing works
☐ Check: User authentication functions
☐ Monitor: System for 24 hours
☐ Notify: Team of successful completion
```

---

## 📊 KEY SYSTEM FILES

### **Migration System**
```
infra/db/alembic/versions/    # Migration files (0001-0016)
scripts/safe_database_migration.sh  # Main deployment script
config/production_deployment_pipeline.yml  # Pipeline config
COMPREHENSIVE_DATABASE_MIGRATION_STRATEGY_AUDIT.md  # Full strategy
```

### **Current Migration Status**
```
Total Migrations: 16 files
Latest Migration: 0016_critical_fix_cascade_delete_constraints
Chain Status: ✅ Clean linear sequence
Data Protection: ✅ CASCADE DELETE → RESTRICT fixes applied
```

---

## 🔄 COMMON SCENARIOS

### **Scenario 1: Regular Feature Migration**
```bash
# 1. Create new migration
alembic revision -m "add_new_feature"

# 2. Edit migration file with changes
# (edit infra/db/alembic/versions/00XX_add_new_feature.py)

# 3. Test on development
alembic upgrade head

# 4. Deploy to production safely
./scripts/safe_database_migration.sh deploy
```

### **Scenario 2: Emergency Rollback**
```bash
# If migration fails or causes issues
./scripts/safe_database_migration.sh rollback

# Or manual Alembic rollback
alembic downgrade -1  # Go back one migration
alembic downgrade 0015  # Go to specific revision
```

### **Scenario 3: Data Migration**
```bash
# For large data transformations
# 1. Add migration_status column
# 2. Deploy application with dual-mode support
# 3. Run background data migration job
# 4. Switch to new data format
# 5. Remove old columns in next release
```

---

## ⚠️ CRITICAL WARNINGS

### **NEVER DO THESE IN PRODUCTION**
```sql
❌ ALTER TABLE users DROP COLUMN email;  -- Data loss!
❌ DROP TABLE payments;  -- Data loss!
❌ DELETE FROM users WHERE ...;  -- Potential data loss!
❌ ALTER TABLE large_table ADD COLUMN ...;  -- Without CONCURRENTLY
❌ CREATE INDEX idx_name ON large_table(col);  -- Blocks writes
```

### **ALWAYS DO THESE INSTEAD**
```sql
✅ ALTER TABLE users ADD COLUMN email_new VARCHAR(255);  -- Safe addition
✅ CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name ON table(col);  -- Non-blocking
✅ Use background jobs for large data migrations
✅ Test migrations on staging with production data copy first
✅ Keep rollback window open for 24 hours
```

---

## 📞 EMERGENCY CONTACTS

### **If Migration Fails**
1. **DON'T PANIC** - rollback procedures are automated
2. Run: `./scripts/safe_database_migration.sh rollback`
3. Check logs in: `/var/log/analyticbot-migration-*.log`
4. Notify team via configured channels
5. Investigate root cause before retry

### **If Data Loss Suspected**
1. **IMMEDIATELY** stop all write operations
2. Run: `./scripts/safe_database_migration.sh rollback`
3. Validate user data integrity
4. Check backup files in: `backups/migration-*/`
5. Contact database administrator

---

## 🎯 SUCCESS METRICS

### **Migration Success Indicators**
```
✅ Zero data loss (user count unchanged)
✅ All foreign key relationships intact
✅ Migration execution time < 30 minutes
✅ Application health check passes
✅ User authentication works
✅ Payment processing functional
✅ No constraint violations
```

### **Rollback Triggers**
```
🚨 Migration execution time > 60 minutes
🚨 Any data loss detected
🚨 Application health failure rate > 50%
🚨 Database performance degradation > 30%
🚨 User authentication failure rate > 5%
```

---

## 🔧 TROUBLESHOOTING

### **Common Issues & Solutions**

#### **Issue: "Migration timeout"**
```bash
# Solution: Check for blocking queries
SELECT * FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';

# Kill blocking queries if safe
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ...;
```

#### **Issue: "Disk space insufficient"**
```bash
# Solution: Free up space
docker system prune -f  # Remove unused Docker resources
du -sh /var/lib/postgresql/data/*  # Check database size
```

#### **Issue: "Backup validation failed"**
```bash
# Solution: Create new backup
pg_dump -h postgres -U analytic -d analytic_bot > manual_backup.sql
pg_restore --list backup.dump  # Validate backup file
```

---

## 📈 MONITORING COMMANDS

### **Real-time Monitoring During Migration**
```bash
# Database performance
watch "psql -c 'SELECT * FROM pg_stat_activity;'"

# Application health
watch "curl -s http://localhost:8000/health"

# Disk usage
watch "df -h /var/lib/postgresql/data"

# Migration progress (if visible)
tail -f /var/log/analyticbot-migration*.log
```

---

## 💡 BEST PRACTICES REMINDER

### **Development Best Practices**
- Always test migrations on staging first
- Use descriptive migration names
- Include both upgrade AND downgrade procedures
- Add comments explaining complex migrations
- Keep migrations small and focused

### **Production Best Practices**
- Schedule migrations during low-traffic periods
- Always create backup before migration
- Monitor system for 24 hours after migration
- Keep rollback option available for 24 hours
- Document any issues for future reference

---

## 🎉 CONGRATULATIONS!

Your database migration system is now **PRODUCTION READY** with:

✅ **Zero Data Loss Protection**  
✅ **Automated Safety Checks**  
✅ **One-Command Deployment**  
✅ **Emergency Rollback Capability**  
✅ **Comprehensive Monitoring**  

**Ready to deploy safely!** 🚀