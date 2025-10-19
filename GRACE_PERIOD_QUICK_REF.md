# 🗓️ QUICK REFERENCE: Grace Period Deletions

## October 21, 2025 (Monday) - IN 2 DAYS ⏰

### Files to Delete (723 lines total):
```bash
cd /home/abcdeveloper/projects/analyticbot
rm -v apps/bot/di.py apps/api/deps.py
```

### Quick Verification:
```bash
# Check for new usages (should find 0)
grep -r "from apps.bot.di import" apps/ --exclude-dir=archive
grep -r "from apps.api.deps import" apps/ --exclude-dir=archive
```

### Quick Commit:
```bash
git add -A
git commit -m "refactor(di): Remove deprecated DI files after Oct 21 grace period

- Deleted apps/bot/di.py (470 lines)
- Deleted apps/api/deps.py (253 lines)
- All usages migrated to unified apps/di/ system
- 723 lines of deprecated code removed"
```

---

## October 26, 2025 (Saturday) - IN 7 DAYS ⏰

### File to Delete (56 lines):
```bash
cd /home/abcdeveloper/projects/analyticbot
rm -v apps/api/di.py
```

### Quick Verification:
```bash
grep -r "from apps.api.di import" apps/ --exclude-dir=archive
```

### Quick Commit:
```bash
git add -A
git commit -m "refactor(di): Remove final deprecated DI file after Oct 26 grace period

- Deleted apps/api/di.py (56 lines)
- Phase 2C cleanup: 73% complete
- DI migration fully complete"
```

---

## 📊 Expected Impact

| Metric | Before | After Oct 21 | After Oct 26 |
|--------|--------|--------------|--------------|
| Deprecated DI files | 3 | 1 | 0 |
| Deprecated lines | 779 | 56 | 0 |
| Cleanup progress | 14% | 69% | 73% |
| DI systems | 1 (unified) | 1 | 1 |

---

## ✅ 30-Second Checklist

### Oct 21:
- [ ] Run verification greps (expect 0 results)
- [ ] Delete both files
- [ ] Run `python3 -m py_compile apps/di/*.py`
- [ ] Commit with provided message
- [ ] Update APPS_ARCHITECTURE_TOP_10_ISSUES.md

### Oct 26:
- [ ] Run verification grep (expect 0 results)
- [ ] Delete file
- [ ] Run syntax check
- [ ] Commit with provided message
- [ ] Create PHASE_2_COMPLETE.md

---

**📋 Full Details:** See GRACE_PERIOD_DELETION_PLAN.md

**⚠️ If Issues:** Run `git checkout HEAD -- apps/bot/di.py apps/api/deps.py apps/api/di.py` to restore
