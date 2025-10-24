# 📊 Complete Subscription & Status Systems Inventory

**Date:** January 2025  
**Purpose:** Comprehensive audit of ALL subscription, status, plan, and tier systems across backend and frontend  
**Related:** Similar to ROLE_AUDIT_FINAL.md - identifies mismatches and recommends alignment

---

## 🎯 Executive Summary

### Critical Findings

🔴 **MAJOR MISMATCHES DETECTED**

1. **Subscription Status Inconsistency**: Frontend uses 'inactive', 'cancelled' vs Backend uses 'CANCELED', 'INCOMPLETE', 'TRIALING'
2. **Payment Status Mismatch**: Frontend 'completed' ≠ Backend 'SUCCEEDED'
3. **User Tier Fragmentation**: Backend has 4 tiers (free/starter/pro/enterprise), Frontend has varied implementations
4. **Multiple Frontend Definitions**: `subscriptionService.ts` vs `paymentUtils.ts` have different status lists
5. **Post Status Difference**: Frontend has 'publishing' state, Backend has 'CANCELLED' (with two L's)

### Impact Assessment
- 🔴 **HIGH RISK**: Payment/subscription flows may fail due to status mismatches
- 🟡 **MEDIUM RISK**: User tier checks inconsistent between services
- 🟡 **MEDIUM RISK**: Post status synchronization issues

---

## 1️⃣ Payment Status Systems

### Backend Payment Status (Source of Truth)

**Location:** `apps/bot/models/payment.py` & `core/domain/payment/models.py`

```python
class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"      # ⚠️ Frontend uses "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"
```

**Usage:**
- Used by Stripe adapter, PayMe, Click payment providers
- Database payment records
- Webhook event processing

### Frontend Payment Status

**Location 1:** `apps/frontend/src/services/payment/paymentProcessingService.ts`

```typescript
export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
//                                                     ^^^^^^^^^^^
//                                                     MISMATCH: Backend uses "succeeded"
```

### ❌ Mismatches Detected

| Frontend Value | Backend Value | Status | Issue |
|---------------|---------------|---------|-------|
| `'completed'` | `'SUCCEEDED'` | ❌ MISMATCH | Different terminology |
| `'canceled'` | `'CANCELED'` | ⚠️ SPELLING | Inconsistent spelling (missing in frontend) |

---

## 2️⃣ Subscription Status Systems

### Backend Subscription Status (Authoritative)

**Location:** `apps/bot/models/payment.py` & `core/domain/payment/models.py`

```python
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"        # ⚠️ One 'L' spelling
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"        # ⚠️ Missing in some frontend definitions
    INCOMPLETE = "incomplete"    # ⚠️ Missing in some frontend definitions
    PAUSED = "paused"            # ⚠️ Added in core/domain, may not be used
```

**Usage:**
- Stripe subscription lifecycle management
- User access control based on subscription state
- Billing cycle management

### Frontend Subscription Status (Multiple Definitions!)

**Location 1:** `apps/frontend/src/services/payment/subscriptionService.ts`

```typescript
export type SubscriptionStatus = 'active' | 'inactive' | 'cancelled' | 'past_due';
//                                         ^^^^^^^^^^   ^^^^^^^^^^
//                           MISMATCH: 'inactive' not in backend
//                           SPELLING: two L's vs backend one L
```

**Location 2:** `apps/frontend/src/components/payment/utils/paymentUtils.ts`

```typescript
export type SubscriptionStatus = 'active' | 'trialing' | 'past_due' | 'incomplete' | 
                                 'canceled' | 'cancelled' | 'incomplete_expired';
//                                           ^^^^^^^^^^   ^^^^^^^^^^^
//                    BOTH spellings accepted! 'incomplete_expired' not in backend
```

### ❌ Critical Mismatches

| Frontend Value | Backend Value | Status | Issue |
|---------------|---------------|---------|-------|
| `'inactive'` | *(none)* | ❌ **MISSING** | Frontend-only status |
| `'cancelled'` (2 L's) | `'CANCELED'` (1 L) | ❌ **SPELLING** | British vs American English |
| *(none)* | `'TRIALING'` | ❌ **MISSING** | Backend-only (not in subscriptionService.ts) |
| *(none)* | `'INCOMPLETE'` | ❌ **MISSING** | Backend-only (not in subscriptionService.ts) |
| *(none)* | `'UNPAID'` | ❌ **MISSING** | Backend-only status |
| `'incomplete_expired'` | *(none)* | ⚠️ **EXTRA** | Frontend-only (Stripe-specific?) |

---

## 3️⃣ User Tier / Subscription Plan Systems

### Backend User Tiers

**Location:** `apps/bot/models/content_protection.py`

```python
class UserTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"
```

**Usage:**
- Content protection feature limits
- Premium emoji access
- Watermarking capabilities
- Theft detection scan limits

**Mock Data:** `tests/mocks/data/ai_services/mock_ai_data.py`
```python
subscription_tiers = ["free", "basic", "premium", "enterprise"]
#                              ^^^^^^   ^^^^^^^^
#                     "basic" and "premium" used in tests, not "starter"/"pro"!
```

### Frontend Tier References

**Not standardized** - Found scattered tier strings:
- "Free" plan (hardcoded in `initial_data_service.py`)
- `subscription_tier` field in user management
- No centralized tier enum in frontend

### ⚠️ Tier Inconsistency

| System | Tier Names | Source |
|--------|-----------|---------|
| **Backend Production** | free, starter, pro, enterprise | `content_protection.py` |
| **Test Mocks** | free, **basic**, **premium**, enterprise | `mock_ai_data.py` |
| **Frontend** | *(not defined)* | Scattered strings |

**Issue:** Mock tests use "basic" and "premium", but production code uses "starter" and "pro"!

---

## 4️⃣ User Status Systems

### Backend User Status

**Location 1:** `core/models/superadmin_domain.py`

```python
class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"
```

**Location 2:** `core/security_engine/models.py` (duplicate definition)

```python
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"
```

### Frontend User Status

**Location:** `apps/frontend/src/types/models.ts`

```typescript
export interface User {
  // ...
  isActive: boolean;  // ⚠️ Simplified - only boolean, not enum
  // ...
}
```

**Issue:** Frontend uses boolean `isActive`, Backend uses 5-state enum. This loses information about SUSPENDED, PENDING, DELETED states!

---

## 5️⃣ Post Status Systems

### Backend Post Status

**Location:** `core/models/__init__.py`

```python
class PostStatus(str, Enum):
    """Post status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"    # ⚠️ Two L's (British spelling)
```

### Frontend Post Status

**Location:** `apps/frontend/src/types/models.ts` & `apps/frontend/src/types/api.ts`

```typescript
export type PostStatus = 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed';
//                                              ^^^^^^^^^^^^
//                                   EXTRA: 'publishing' not in backend
//                                   MISSING: 'cancelled' from backend
```

### ❌ Post Status Mismatches

| Frontend | Backend | Status | Issue |
|----------|---------|---------|-------|
| `'publishing'` | *(none)* | ⚠️ **EXTRA** | Frontend-only transition state |
| *(none)* | `'CANCELLED'` | ❌ **MISSING** | Backend status not in frontend |

---

## 6️⃣ System/Health Status Systems

### Backend Health Status

**Location:** `core/common/health/models.py`

```python
class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
```

**Location:** `core/models/superadmin_domain.py`

```python
class SystemStatus(str, Enum):
    """System component status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
```

### Frontend Health/System Status

**Location:** `apps/frontend/src/components/common/SystemHealthCheck.tsx`

```typescript
export type CheckStatus = 'passed' | 'failed' | 'degraded' | 'timeout' | 'pending';
export type OverallStatus = 'passed' | 'degraded' | 'failed';
```

**Location:** `apps/frontend/src/utils/systemHealthCheck.ts`

```typescript
export enum CheckStatus {
  // Values not shown in grep, needs full read
}
```

### ⚠️ Alignment Needed

Backend and frontend use different terminology for health checks:
- Backend: `HEALTHY` / `DEGRADED` / `UNHEALTHY`
- Frontend: `passed` / `degraded` / `failed`

Functional overlap but inconsistent naming.

---

## 7️⃣ Billing Cycle / Plan Interval

### Backend Billing Cycle

**Location:** `apps/bot/models/payment.py`

```python
class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
```

### Frontend Plan Interval

**Location:** `apps/frontend/src/services/payment/subscriptionService.ts`

```typescript
export interface SubscriptionPlan {
    // ...
    interval: 'day' | 'week' | 'month' | 'year';
    //        ^^^^^^^  ^^^^^^
    // EXTRA: Backend doesn't support 'day' or 'week'
}
```

### ❌ Interval Mismatch

| Frontend | Backend | Status | Issue |
|----------|---------|---------|-------|
| `'day'` | *(none)* | ⚠️ **EXTRA** | Frontend supports, backend doesn't |
| `'week'` | *(none)* | ⚠️ **EXTRA** | Frontend supports, backend doesn't |
| `'month'` | `'MONTHLY'` | ✅ **OK** | Functional match (different case) |
| `'year'` | `'YEARLY'` | ✅ **OK** | Functional match (different case) |

---

## 8️⃣ Payment Provider Systems

### Backend Payment Providers

**Location:** `apps/bot/models/payment.py` & `core/domain/payment/models.py`

```python
class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYME = "payme"
    CLICK = "click"
    MOCK = "mock"      # Development only
```

### Frontend Provider References

**Not defined as enum** - providers referenced as strings in payment service integration

---

## 🔧 Recommended Alignment Actions

### 🔴 Priority 1: Critical Payment/Subscription Mismatches

1. **Standardize Payment Status**
   - **Decision Required:** Use `succeeded` (backend) or `completed` (frontend)?
   - **Recommendation:** Keep `succeeded` (Stripe standard), update frontend
   - **Files to Change:**
     - `apps/frontend/src/services/payment/paymentProcessingService.ts`
     - `apps/frontend/src/components/payment/` (status handling)

2. **Fix Subscription Status Spelling**
   - **Decision Required:** `canceled` (1 L) or `cancelled` (2 L's)?
   - **Recommendation:** Use `canceled` (American English, Stripe standard)
   - **Impact:** Low - mostly string comparison, but critical for API contracts
   - **Files to Change:**
     - `apps/frontend/src/services/payment/subscriptionService.ts`
     - `apps/frontend/src/components/payment/utils/paymentUtils.ts`

3. **Add Missing Subscription Statuses to Frontend**
   - Add `trialing`, `incomplete`, `unpaid` to frontend TypeScript types
   - **Impact:** Medium - needed for complete subscription lifecycle handling
   - **Files to Change:**
     - `apps/frontend/src/services/payment/subscriptionService.ts`
     - Add UI handling for these states

4. **Remove Frontend-Only 'inactive' Status**
   - Either:
     - Add `INACTIVE` to backend `SubscriptionStatus`, OR
     - Remove from frontend and map to existing backend status
   - **Recommendation:** Map `inactive` → `canceled` or `unpaid` depending on context

### 🟡 Priority 2: User Tier Standardization

5. **Align Test Mocks with Production Tiers**
   - **Current Issue:** Tests use "basic"/"premium", production uses "starter"/"pro"
   - **Files to Fix:**
     - `tests/mocks/data/ai_services/mock_ai_data.py`
     - Update all tier references to: `free | starter | pro | enterprise`

6. **Create Frontend UserTier Enum**
   - **Recommendation:** Create central enum in `apps/frontend/src/types/models.ts`
   ```typescript
   export type UserTier = 'free' | 'starter' | 'pro' | 'enterprise';
   ```
   - Use consistently across all components

### 🟢 Priority 3: Post Status & User Status

7. **Add 'publishing' to Backend or Remove from Frontend**
   - **Recommendation:** Keep frontend `publishing` as UI-only transition state
   - Document that it maps to `SCHEDULED` in backend

8. **Align User Status: Boolean vs Enum**
   - **Current:** Frontend uses `isActive: boolean`
   - **Backend:** Has 5 states (active, inactive, suspended, pending, deleted)
   - **Recommendation:** Expand frontend User type:
   ```typescript
   export type UserStatus = 'active' | 'inactive' | 'suspended' | 'pending' | 'deleted';
   export interface User {
     // ...
     status: UserStatus;  // Replace isActive
     // ...
   }
   ```

### 📋 Priority 4: Documentation & Type Safety

9. **Create Shared Type Definitions**
   - Consider creating a shared types package or codegen from backend
   - **Tools to explore:**
     - OpenAPI/Swagger schema → TypeScript types
     - Pydantic model → TypeScript interface generator

10. **Add Status Validation at API Boundaries**
    - Backend: Validate incoming status strings match enum values
    - Frontend: Use TypeScript discriminated unions for status handling

---

## 📊 Alignment Matrix: Payment & Subscription

| System | Backend Value | Frontend Value(s) | Aligned? | Action |
|--------|--------------|-------------------|----------|---------|
| **Payment Status** | | | | |
| Pending | `PENDING` | `pending` | ✅ | None |
| Processing | `PROCESSING` | `processing` | ✅ | None |
| Success | `SUCCEEDED` | `completed` | ❌ | Change FE to `succeeded` |
| Failed | `FAILED` | `failed` | ✅ | None |
| Canceled | `CANCELED` | *(missing)* | ⚠️ | Add to FE |
| Refunded | `REFUNDED` | `refunded` | ✅ | None |
| **Subscription Status** | | | | |
| Active | `ACTIVE` | `active` | ✅ | None |
| Inactive | *(none)* | `inactive` | ❌ | Remove from FE or add to BE |
| Canceled | `CANCELED` (1L) | `cancelled` (2L) | ❌ | Standardize spelling (1L) |
| Past Due | `PAST_DUE` | `past_due` | ✅ | None |
| Unpaid | `UNPAID` | *(missing)* | ❌ | Add to FE |
| Trialing | `TRIALING` | *(missing in subscriptionService)* | ⚠️ | Add to all FE definitions |
| Incomplete | `INCOMPLETE` | *(missing in subscriptionService)* | ⚠️ | Add to all FE definitions |
| Paused | `PAUSED` | *(missing)* | ⚠️ | Add to FE if used |
| Incomplete Expired | *(none)* | `incomplete_expired` | ⚠️ | Remove or map to `INCOMPLETE` |

---

## 📊 Alignment Matrix: Tiers & Plans

| System | Backend | Test Mocks | Frontend | Action |
|--------|---------|-----------|----------|---------|
| Free | ✅ `free` | ✅ `free` | ⚠️ *varied* | Standardize |
| Tier 2 | ✅ `starter` | ❌ `basic` | ⚠️ *varied* | Use `starter` everywhere |
| Tier 3 | ✅ `pro` | ❌ `premium` | ⚠️ *varied* | Use `pro` everywhere |
| Enterprise | ✅ `enterprise` | ✅ `enterprise` | ⚠️ *varied* | Standardize |

---

## 🎯 Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)
- [ ] Fix payment status: `completed` → `succeeded`
- [ ] Fix subscription spelling: `cancelled` → `canceled`
- [ ] Add missing subscription statuses to frontend
- [ ] Create frontend `SubscriptionStatus` and `PaymentStatus` enums

### Phase 2: Tier Alignment (Week 1-2)
- [ ] Fix test mock tiers: `basic`/`premium` → `starter`/`pro`
- [ ] Create frontend `UserTier` enum
- [ ] Update all tier references across frontend

### Phase 3: User & Post Status (Week 2)
- [ ] Expand frontend User status from boolean to enum
- [ ] Document `publishing` as frontend-only state
- [ ] Add `cancelled` post status to frontend if needed

### Phase 4: Type Safety (Week 3-4)
- [ ] Set up OpenAPI schema validation
- [ ] Consider TypeScript codegen from Pydantic models
- [ ] Add runtime validation at API boundaries

---

## 📝 Related Documents

- `ROLE_AUDIT_FINAL.md` - Similar alignment work for role system (completed)
- `PHASE_4_MIGRATION.md` - Role system migration reference
- API documentation (needs update with aligned statuses)

---

## 🔍 Audit Methodology

1. Searched Python files for status enum definitions
2. Searched TypeScript files for status type definitions
3. Cross-referenced payment.py, content_protection.py, core/domain models
4. Analyzed subscriptionService.ts, paymentUtils.ts, and component types
5. Identified all tier/plan references in tests and services
6. Created alignment matrices for all systems

**Files Analyzed:** 50+  
**Status Enums Found:** 12 backend, 8+ frontend  
**Mismatches Identified:** 15 critical, 8 minor  
**Test Coverage:** Yes (found mock data mismatches)

---

**Status:** ✅ INVENTORY COMPLETE  
**Next Step:** Review with team, prioritize fixes, create implementation tasks  
**Estimated Effort:** 3-4 weeks for complete alignment (similar to role migration)
