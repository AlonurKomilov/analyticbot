# Known Limitations & Workarounds

**Last Updated:** October 19, 2025
**Status:** Active Development
**Related:** [GitHub Issues - TODO Cleanup](./GITHUB_ISSUES_TODO_CLEANUP.md), [Week 1 Action Plan](./WEEK_1_ACTION_PLAN.md)

This document catalogs known limitations in the AnalyticBot system, provides workarounds where available, and links to tracking issues for planned resolutions.

---

## 📋 Table of Contents

1. [Service Integration](#1-service-integration)
2. [Dependency Injection](#2-dependency-injection)
3. [Repository Layer](#3-repository-layer)
4. [Authentication & Security](#4-authentication--security)
5. [Background Jobs](#5-background-jobs)
6. [Payment Integration](#6-payment-integration)
7. [AI/ML Services](#7-aiml-services)
8. [Export Features](#8-export-features)
9. [Telegram Integration](#9-telegram-integration)
10. [Testing & Coverage](#10-testing--coverage)

---

## 1. Service Integration

### 1.1 Chart Service Not in DI Container

**Status:** ⚠️ Temporary Workaround
**Tracking:** GitHub Issue #1
**Priority:** HIGH

**Limitation:**
Chart service is instantiated via factory functions in 4 locations instead of using dependency injection:
- `apps/bot/handlers/admin_handlers.py`
- `apps/bot/handlers/exports.py`
- `apps/api/routers/exports_router.py`
- `apps/api/routers/sharing_router.py`

**Impact:**
- Harder to test (requires factory patching)
- Inconsistent service lifecycle
- Violates DI architecture principles

**Current Workaround:**
```python
# Temporary factory function
def get_chart_service():
    from apps.shared.services.chart_service import create_chart_service
    return create_chart_service()
```

**Planned Resolution:**
Week 2 - Create `ChartServiceProvider` and register in DI container (3 hours)

---

### 1.2 Job Services Use Simulated Processing

**Status:** ⚠️ Placeholder Implementation
**Tracking:** GitHub Issue #3
**Priority:** HIGH

**Limitation:**
Analytics and delivery job services contain only simulated processing:
- `AnalyticsJobService.process_analytics_data()` - Returns mock results
- `DeliveryJobService.deliver_scheduled_content()` - Simulates delivery

**Impact:**
- No actual background processing
- Cannot use for production workloads
- Tests don't reflect real behavior

**Current Workaround:**
```python
# Simulated processing
processed_items = len(data)
result = {"status": "completed", "processed_items": processed_items}
```

**Planned Resolution:**
Week 2 - Integrate with core analytics and delivery services (4 hours)

---

### 1.3 Demo Data Service Uses Fallback Pattern

**Status:** ⚠️ Temporary Implementation
**Tracking:** GitHub Issue #8
**Priority:** MEDIUM

**Limitation:**
`deps_factory.py` uses fallback pattern instead of proper DI container integration.

**Impact:**
- Inconsistent dependency resolution
- Demo mode tightly coupled to factory
- Harder to extend with new services

**Current Workaround:**
Factory checks demo_config and returns appropriate service implementation.

**Planned Resolution:**
Week 3 - Refactor to use core DI container (3 hours)

---

## 2. Dependency Injection

### 2.1 Limited DI Coverage in API Layer

**Status:** ⚠️ Partial Coverage
**Tracking:** Multiple issues
**Priority:** MEDIUM

**Limitation:**
Some API dependencies still use direct imports or factory functions instead of DI:
- Chart services (4 locations)
- Demo services (deps_factory)
- Some repository instantiations

**Impact:**
- Inconsistent architecture
- Harder to test and mock
- Violates clean architecture boundaries

**Current Workaround:**
Mix of DI and factory patterns based on component maturity.

**Planned Resolution:**
Week 2-3 - Systematic migration to DI container (ongoing)

---

## 3. Repository Layer

### 3.1 Missing Repository Implementations

**Status:** 🔴 Not Implemented
**Tracking:** GitHub Issues #5, #9, #11, #12
**Priority:** HIGH-MEDIUM

**Limitation:**
Several repositories referenced but not yet implemented:
- **SubscriptionRepository** (HIGH priority)
- **AlertSentRepository** (MEDIUM priority)
- **ScheduleRepository** (MEDIUM priority)
- **DeliveryRepository** (MEDIUM priority)

**Impact:**
- Services cannot persist data
- Features incomplete
- Tests use mocks only

**Current Workaround:**
Services use in-memory data or skip persistence entirely.

**Planned Resolution:**
- Week 2: SubscriptionRepository (2 hours)
- Week 3: Alert, Schedule, Delivery repositories (6 hours total)

---

### 3.2 Repository Factory Not Fully Integrated

**Status:** ⚠️ Partial Implementation
**Priority:** MEDIUM

**Limitation:**
Not all repositories are registered in the repository factory.

**Impact:**
- Inconsistent repository access patterns
- Some code uses direct instantiation

**Current Workaround:**
Direct repository instantiation where factory doesn't provide access.

**Planned Resolution:**
Week 3 - Complete factory integration as repositories are implemented

---

## 4. Authentication & Security

### 4.1 Session Invalidation Not Implemented

**Status:** 🔴 Critical Gap
**Tracking:** GitHub Issue #2
**Priority:** HIGH

**Limitation:**
Admin logout endpoint doesn't actually invalidate sessions. System relies only on JWT expiration (stateless).

**Location:** `apps/api/routers/superadmin_router.py:224`

**Security Impact:**
- ⚠️ Stolen tokens remain valid until expiration
- ⚠️ No immediate revocation capability
- ⚠️ Cannot force logout on security incidents

**Current Workaround:**
Short JWT expiration times (15 minutes recommended) mitigate risk.

**Planned Resolution:**
Week 2 - Implement Redis-based token blacklist (2 hours)

**Immediate Mitigation:**
```python
# Ensure short JWT expiration
JWT_EXPIRATION = 15 * 60  # 15 minutes
```

---

### 4.2 Channel Admin Verification Uses Placeholder

**Status:** ⚠️ Incomplete
**Tracking:** GitHub Issue #10
**Priority:** MEDIUM

**Limitation:**
Guard service has placeholder for admin verification via Telegram API.

**Impact:**
- Cannot verify actual channel admin status
- Security check incomplete

**Current Workaround:**
Basic permission checks without Telegram API verification.

**Planned Resolution:**
Week 3 - Integrate with Telegram Bot API getChatMember (2 hours)

---

## 5. Background Jobs

### 5.1 Celery Tasks Use Placeholders

**Status:** ⚠️ Placeholder Implementations
**Tracking:** GitHub Issues #17, #18
**Priority:** LOW

**Limitation:**
Several Celery tasks have placeholder implementations:
- `claim_due_posts` - Not implemented
- `requeue_stuck_sending_posts` - Not implemented
- `cleanup_old_posts` - Not implemented

**Impact:**
- Background job scheduling exists but doesn't perform work
- Cannot rely on automated cleanup/processing

**Current Workaround:**
Manual intervention or alternative cleanup mechanisms.

**Planned Resolution:**
Future - Implement with clean architecture patterns (6 hours total)

---

## 6. Payment Integration

### 6.1 Content Protection Payment Integration Missing

**Status:** 🔴 Not Implemented
**Tracking:** GitHub Issue #7
**Priority:** MEDIUM

**Limitation:**
Content protection features reference payment integration but it's not connected.

**Locations:**
- `apps/api/routers/content_protection_router.py:408`
- `apps/bot/handlers/content_protection.py:735`

**Impact:**
- Cannot gate premium features
- No subscription tier verification
- Payment-based access control missing

**Current Workaround:**
All users have access to all features (acceptable for beta/testing).

**Planned Resolution:**
Week 3 - Integrate with payment system Phase 2.2 (4 hours)

---

## 7. AI/ML Services

### 7.1 ContentAnalyzer Service Not Implemented

**Status:** 🔴 Not Implemented
**Tracking:** GitHub Issue #4
**Priority:** HIGH

**Limitation:**
ContentAnalyzer is referenced in ML pipeline but doesn't exist.

**Impact:**
- No automated content analysis
- ML features incomplete
- Cannot provide content insights

**Current Workaround:**
Skip content analysis in ML pipeline.

**Planned Resolution:**
Week 2 - Implement basic ContentAnalyzer (4 hours)

---

### 7.2 AI Security Analysis Service Is Placeholder

**Status:** 🔴 Not Implemented
**Tracking:** GitHub Issue #6
**Priority:** MEDIUM

**Limitation:**
AI services router has placeholder for security analysis.

**Location:** `apps/api/routers/ai_services_router.py:277`

**Impact:**
- No AI-powered threat detection
- Security analysis endpoint non-functional

**Current Workaround:**
Use existing security engine without AI enhancement.

**Planned Resolution:**
Week 3 - Implement AI security service (6 hours)

---

## 8. Export Features

### 8.1 User-Specific Export Settings Not Implemented

**Status:** ⚠️ Uses Defaults
**Tracking:** GitHub Issue #15
**Priority:** LOW

**Limitation:**
Export handler uses hardcoded defaults for channel and period:
```python
channel_id = "@demo_channel"  # Default export channel
period = 30  # Default export period in days
```

**Impact:**
- Users cannot customize export preferences
- Must use default values for all exports

**Current Workaround:**
Defaults work for most use cases. Advanced users can use direct API with parameters.

**Planned Resolution:**
Future - Add user settings system (2 hours)

---

## 9. Telegram Integration

### 9.1 Alert Bot Integration Not Connected

**Status:** 🔴 Not Implemented
**Tracking:** GitHub Issue #13
**Priority:** MEDIUM

**Limitation:**
Alert sending is mentioned but bot integration doesn't exist.

**Location:** `apps/jobs/alerts/runner.py:302`

**Impact:**
- Alerts generated but not delivered
- Users don't receive notifications

**Current Workaround:**
View alerts in web dashboard only.

**Planned Resolution:**
Week 3 - Implement bot alert delivery (3 hours)

---

### 9.2 Premium Emoji Parsing Not Implemented

**Status:** ⚠️ Placeholder
**Tracking:** GitHub Issue #14
**Priority:** LOW

**Limitation:**
Premium emoji service has placeholder for text parsing.

**Impact:**
- Cannot replace emoji placeholders
- Premium feature non-functional

**Current Workaround:**
Feature disabled/not advertised.

**Planned Resolution:**
Future - Implement parser (1 hour)

---

## 10. Testing & Coverage

### 10.1 Low Test Coverage for New Features

**Status:** ⚠️ Improvement Needed
**Tracking:** Week 1 Action Plan - Issue #8
**Priority:** HIGH

**Limitation:**
Current test coverage: ~15-18% (target: 25% by Week 1 end)

**Impact:**
- Higher risk of regressions
- Harder to refactor confidently
- Quality concerns

**Current Workaround:**
Manual testing and careful code review.

**Planned Resolution:**
Days 2-7 of Week 1 - Add comprehensive tests (15-20 hours)

**Focus Areas:**
1. Payment system tests (30% → 70%)
2. Integration tests for critical paths
3. API endpoint tests
4. Background job tests

---

## 📊 Summary Dashboard

### By Priority

| Priority | Count | Total Effort |
|----------|-------|--------------|
| 🔴 HIGH | 5 | 15 hours |
| 🟡 MEDIUM | 8 | 24 hours |
| 🟢 LOW | 5 | 10 hours |
| **Total** | **18** | **49 hours** |

### By Category

| Category | Limitations | Status |
|----------|-------------|--------|
| Service Integration | 3 | ⚠️ Partial |
| Dependency Injection | 2 | ⚠️ Partial |
| Repository Layer | 5 | 🔴 Critical |
| Auth & Security | 2 | 🔴 Critical |
| Background Jobs | 3 | ⚠️ Partial |
| Payment Integration | 1 | 🔴 Missing |
| AI/ML Services | 2 | 🔴 Missing |
| Export Features | 1 | ⚠️ Basic |
| Telegram Integration | 2 | ⚠️ Partial |
| Testing | 1 | ⚠️ Improving |

### Resolution Timeline

**Week 2 (HIGH Priority):**
- Session invalidation ✓
- Chart service DI ✓
- Job service integration ✓
- ContentAnalyzer ✓
- Subscription repository ✓

**Week 3 (MEDIUM Priority):**
- AI security service ✓
- Payment integration ✓
- Repository implementations ✓
- Alert bot integration ✓
- Admin verification ✓

**Future (LOW Priority):**
- Celery task implementations
- Premium emoji parsing
- User export settings
- Password reset improvements

---

## 🎯 Using This Document

### For Developers

1. **Before starting new features**: Check if dependencies listed here
2. **When encountering TODOs**: Reference this doc for context
3. **When testing**: Be aware of limitations in related areas

### For Product/PM

1. **Feature planning**: Consider limitations when scoping
2. **User communication**: Know what's not yet implemented
3. **Priority decisions**: Use effort estimates from tracking issues

### For QA

1. **Test planning**: Focus on implemented features
2. **Bug reports**: Check if issue is known limitation
3. **Regression testing**: Monitor as limitations are resolved

---

## 🔄 Maintenance

This document is maintained as part of the technical debt tracking process:

1. **Update frequency**: Weekly during active development
2. **Review trigger**: When limitations are resolved or new ones discovered
3. **Owner**: Architecture team / Tech Lead
4. **Related docs**: GitHub Issues, Week Action Plans, Architecture Decision Records

**Last reviewed:** October 19, 2025
**Next review:** October 26, 2025
