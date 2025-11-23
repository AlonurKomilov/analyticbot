# Phase 4 Rollback Procedures

## Quick Reference Guide for Operations Team

**Last Updated:** November 21, 2025
**Phase:** 4 - Production Deployment
**Feature:** Recommendation System Enhancements

---

## 🚨 Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| Lead Developer | TBD | 24/7 |
| DevOps | TBD | Business hours |
| DBA | TBD | On-call |

---

## ⚡ Quick Rollback (< 1 minute)

### Scenario: Advanced features causing errors or performance issues

**Immediate Action - Disable all advanced features:**

```bash
# 1. SSH into production server
ssh user@production-server

# 2. Edit environment file
nano /path/to/.env.production

# 3. Change this line:
ENABLE_ADVANCED_RECOMMENDATIONS=false

# 4. Restart API
systemctl restart analyticbot-api
# OR
docker-compose restart api
# OR
./scripts/dev-start.sh stop && ./scripts/dev-start.sh all

# 5. Verify health
curl http://localhost:10300/health

# 6. Test recommendations
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:10300/analytics/predictive/best-times/CHANNEL_ID?days=90
```

**Expected Result:** System reverts to legacy behavior immediately. No advanced fields in response.

**Rollback Time:** < 60 seconds
**Data Loss:** None
**Reversible:** Yes (re-enable flags)

---

## 🎚️ Partial Rollback (< 2 minutes)

### Scenario A: Time-weighting causing issues

**Disable only time-weighting, keep content-type detection:**

```bash
# Edit .env.production
ENABLE_ADVANCED_RECOMMENDATIONS=true
ENABLE_TIME_WEIGHTING=false          # ← Disable this
ENABLE_CONTENT_TYPE_ANALYSIS=true

# Restart
systemctl restart analyticbot-api

# Verify
tail -f /var/log/analyticbot/production.log | grep "Feature flags"
# Should show: "Time-weighting: False"
```

### Scenario B: Content-type detection causing issues

**Disable only content-type analysis, keep time-weighting:**

```bash
# Edit .env.production
ENABLE_ADVANCED_RECOMMENDATIONS=true
ENABLE_TIME_WEIGHTING=true
ENABLE_CONTENT_TYPE_ANALYSIS=false   # ← Disable this

# Restart
systemctl restart analyticbot-api
```

---

## 🔄 Full Code Rollback (< 10 minutes)

### Scenario: Code bugs requiring revert

**Step 1: Identify commit to revert**

```bash
cd /path/to/analyticbot
git log --oneline | head -10

# Find Phase 4 commit (example):
# abc1234 Phase 4: Production deployment with feature flags
```

**Step 2: Revert code**

```bash
# Create revert commit
git revert abc1234

# Or reset to previous commit (destructive)
git reset --hard HEAD~1
```

**Step 3: Rebuild and redeploy**

```bash
# Rebuild Docker images
docker-compose build

# Restart services
docker-compose up -d

# Verify
curl http://localhost:10300/health
```

**Step 4: Database rollback (if needed)**

```bash
# Connect to database
psql postgresql://user:pass@localhost:10100/analytic_bot

# Run rollback script
\i /path/to/infra/db/migrations/004_rollback.sql

# Verify columns removed
\d posts
# Should NOT see has_video, has_media columns
```

**Rollback Time:** 5-10 minutes
**Data Loss:** Content-type detection data (has_video, has_media)
**Reversible:** Must re-run migration 004 and backfill data

---

## 📊 Validation After Rollback

### 1. Health Check

```bash
curl http://localhost:10300/health | jq '.'

# Expected:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-21T...",
#   "service": "analyticbot",
#   "version": "7.5.0"
# }
```

### 2. Feature Flag Status

```bash
tail -50 /var/log/analyticbot/production.log | grep "Feature flags"

# Expected (if disabled):
# [INFO] Feature flags - Advanced: False, Time-weighting: False, Content-type: False
# [INFO] Using SIMPLE query (legacy mode)
```

### 3. Test Recommendations

```bash
# Get auth token
TOKEN=$(curl -s -X POST "http://localhost:10300/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}' \
  | jq -r '.access_token')

# Test endpoint
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:10300/analytics/predictive/best-times/CHANNEL_ID?days=90" \
  | jq '{
    total_posts: .data.total_posts_analyzed,
    has_advanced: (.data.best_day_hour_combinations != null)
  }'

# Expected (if rolled back):
# {
#   "total_posts": 629,
#   "has_advanced": false     ← Should be false after rollback
# }
```

### 4. Error Rate Check

```bash
# Check for errors in last 100 lines
tail -100 /var/log/analyticbot/production.log | grep ERROR | wc -l

# Expected: 0
```

### 5. Response Time Check

```bash
# Measure response time
time curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:10300/analytics/predictive/best-times/CHANNEL_ID?days=90" \
  > /dev/null

# Expected: < 2 seconds (legacy mode faster)
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Environment changes not taking effect

**Problem:** Changed flags but API still using old values

**Solution:**
```bash
# Ensure environment file is correct
cat .env.production | grep ENABLE_ADVANCED

# Force reload environment
systemctl daemon-reload
systemctl restart analyticbot-api

# Verify process has new environment
ps aux | grep uvicorn
sudo cat /proc/$(pgrep -f uvicorn)/environ | tr '\0' '\n' | grep ENABLE_
```

### Issue 2: API won't start after rollback

**Problem:** API crashes on startup

**Solution:**
```bash
# Check logs
journalctl -u analyticbot-api -n 50

# Common causes:
# 1. Syntax error in .env
#    Fix: Validate .env syntax
# 2. Missing dependency
#    Fix: pip install -r requirements.txt
# 3. Database connection error
#    Fix: Check DATABASE_URL
```

### Issue 3: Database rollback fails

**Problem:** Migration rollback script errors

**Solution:**
```bash
# Check if columns exist
psql $DATABASE_URL -c "\d posts" | grep has_video

# If columns don't exist, skip rollback
# If columns exist but script fails, manual rollback:
psql $DATABASE_URL <<EOF
DROP INDEX IF EXISTS idx_posts_content_type;
DROP INDEX IF EXISTS idx_posts_date_content;
ALTER TABLE posts DROP COLUMN IF EXISTS has_video;
ALTER TABLE posts DROP COLUMN IF EXISTS has_media;
EOF
```

### Issue 4: Partial rollback - only one flag changed

**Problem:** Disabled ENABLE_TIME_WEIGHTING but still seeing time-weighted results

**Solution:**
```bash
# Verify all three flags are correctly set
cat .env.production | grep ENABLE_

# If master flag is true but sub-flag is false, system should respect it
# Check logs to confirm:
tail -f /var/log/analyticbot/production.log | grep "Time-weighting"

# Should see: "Time-weighting: False"

# If still showing True, API may be caching environment
pkill -9 -f uvicorn
systemctl start analyticbot-api
```

---

## 📝 Rollback Decision Matrix

| Symptom | Severity | Action | Timeline |
|---------|----------|--------|----------|
| Response time > 5s | HIGH | Quick rollback (disable all) | < 1 min |
| Error rate > 5% | HIGH | Quick rollback (disable all) | < 1 min |
| Memory usage > 2GB | MEDIUM | Partial rollback (disable time-weighting) | < 2 min |
| Incorrect recommendations | MEDIUM | Investigate, consider partial rollback | < 5 min |
| Missing data in response | LOW | Check feature flag settings | < 5 min |
| Code bugs | HIGH | Full code rollback | < 10 min |

---

## 📞 Escalation Path

1. **Level 1:** Ops team attempts quick rollback (disable flags)
2. **Level 2:** Contact on-call developer if rollback doesn't resolve
3. **Level 3:** DBA involved if database issues persist
4. **Level 4:** Full team escalation for code rollback

---

## ✅ Post-Rollback Checklist

- [ ] Health endpoint responding (200 OK)
- [ ] Feature flags confirmed disabled in logs
- [ ] No errors in last 100 log lines
- [ ] Response times < 2 seconds
- [ ] Test recommendations returning data
- [ ] Monitoring dashboards showing normal metrics
- [ ] Alert channels notified of rollback
- [ ] Incident report created (if applicable)
- [ ] Root cause analysis scheduled

---

## 🔐 Rollback Authorization

| Environment | Authorization Required | Approver |
|-------------|------------------------|----------|
| Staging | None (self-service) | Any developer |
| Production | Approval required | Team lead or on-call |

**Note:** In emergency situations (P0/P1), on-call engineer can execute production rollback immediately and notify afterward.

---

## 📚 Related Documentation

- [Phase 3 Completion Report](./phase3_completion_report.md)
- [Feature Flags Configuration](../config/feature_flags.md)
- [Deployment Checklist](./deployment_checklist_phase4.md)
- [Migration 004 Rollback Script](../infra/db/migrations/004_rollback.sql)

---

## 🔄 Rollback History

| Date | Environment | Reason | Duration | Outcome |
|------|-------------|--------|----------|---------|
| TBD | - | - | - | - |

*(Update this table after each rollback)*

---

**Document Version:** 1.0
**Last Review:** November 21, 2025
**Next Review:** December 21, 2025
