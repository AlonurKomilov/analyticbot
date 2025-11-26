# GitHub Issues for TODO Cleanup - October 19, 2025

**Generated from Task 1.2 Phase 2: TODO Marker Cleanup**

This document contains 18 GitHub issues to track and replace remaining TODO markers in the codebase.
All issues are tagged with `technical-debt` and `enhancement` labels.

---

## 🔴 HIGH PRIORITY - Week 2 (5 issues)

### Issue #1: Implement Chart Service DI Provider
**Priority:** HIGH
**Milestone:** Week 2
**Effort:** 3 hours
**Label:** `technical-debt`, `enhancement`, `di-system`

**Current State:**
Chart service is currently instantiated via factory functions in 4 locations, bypassing the DI container.

**Locations:**
- `apps/bot/handlers/admin_handlers.py:36`
- `apps/bot/handlers/exports.py:59`
- `apps/api/routers/exports_router.py:49`
- `apps/api/routers/sharing_router.py:79`

**Proposed Solution:**
1. Create `ChartServiceProvider` in `apps/di/providers/`
2. Register in `core_services_container.py`
3. Update all 4 locations to use DI injection
4. Remove factory functions

**Dependencies:**
- Chart service refactoring (if needed)
- DI container access in all affected modules

**Acceptance Criteria:**
- [ ] Chart service provider implemented
- [ ] All 4 locations use DI injection
- [ ] Factory functions removed
- [ ] Tests pass
- [ ] Import linter passes

---

### Issue #2: Implement Session Invalidation for Admin Logout
**Priority:** HIGH
**Milestone:** Week 2
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `security`

**Current State:**
Admin logout endpoint exists but doesn't actually invalidate sessions. Relies only on JWT expiration (stateless).

**Location:**
- `apps/api/routers/superadmin_router.py:224`

**Proposed Solution:**
1. Implement session blacklist/invalidation mechanism
2. Options:
   - Redis-based token blacklist
   - Database session tracking
   - JWT revocation list
3. Add session cleanup job
4. Update logout endpoint

**Dependencies:**
- Redis cache (preferred) or database
- Session storage strategy decision

**Acceptance Criteria:**
- [ ] Session invalidation mechanism implemented
- [ ] Logout endpoint invalidates sessions
- [ ] Tests for session invalidation
- [ ] Cleanup job for expired sessions
- [ ] Documentation updated

---

### Issue #3: Connect Job Services to Core Analytics Pipeline
**Priority:** HIGH
**Milestone:** Week 2
**Effort:** 4 hours
**Label:** `technical-debt`, `enhancement`, `analytics`

**Current State:**
Analytics and delivery job services contain only simulated processing. Not connected to actual core services.

**Locations:**
- `apps/jobs/services/analytics_job_service.py:33`
- `apps/jobs/services/delivery_job_service.py:33`

**Proposed Solution:**
1. Inject core analytics services via DI
2. Replace simulated processing with actual service calls
3. Add error handling and retry logic
4. Update job service tests

**Dependencies:**
- Core analytics services must be defined
- Core delivery services must be available
- DI container integration

**Acceptance Criteria:**
- [ ] Job services integrated with core services
- [ ] Actual processing replaces simulation
- [ ] Error handling implemented
- [ ] Tests updated with real service mocks
- [ ] Performance acceptable for background jobs

---

### Issue #4: Implement ContentAnalyzer Service
**Priority:** HIGH
**Milestone:** Week 2
**Effort:** 4 hours
**Label:** `technical-debt`, `enhancement`, `ml-services`

**Current State:**
ContentAnalyzer is referenced but not implemented. ML tasks have placeholder for this service.

**Location:**
- `apps/celery/tasks/ml_tasks.py` (referenced in comments)

**Proposed Solution:**
1. Define ContentAnalyzer interface in `core/services/`
2. Implement basic content analysis:
   - Text sentiment analysis
   - Topic extraction
   - Quality scoring
3. Integrate with ML pipeline
4. Add to DI container

**Dependencies:**
- ML infrastructure
- NLP libraries (if not already available)
- Core services structure

**Acceptance Criteria:**
- [ ] ContentAnalyzer service implemented
- [ ] Basic analysis features working
- [ ] Tests with sample content
- [ ] DI integration complete
- [ ] Documentation added

---

### Issue #5: Implement Repository Protocols for Subscription Service
**Priority:** HIGH
**Milestone:** Week 2
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `repositories`

**Current State:**
Subscription service references repositories that don't exist yet.

**Location:**
- `apps/bot/services/subscription_service.py:7`

**Proposed Solution:**
1. Define subscription repository protocol in `core/ports/`
2. Implement repository in `infra/db/repositories/`
3. Add to repository factory
4. Update subscription service to use repository

**Dependencies:**
- Database schema for subscriptions
- Repository factory pattern

**Acceptance Criteria:**
- [ ] Repository protocol defined
- [ ] Repository implementation complete
- [ ] Factory integration done
- [ ] Subscription service updated
- [ ] Tests pass

---

## 🟡 MEDIUM PRIORITY - Week 3 (8 issues)

### Issue #6: Implement AI Security Analysis Service
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 6 hours
**Label:** `technical-debt`, `enhancement`, `ai-services`, `security`

**Current State:**
AI services router has placeholder for security analysis.

**Location:**
- `apps/api/routers/ai_services_router.py:277`

**Proposed Solution:**
1. Design security analysis service interface
2. Implement threat detection algorithms
3. Integrate with existing security engine
4. Add caching for analysis results
5. Create API endpoints

**Dependencies:**
- Security engine (core/security_engine/)
- ML models for threat detection
- Test data for validation

**Acceptance Criteria:**
- [ ] Service implemented with real analysis
- [ ] Integration with security engine
- [ ] API endpoints functional
- [ ] Performance optimized with caching
- [ ] Tests cover common threat scenarios

---

### Issue #7: Integrate Payment System with Content Protection
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 4 hours
**Label:** `technical-debt`, `enhancement`, `payment`

**Current State:**
Content protection features reference payment integration but it's not implemented.

**Locations:**
- `apps/api/routers/content_protection_router.py:408`
- `apps/bot/handlers/content_protection.py:735`

**Proposed Solution:**
1. Define payment verification interface
2. Integrate with existing payment adapters
3. Add subscription tier checks
4. Implement access control based on payment status

**Dependencies:**
- Payment system (Phase 2.2)
- Subscription management
- User payment status tracking

**Acceptance Criteria:**
- [ ] Payment verification implemented
- [ ] Access control working
- [ ] Both locations updated
- [ ] Tests for different subscription tiers
- [ ] Error handling for payment failures

---

### Issue #8: Integrate deps_factory with Core DI Container
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 3 hours
**Label:** `technical-debt`, `enhancement`, `di-system`

**Current State:**
deps_factory uses fallback pattern instead of proper DI container integration.

**Location:**
- `apps/api/deps_factory.py:20`

**Proposed Solution:**
1. Refactor deps_factory to use core DI container
2. Remove fallback pattern where possible
3. Maintain demo mode compatibility
4. Update all dependencies

**Dependencies:**
- Core DI container must be stable
- Demo configuration system

**Acceptance Criteria:**
- [ ] deps_factory integrated with DI
- [ ] Demo mode still functional
- [ ] Fallback pattern removed/minimized
- [ ] All dependents updated
- [ ] Tests pass

---

### Issue #9: Implement AlertSentRepository for Proper Tracking
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `repositories`, `alerts`

**Current State:**
Alert tracking mentioned but repository not implemented.

**Location:**
- `apps/jobs/alerts/runner.py:282`

**Proposed Solution:**
1. Define AlertSent repository protocol
2. Implement repository with database backend
3. Track alert delivery status
4. Add query methods for alert history

**Dependencies:**
- Database schema for alert tracking
- Repository factory

**Acceptance Criteria:**
- [ ] Repository protocol defined
- [ ] Implementation complete
- [ ] Alert runner uses repository
- [ ] Query methods working
- [ ] Tests pass

---

### Issue #10: Implement Channel Admin Verification via Telegram API
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `telegram`

**Current State:**
Guard service has placeholder for admin verification.

**Location:**
- `apps/bot/services/guard_service.py:74`

**Proposed Solution:**
1. Integrate with Telegram Bot API
2. Implement getChatMember check
3. Add caching for admin status
4. Handle edge cases (private channels, etc.)

**Dependencies:**
- Telegram Bot API client
- MTProto client (if needed for advanced checks)

**Acceptance Criteria:**
- [ ] Admin verification working
- [ ] Caching implemented
- [ ] Edge cases handled
- [ ] Tests with mock Telegram API
- [ ] Rate limiting respected

---

### Issue #11: Implement Schedule Repository
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `repositories`, `scheduling`

**Current State:**
Referenced but not implemented.

**Location:**
- `apps/api/deps.py:196`

**Proposed Solution:**
1. Define schedule repository protocol
2. Implement with database backend
3. Add CRUD operations for scheduled posts
4. Integrate with scheduling services

**Dependencies:**
- Database schema for schedules
- Repository factory

**Acceptance Criteria:**
- [ ] Repository implemented
- [ ] CRUD operations working
- [ ] Integration with scheduler
- [ ] Tests pass
- [ ] Migration created

---

### Issue #12: Implement Delivery Repository
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `repositories`, `delivery`

**Current State:**
Referenced but not implemented.

**Location:**
- `apps/api/deps.py:207`

**Proposed Solution:**
1. Define delivery repository protocol
2. Implement with database backend
3. Track delivery status and history
4. Add query methods

**Dependencies:**
- Database schema for deliveries
- Repository factory

**Acceptance Criteria:**
- [ ] Repository implemented
- [ ] Status tracking working
- [ ] History queries functional
- [ ] Tests pass
- [ ] Migration created

---

### Issue #13: Implement Bot-Telegram Integration for Alerts
**Priority:** MEDIUM
**Milestone:** Week 3
**Effort:** 3 hours
**Label:** `technical-debt`, `enhancement`, `alerts`, `telegram`

**Current State:**
Alert sending mentioned but bot integration not implemented.

**Location:**
- `apps/jobs/alerts/runner.py:302`

**Proposed Solution:**
1. Create alert message formatter
2. Integrate with bot's message sending
3. Add user notification preferences
4. Implement delivery retry logic

**Dependencies:**
- Bot adapter
- User preferences system

**Acceptance Criteria:**
- [ ] Alerts sent via Telegram bot
- [ ] Message formatting working
- [ ] User preferences respected
- [ ] Retry logic functional
- [ ] Tests with mock bot

---

## 🟢 LOW PRIORITY - Future (5 issues)

### Issue #14: Implement Premium Emoji Placeholder Parsing
**Priority:** LOW
**Milestone:** Future
**Effort:** 1 hour
**Label:** `technical-debt`, `enhancement`, `premium-features`

**Current State:**
Premium emoji service has placeholder for text parsing.

**Location:**
- `apps/bot/services/premium_emoji_service.py:84`

**Proposed Solution:**
1. Define emoji placeholder syntax
2. Implement parser
3. Add emoji replacement logic
4. Integrate with premium tier check

**Dependencies:**
- Premium emoji catalog
- Subscription tier verification

**Acceptance Criteria:**
- [ ] Parser implemented
- [ ] Placeholders replaced correctly
- [ ] Premium tier check working
- [ ] Tests with various formats

---

### Issue #15: Implement User-Specific Export Settings
**Priority:** LOW
**Milestone:** Future
**Effort:** 2 hours
**Label:** `technical-debt`, `enhancement`, `export`

**Current State:**
Export handler uses hardcoded default values for channel and period.

**Location:**
- `apps/bot/handlers/exports.py:168`

**Proposed Solution:**
1. Add user settings for exports
2. Store preferred channel and periods
3. Update export handler to use settings
4. Add settings UI in bot

**Dependencies:**
- User settings system
- Database schema updates

**Acceptance Criteria:**
- [ ] User settings stored
- [ ] Export handler uses settings
- [ ] Default values maintained as fallback
- [ ] Tests pass

---

### Issue #16: Implement Actual Database Lookup for Password Reset
**Priority:** LOW
**Milestone:** Future
**Effort:** 1 hour
**Label:** `technical-debt`, `enhancement`, `auth`

**Current State:**
Password reset has placeholder comments.

**Location:**
- Referenced in docs (TASK_1_2_HYBRID_PLAN.md:595)

**Proposed Solution:**
1. Implement database user lookup
2. Generate secure reset tokens
3. Send reset email
4. Implement token verification

**Dependencies:**
- Email service
- Token generation system

**Acceptance Criteria:**
- [ ] Database lookup working
- [ ] Token generation secure
- [ ] Email sending functional
- [ ] Token verification implemented

---

### Issue #17: Implement claim_due_posts with Clean Architecture
**Priority:** LOW
**Milestone:** Future
**Effort:** 3 hours
**Label:** `technical-debt`, `enhancement`, `celery-tasks`

**Current State:**
Celery task has placeholder implementation.

**Location:**
- `apps/celery/tasks/bot_tasks.py:126`

**Proposed Solution:**
1. Define post claiming service interface
2. Implement service in core layer
3. Update celery task to use service
4. Add proper error handling

**Dependencies:**
- Post claiming business logic defined
- Database access patterns

**Acceptance Criteria:**
- [ ] Service implemented
- [ ] Celery task updated
- [ ] Tests pass
- [ ] Performance acceptable

---

### Issue #18: Implement requeue_stuck_sending_posts with Clean Architecture
**Priority:** LOW
**Milestone:** Future
**Effort:** 3 hours
**Label:** `technical-debt`, `enhancement`, `celery-tasks`

**Current State:**
Celery tasks have placeholder implementation.

**Locations:**
- `apps/celery/tasks/bot_tasks.py:275`
- `apps/bot/tasks.py:269`

**Proposed Solution:**
1. Define post requeue service interface
2. Implement service in core layer
3. Update both celery task locations
4. Add stuck post detection logic

**Dependencies:**
- Post status tracking
- Retry logic definition

**Acceptance Criteria:**
- [ ] Service implemented
- [ ] Both locations updated
- [ ] Stuck detection working
- [ ] Tests pass

---

## 📊 Summary Statistics

**Total Issues:** 18
**HIGH Priority:** 5 (Week 2)
**MEDIUM Priority:** 8 (Week 3)
**LOW Priority:** 5 (Future)

**Estimated Effort:**
- HIGH: 15 hours
- MEDIUM: 24 hours
- LOW: 10 hours
- **Total: 49 hours**

**Labels Used:**
- `technical-debt` (all)
- `enhancement` (all)
- `di-system` (3)
- `security` (2)
- `repositories` (5)
- `analytics` (1)
- `ml-services` (1)
- `ai-services` (1)
- `payment` (1)
- `alerts` (2)
- `telegram` (2)
- `scheduling` (1)
- `delivery` (1)
- `premium-features` (1)
- `export` (1)
- `auth` (1)
- `celery-tasks` (2)

---

## 🎯 Next Actions

1. **Create these issues in GitHub** with appropriate labels and milestones
2. **Update TODO markers** to reference issue numbers
3. **Link to Week 1 Action Plan** for coordination
4. **Assign to appropriate developers** based on expertise
5. **Track progress** in project board

---

**Generated:** October 19, 2025
**Source:** Task 1.2 Phase 2 - TODO Marker Cleanup
**Related:** [Week 1 Action Plan](./WEEK_1_ACTION_PLAN.md), [Task 1.2 Hybrid Plan](./TASK_1_2_HYBRID_PLAN.md)
