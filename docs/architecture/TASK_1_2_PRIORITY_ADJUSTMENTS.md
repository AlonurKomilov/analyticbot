# Task 1.2 Priority Adjustment - Your Choices

**Date:** October 19, 2025  
**Status:** Awaiting Your Input  

---

## 🎯 Current Priority Assignments

Below are the current priorities for all 63 markers. Review and adjust as needed.

---

## PHASE 1: Automated Quick Fixes (15 markers)

### Auto-Fix Group 1: Simple Default Values
**Current Priority:** HIGH (Implement Now)  
**Estimated Time:** 10 minutes  
**Your Decision:** Keep / Defer / Skip

**Affected Files:**
1. `apps/bot/handlers/exports.py:168-169` - channel_id and period defaults
2. `apps/jobs/services/analytics_job_service.py:40` - timestamp default
3. `apps/jobs/services/delivery_job_service.py:41` - delivery_time default

**Proposed Changes:**
- Add proper default values from config/settings
- Remove placeholder TODOs
- Improve code reliability

**YOUR CHOICE:**
- [ ] A) Keep - Implement all 3 (10 min)
- [ ] B) Partial - Only exports.py (5 min)
- [ ] C) Skip - Create issues instead

**Decision:** _________

---

### Auto-Fix Group 2: Obsolete Comments
**Current Priority:** HIGH (Delete Now)  
**Estimated Time:** 5 minutes  
**Your Decision:** Keep / Defer / Skip

**Affected Files:**
1. `apps/api/main.py:25` - "DEPRECATED ROUTERS REMOVED" (already done)
2. `apps/bot/services/adapters/ml_coordinator.py:4` - Backward compatibility note
3. `apps/bot/handlers/content_protection.py:5-7` - Legacy code note

**Proposed Changes:**
- Delete obsolete comments
- Update remaining to reference docs
- Clean up noise

**YOUR CHOICE:**
- [ ] A) Delete all 3 obsolete comments (5 min)
- [ ] B) Keep content_protection note as warning (delete 2)
- [ ] C) Update all to reference specific docs

**Decision:** _________

---

### Auto-Fix Group 3: Better Comments
**Current Priority:** HIGH (Update Now)  
**Estimated Time:** 10 minutes  
**Your Decision:** Keep / Defer / Skip

**Affected Files:**
1. `apps/api/routers/superadmin_router.py:227` - Session invalidation
2. `apps/api/routers/system_router.py:123` - Service injection
3. `apps/api/services/database_error_handler.py:100` - Monitoring system
4. `apps/api/deps_factory.py:22` - DI container resolution

**Proposed Changes:**
- Replace vague TODOs with clear action items
- Add issue references or timelines
- Improve developer context

**YOUR CHOICE:**
- [ ] A) Update all 4 (10 min)
- [ ] B) Update only router TODOs (5 min)
- [ ] C) Skip - will be addressed in Phase 2 issues

**Decision:** _________

---

### Auto-Fix Group 4: Remove DEPRECATED Functions
**Current Priority:** HIGH (Delete Now)  
**Estimated Time:** 15 minutes  
**Your Decision:** Keep / Defer / Skip

**Affected Files:**
1. `apps/di/bot_container.py:209-220` - get_scheduler_service() (~12 lines)
2. `apps/di/bot_container.py:374-385` - get_alerting_service() (~12 lines)
3. `apps/api/middleware/auth.py:438` - Legacy role comment

**Proposed Changes:**
- Delete deprecated scheduler service function
- Delete deprecated alerting service function
- Update auth middleware comment

**Impact Check:**
- Scheduler: grep shows 1 usage in middleware (line 118)
- Alerting: No direct usages found
- Auth roles: Comment only, no code impact

**YOUR CHOICE:**
- [ ] A) Delete both functions + update comment (15 min)
- [ ] B) Keep scheduler (1 usage), delete alerting only (10 min)
- [ ] C) Update middleware first, then delete in Week 2

**Decision:** _________

**⚠️ IMPORTANT NOTE:**
If you choose A or B, we'll need to update the middleware that uses scheduler_service first!

---

## PHASE 2: GitHub Issues (20 markers)

### High Priority Issues (Week 2)
**Current Assignment:** 5 issues  
**Your Decision:** Adjust priorities / Keep / Add more

1. **ContentAnalyzer service implementation**
   - Current: HIGH (Week 2)
   - Effort: 4 hours
   - Your Priority: HIGH / MEDIUM / LOW / CRITICAL
   - Your Week: Week 1 / Week 2 / Week 3 / Future

2. **Repository protocols for subscription service**
   - Current: HIGH (Week 2)
   - Effort: 2 hours
   - Your Priority: HIGH / MEDIUM / LOW / CRITICAL
   - Your Week: Week 1 / Week 2 / Week 3 / Future

3. **Chart service DI provider** (affects 4 locations)
   - Current: HIGH (Week 2)
   - Effort: 3 hours
   - Your Priority: HIGH / MEDIUM / LOW / CRITICAL
   - Your Week: Week 1 / Week 2 / Week 3 / Future

4. **Channel admin verification via Telegram API**
   - Current: HIGH (Week 2)
   - Effort: 2 hours
   - Your Priority: HIGH / MEDIUM / LOW / CRITICAL
   - Your Week: Week 1 / Week 2 / Week 3 / Future

5. **AlertSentRepository implementation**
   - Current: HIGH (Week 2)
   - Effort: 2 hours
   - Your Priority: HIGH / MEDIUM / LOW / CRITICAL
   - Your Week: Week 1 / Week 2 / Week 3 / Future

**YOUR ADJUSTMENTS:**
- Promote any MEDIUM to HIGH? _________
- Demote any HIGH to MEDIUM? _________
- Add any to CRITICAL (Week 1)? _________

---

### Medium Priority Issues (Week 3)
**Current Assignment:** 8 issues  
**Your Decision:** Adjust priorities / Keep

6. AI security analysis service (6h)
7. Payment system integration (4h)
8. Content protection database ops (3h)
9. ML predictions to Celery (2h)
10. Analytics channels query (1h)
11. Password reset email (2h)
12. Alert details from repository (1h)
13. Channel management core service (3h)

**YOUR ADJUSTMENTS:**
- Promote to HIGH (Week 2)? _________
- Demote to LOW? _________
- Which is MOST important? _________

---

### Low Priority Issues (Future)
**Current Assignment:** 7 issues

14. PredictiveOrchestratorService refactor (8h)
15. Churn prediction core services (6h)
16. Bot alert sending integration (3h)
17. remove_expired clean architecture (2h)
18. claim_due_posts clean architecture (2h)
19. Post queue management (3h)
20. Premium features consolidation (4h)

**YOUR ADJUSTMENTS:**
- Promote any to MEDIUM? _________
- Remove any (won't fix)? _________

---

## PHASE 3: Documentation (10 markers)

### Known Limitations to Document
**Current Plan:** Document all 10 categories  
**Your Decision:** Keep all / Prioritize some / Skip any

**Categories:**
1. Repository Protocols (Missing implementations)
2. DI Container Coverage (Chart service)
3. Middleware Dependencies (Repository injection)
4. Legacy Services (Scheduler/Alerting references)
5. Subscription System (Mock adapter)
6. Premium Features (Location/organization)
7. Analytics Services (Core service integration)
8. Database Lookups (Placeholder implementations)
9. Auth Router Operations (Mock responses)
10. Monitoring Integration (Sentry/DataDog)

**YOUR CHOICE:**
- [ ] A) Document all 10 (20 min, comprehensive)
- [ ] B) Top 5 only (10 min, focused on HIGH impact)
- [ ] C) Separate doc per category (longer, more detailed)

**If B, which 5?** _________

---

## PHASE 4: Manual Review (13 decision points)

### Review These During Execution

These will be presented during Phase 4. You can pre-decide now or wait:

**Pre-Decisions (Optional):**

1. Legacy scheduler service reference → **Remove now / Week 2 / Keep**
2. Content protection legacy note → **Delete / Update / Keep**
3. Repository injection middleware → **Implement / Issue / Document**
4. Initial data service protocols → **Implement / Issue / Document**
5. Database delivery repository → **Implement / Issue / Keep as-is**
6. ML Coordinator module → **Delete / Keep / Sunset date**
7. Subscription service → **Week 1 / Week 2 / Week 3**
8. Premium emoji implementation → **Implement / Issue / Remove TODO**
9. Auth router TODOs → **Week 1 / Week 2 / Split**
10. Payment integration → **Week 2 / Week 3 / Future**
11. Bot tasks refactor → **Now / Issues / Document**
12. Job service stubs → **Implement / Issue / Keep**
13. Legacy role dependencies → **Remove / Migrate / Keep**

**YOUR PRE-DECISIONS (if any):**
_________________________________________
_________________________________________

---

## PHASE 5: Strategic TODOs (5 markers)

### Keep These with Better Formatting
**Current Plan:** Format 5 strategic TODOs  
**Your Decision:** Keep / Remove any / Add others

**Planned to Keep:**
1. Premium features consolidation (part of larger refactor)
2. Phase 3.5 improvements (documented roadmap)
3. Service implementations waiting on dependencies
4. Architecture improvements (strategic)
5. Future enhancements (valuable context)

**YOUR ADJUSTMENTS:**
- Remove any from "keep" list? _________
- Add any to "keep" list? _________
- Change formatting approach? _________

---

## ⚡ SPECIAL ADJUSTMENTS

### Do You Want To:

**Add Emergency Fixes (not in plan)?**
- [ ] Yes - Please list: _________
- [ ] No - Current plan is fine

**Skip Entire Phases?**
- [ ] Skip Phase 1 (go straight to issues)
- [ ] Skip Phase 2 (no GitHub issues, just document)
- [ ] Skip Phase 3 (no documentation)
- [ ] Skip Phase 4 (auto-decide everything)
- [ ] Skip Phase 5 (remove all remaining TODOs)

**Change Overall Approach?**
- [ ] More aggressive (remove everything, less documentation)
- [ ] More conservative (document more, remove less)
- [ ] Balanced (keep current plan)

---

## 🎯 PRIORITY SCORING SYSTEM

To help you decide, here's how I evaluated priorities:

**CRITICAL (Week 1):**
- Blocking other work
- Security-related
- High user impact
- Quick wins (<2 hours)

**HIGH (Week 2):**
- Important but not blocking
- Medium impact
- Reasonable effort (2-4 hours)
- Clear requirements

**MEDIUM (Week 3):**
- Nice to have
- Lower impact
- More effort (4-6 hours)
- Some uncertainties

**LOW (Future):**
- Enhancement
- Low impact
- High effort (6+ hours)
- Needs more planning

---

## 📝 YOUR FINAL ADJUSTMENTS

**Summary of Changes:**
1. Phase 1 adjustments: _________
2. Phase 2 priority changes: _________
3. Phase 3 scope: _________
4. Phase 4 pre-decisions: _________
5. Phase 5 adjustments: _________
6. Overall approach: _________

**Estimated Time Impact:**
- Original: 1.5 hours
- With your changes: _________ hours

**Ready to Proceed?**
- [ ] Yes, start Phase 1 with adjustments
- [ ] No, need more discussion
- [ ] Yes, but skip _________ phase(s)

---

## 🚀 QUICK RECOMMENDATIONS

Based on the comprehensive audit, here are my suggestions:

**HIGH PRIORITY (Do Now):**
1. ✅ Delete deprecated functions (clean up DI container)
2. ✅ Fix simple default values (quick wins)
3. ✅ Create GitHub issues (organize work)
4. ✅ Document known limitations (clarity)

**MEDIUM PRIORITY (Week 2):**
1. 🟡 Subscription service (HIGH impact but needs payment system)
2. 🟡 Chart service DI (affects multiple locations)
3. 🟡 Repository protocols (clean architecture completion)

**LOW PRIORITY (Week 3+):**
1. 🔵 Premium features organization (refactor, not critical)
2. 🔵 ML service refactors (working, just not ideal)
3. 🔵 Job service improvements (nice to have)

**AGREE?** _________

---

**Save your adjustments above, then say "Start with my adjustments" to begin!**

**Or say "Start with defaults" to use the plan as-is.**
