# 🚀 QUICK START - API RESTRUCTURE PHASE 0

**Architecture:** Option A - Flat Resources
**Estimated Time:** 2-3 hours
**Risk Level:** ✅ LOW (read-only analysis only)

---

## ⚡ QUICK RUN (Automated)

```bash
cd /home/abcdeveloper/projects/analyticbot

# Make sure API is running
make dev

# Run all Phase 0 steps at once
./scripts/run_phase0.sh
```

This will:
1. ✅ Analyze current API structure (361 endpoints)
2. ✅ Analyze which endpoints are actually used (from logs)
3. ✅ Find all frontend API calls
4. ✅ Create detailed migration map

**Time:** ~5-10 minutes

---

## 📋 MANUAL EXECUTION (Step by Step)

If you prefer to run steps individually:

### Step 1: Analyze Current Structure
```bash
python3 scripts/phase0_analyze_current_structure.py
```
**Output:**
- `reports/openapi_current.json`
- `reports/phase0_current_structure.txt`
- `reports/phase0_issues.txt`

### Step 2: Analyze Usage
```bash
python3 scripts/phase0_analyze_usage.py
```
**Output:**
- `reports/phase0_endpoint_usage.txt`

### Step 3: Analyze Frontend
```bash
./scripts/phase0_analyze_frontend.sh
```
**Output:**
- `reports/phase0_frontend_api_calls.txt`
- `reports/phase0_frontend_endpoints.txt`

### Step 4: Create Migration Map
```bash
python3 scripts/phase0_create_migration_map.py
```
**Output:**
- `reports/phase0_migration_map.json`
- `reports/phase0_migration_map.txt`

---

## 📊 REVIEW REPORTS

### Most Important Reports:

1. **Migration Map** (what will change):
   ```bash
   cat reports/phase0_migration_map.txt
   ```

2. **Detected Issues**:
   ```bash
   cat reports/phase0_issues.txt
   ```

3. **Top 20 Most-Used Endpoints**:
   ```bash
   head -30 reports/phase0_endpoint_usage.txt
   ```

4. **Current Structure Overview**:
   ```bash
   head -50 reports/phase0_current_structure.txt
   ```

---

## 🎯 WHAT TO LOOK FOR

### ✅ Good Signs:
- Most-used endpoints are in "KEEP" category
- Few endpoints in "REVIEW" category
- Clear migration path for all endpoints

### ⚠️ Red Flags:
- Critical endpoints in "DEPRECATE" category
- Many endpoints in "REVIEW" category
- Frontend using endpoints we plan to remove

---

## 🛡️ STEP 5: SAFETY SETUP

After reviewing reports, create safety backups:

```bash
cd /home/abcdeveloper/projects/analyticbot

# Create backup branch
git checkout -b backup-before-api-restructure-$(date +%Y%m%d)
git add .
git commit -m "Backup before API restructure - Phase 0 complete"
git push origin backup-before-api-restructure-$(date +%Y%m%d)

# Create feature branch for Phase 1
git checkout main
git checkout -b feature/api-restructure-phase1

echo "✅ Safety branches created!"
```

---

## ✅ PHASE 0 CHECKLIST

- [ ] API server is running (`make dev`)
- [ ] Ran `./scripts/run_phase0.sh` successfully
- [ ] Reviewed `reports/phase0_migration_map.txt`
- [ ] Checked `reports/phase0_issues.txt`
- [ ] Verified top 20 endpoints won't break
- [ ] Reviewed frontend API calls
- [ ] Created backup branch
- [ ] Created feature branch for Phase 1
- [ ] Team reviewed and approved migration plan

---

## 📈 EXPECTED RESULTS

**Before (Current):**
- 361 endpoints
- 29 prefix groups
- Multiple duplicates
- Nested redundancy
- Inconsistent structure

**After Phase 0 Analysis:**
- Complete endpoint inventory
- Usage statistics
- Frontend dependency map
- Detailed migration plan
- Safety backups created

---

## 🚦 NEXT PHASE

Once Phase 0 is complete and reviewed:

**Phase 1: Remove Duplicates** (Week 1)
- Add redirect middleware
- Test redirects work
- Monitor for errors
- No deletion yet!

**Document:** `docs/API_RESTRUCTURE_PHASE_1_DUPLICATES.md` (will be created)

---

## ❓ TROUBLESHOOTING

### API server not running:
```bash
make dev
# Wait 10 seconds for server to start
curl http://localhost:11400/health/
```

### Reports directory missing:
```bash
mkdir -p reports
```

### Script permissions:
```bash
chmod +x scripts/*.sh
```

### No log files:
```bash
# Generate some traffic first
curl http://localhost:11400/health/
curl http://localhost:11400/channels/
# Then run Step 2 again
```

---

## 📞 SUPPORT

**Documentation:**
- Full Plan: `docs/API_ENDPOINT_CHAOS_AUDIT_AND_CLEANUP_PLAN.md`
- Phase 0: `docs/API_RESTRUCTURE_PHASE_0_PREPARATION.md`

**Questions Before Phase 1:**
1. Are all critical endpoints safe?
2. Do we need to notify external API consumers?
3. What's the rollback plan?
4. When is the best deployment time?

---

**Status:** Ready to execute
**Next:** Run `./scripts/run_phase0.sh` and review reports
