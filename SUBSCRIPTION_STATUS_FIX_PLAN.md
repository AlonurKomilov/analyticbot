# 🔧 Subscription & Status Systems - Fix Implementation Plan

**Created:** October 24, 2025
**Related:** SUBSCRIPTION_STATUS_INVENTORY.md
**Estimated Total Effort:** 3-4 weeks
**Risk Level:** Medium (requires API contract changes)

---

## 🎯 Strategic Approach

### Core Principles

1. **Backend as Source of Truth** - All status definitions come from backend enums
2. **Stripe Standards** - Follow Stripe API conventions where applicable
3. **American English** - Use `canceled` (1 L) not `cancelled` (2 L's)
4. **Type Safety First** - Use enums/unions, never raw strings
5. **Backward Compatibility** - Support both old/new values during migration

### Migration Strategy

**Phased rollout with backward compatibility:**
- Phase 1: Add new values without breaking existing code
- Phase 2: Update all usages to new values
- Phase 3: Deprecate old values with warnings
- Phase 4: Remove old values after monitoring period

---

## 📋 Phase 1: Critical Payment & Subscription Fixes (Week 1)

**Goal:** Fix API contract mismatches that could cause payment failures
**Risk:** High - touches payment flow
**Testing Required:** Full payment flow integration tests

### Task 1.1: Standardize Payment Status [Priority: CRITICAL]

**Problem:** Frontend uses `'completed'`, Backend uses `'SUCCEEDED'`

#### Backend Changes (Minimal - already correct)

✅ **No changes needed** - Backend already uses Stripe standard `SUCCEEDED`

**Files verified:**
- `apps/bot/models/payment.py` ✓
- `core/domain/payment/models.py` ✓

#### Frontend Changes

**File 1:** `apps/frontend/src/types/payment.ts` (CREATE NEW)

```typescript
/**
 * Payment & Subscription Type Definitions
 * Aligned with backend enums (October 2025)
 *
 * Backend sources:
 * - apps/bot/models/payment.py
 * - core/domain/payment/models.py
 */

/**
 * Payment status values matching backend PaymentStatus enum
 * CHANGED: 'completed' → 'succeeded' (Stripe standard)
 */
export type PaymentStatus =
  | 'pending'      // Payment initiated, awaiting processing
  | 'processing'   // Payment being processed by provider
  | 'succeeded'    // ✅ CHANGED: was 'completed'
  | 'failed'       // Payment failed
  | 'canceled'     // Payment canceled before completion
  | 'refunded';    // Payment refunded after success

/**
 * Legacy payment status type for backward compatibility
 * @deprecated Use PaymentStatus instead
 */
export type LegacyPaymentStatus = PaymentStatus | 'completed';

/**
 * Map legacy status values to current standard
 */
export function normalizePaymentStatus(status: LegacyPaymentStatus): PaymentStatus {
  if (status === 'completed') {
    console.warn('PaymentStatus "completed" is deprecated, use "succeeded" instead');
    return 'succeeded';
  }
  return status;
}
```

**File 2:** `apps/frontend/src/services/payment/paymentProcessingService.ts`

```typescript
// BEFORE:
export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';

// AFTER:
import { PaymentStatus, normalizePaymentStatus } from '../../types/payment';

// Update all usages:
// - Change 'completed' → 'succeeded' in status checks
// - Wrap incoming legacy statuses with normalizePaymentStatus()
```

**Migration Steps:**

1. Create `apps/frontend/src/types/payment.ts` with new definitions
2. Update `paymentProcessingService.ts`:
   ```typescript
   // Old code:
   if (payment.status === 'completed') { ... }

   // New code:
   if (payment.status === 'succeeded') { ... }
   ```
3. Update all payment UI components:
   - `apps/frontend/src/components/payment/PaymentForm.tsx`
   - `apps/frontend/src/components/payment/SubscriptionDashboardRefactored.tsx`
   - Search for `'completed'` and replace with `'succeeded'`
4. Add backward compatibility wrapper for API responses
5. Test payment flow end-to-end

**Testing Checklist:**
- [ ] Stripe test payment succeeds and shows correct status
- [ ] Mock payment adapter returns `'succeeded'`
- [ ] UI displays success status correctly
- [ ] Legacy API responses still work (if any return `'completed'`)

---

### Task 1.2: Fix Subscription Status Spelling [Priority: CRITICAL]

**Problem:** Inconsistent spelling `'cancelled'` (2 L's) vs `'canceled'` (1 L)

#### Backend Changes

✅ **No changes needed** - Backend consistently uses `CANCELED` (1 L)

#### Frontend Changes

**File 1:** Add to `apps/frontend/src/types/payment.ts`

```typescript
/**
 * Subscription status values matching backend SubscriptionStatus enum
 * CHANGED: Standardized to American English spelling (canceled, not cancelled)
 */
export type SubscriptionStatus =
  | 'active'       // Subscription is active and current
  | 'canceled'     // ✅ CHANGED: was 'cancelled' (British spelling)
  | 'past_due'     // Payment failed, grace period
  | 'unpaid'       // Payment failed, suspended
  | 'trialing'     // In trial period
  | 'incomplete'   // Initial payment incomplete
  | 'paused';      // Temporarily paused (if supported)

/**
 * Legacy type accepting both spellings
 * @deprecated Use SubscriptionStatus
 */
export type LegacySubscriptionStatus = SubscriptionStatus | 'cancelled' | 'inactive';

/**
 * Normalize subscription status to current standard
 */
export function normalizeSubscriptionStatus(
  status: LegacySubscriptionStatus
): SubscriptionStatus {
  // Handle spelling variants
  if (status === 'cancelled') {
    console.warn('SubscriptionStatus "cancelled" is deprecated, use "canceled"');
    return 'canceled';
  }

  // Handle removed statuses
  if (status === 'inactive') {
    console.warn('SubscriptionStatus "inactive" is deprecated, mapping to "canceled"');
    return 'canceled';
  }

  return status as SubscriptionStatus;
}
```

**File 2:** `apps/frontend/src/services/payment/subscriptionService.ts`

```typescript
// BEFORE:
export type SubscriptionStatus = 'active' | 'inactive' | 'cancelled' | 'past_due';

// AFTER:
import { SubscriptionStatus, normalizeSubscriptionStatus } from '../../types/payment';

// Remove local type definition, use imported one

// Update all API response handling:
async getSubscription(subscriptionId: string): Promise<Subscription> {
  const response = await apiClient.get<Subscription>(`${this.baseURL}/detail/${subscriptionId}`);

  // Normalize status from API
  return {
    ...response.data,
    status: normalizeSubscriptionStatus(response.data.status)
  };
}
```

**File 3:** `apps/frontend/src/components/payment/utils/paymentUtils.ts`

```typescript
// BEFORE:
export type SubscriptionStatus = 'active' | 'trialing' | 'past_due' | 'incomplete' |
                                 'canceled' | 'cancelled' | 'incomplete_expired';

// AFTER:
import { SubscriptionStatus } from '../../../types/payment';

// Remove duplicate definition, use centralized type

// Update getStatusColor to handle all statuses:
export const getStatusColor = (status: SubscriptionStatus | string): StatusColor => {
  switch (status) {
    case 'active':
      return 'success';
    case 'trialing':
      return 'info';
    case 'past_due':
    case 'unpaid':
      return 'warning';
    case 'incomplete':
    case 'canceled':
      return 'error';
    case 'paused':
      return 'default';
    default:
      console.warn(`Unknown subscription status: ${status}`);
      return 'default';
  }
};
```

**Migration Steps:**

1. Create centralized types in `apps/frontend/src/types/payment.ts`
2. Update all files using subscription status:
   ```bash
   # Find all files with subscription status references
   grep -r "cancelled" apps/frontend/src/
   grep -r "'inactive'" apps/frontend/src/
   ```
3. Replace spelling:
   - `'cancelled'` → `'canceled'`
   - Remove `'inactive'` references
4. Update UI labels to match:
   - "Cancelled" → "Canceled" in user-facing text
5. Test subscription lifecycle

**Files to Update:**
- `apps/frontend/src/services/payment/subscriptionService.ts` ✓
- `apps/frontend/src/components/payment/utils/paymentUtils.ts` ✓
- `apps/frontend/src/components/payment/subscription/SubscriptionCard.tsx`
- `apps/frontend/src/components/payment/SubscriptionDashboardRefactored.tsx`
- `apps/frontend/src/components/payment/dialogs/CancelSubscriptionDialog.tsx`
- Any other components displaying subscription status

**Testing Checklist:**
- [ ] Active subscription displays correctly
- [ ] Canceled subscription (from backend) displays correctly
- [ ] No console warnings about 'cancelled' spelling
- [ ] Stripe webhook handling works with 'canceled'

---

### Task 1.3: Add Missing Subscription Statuses [Priority: HIGH]

**Problem:** Backend has `TRIALING`, `INCOMPLETE`, `UNPAID` missing in some frontend files

#### Implementation

**Already partially in `paymentUtils.ts`** ✓ - but missing in `subscriptionService.ts`

**Update:** `apps/frontend/src/services/payment/subscriptionService.ts`

```typescript
// The centralized type from Task 1.2 already includes all statuses:
// 'trialing', 'incomplete', 'unpaid', 'paused'

// Add UI handling for new statuses:
export interface Subscription {
  id: string;
  user_id: number;
  plan_id: string;
  status: SubscriptionStatus;  // Now includes all 7 statuses
  current_period_start: string;
  current_period_end: string;
  cancel_at?: string;
  trial_end?: string;           // ✅ ADD: for trialing status
  created_at: string;
}
```

**Add user messaging for new statuses:**

```typescript
// File: apps/frontend/src/utils/subscriptionMessages.ts (NEW)

import { SubscriptionStatus } from '../types/payment';

export interface StatusMessage {
  title: string;
  description: string;
  action?: string;
  severity: 'info' | 'warning' | 'error' | 'success';
}

export function getSubscriptionStatusMessage(status: SubscriptionStatus): StatusMessage {
  switch (status) {
    case 'active':
      return {
        title: 'Subscription Active',
        description: 'Your subscription is active and all features are available.',
        severity: 'success'
      };

    case 'trialing':
      return {
        title: 'Trial Period',
        description: 'You are currently in a trial period. Add a payment method before it ends.',
        action: 'Add Payment Method',
        severity: 'info'
      };

    case 'past_due':
      return {
        title: 'Payment Past Due',
        description: 'Your last payment failed. Please update your payment method to continue service.',
        action: 'Update Payment',
        severity: 'warning'
      };

    case 'unpaid':
      return {
        title: 'Subscription Suspended',
        description: 'Your subscription is suspended due to failed payment. Update payment to restore access.',
        action: 'Update Payment',
        severity: 'error'
      };

    case 'incomplete':
      return {
        title: 'Payment Incomplete',
        description: 'Your initial payment is incomplete. Complete payment to activate subscription.',
        action: 'Complete Payment',
        severity: 'warning'
      };

    case 'canceled':
      return {
        title: 'Subscription Canceled',
        description: 'Your subscription has been canceled. You can resubscribe at any time.',
        action: 'Resubscribe',
        severity: 'info'
      };

    case 'paused':
      return {
        title: 'Subscription Paused',
        description: 'Your subscription is temporarily paused. Resume to regain access.',
        action: 'Resume Subscription',
        severity: 'info'
      };
  }
}
```

**Testing Checklist:**
- [ ] Mock subscription with `trialing` status displays correctly
- [ ] `incomplete` subscription shows payment prompt
- [ ] `unpaid` subscription shows update payment option
- [ ] All status messages render properly

---

## 📋 Phase 2: User Tier System Alignment (Week 2)

**Goal:** Standardize tier naming across production, tests, and frontend
**Risk:** Medium - affects feature access control

### Task 2.1: Fix Test Mock Tier Names [Priority: HIGH]

**Problem:** Test mocks use `basic`/`premium`, production uses `starter`/`pro`

**File:** `tests/mocks/data/ai_services/mock_ai_data.py`

```python
# BEFORE:
subscription_tiers = ["free", "basic", "premium", "enterprise"]

# AFTER:
subscription_tiers = ["free", "starter", "pro", "enterprise"]

# Update all usages in the same file:
# "basic" → "starter"
# "premium" → "pro"
```

**Search and replace across all test files:**

```bash
cd /home/abcdeveloper/projects/analyticbot
grep -r '"basic"' tests/
grep -r '"premium"' tests/
# Replace with "starter" and "pro" respectively
```

**Testing Checklist:**
- [ ] All existing tests pass with new tier names
- [ ] Mock data generation uses correct tiers
- [ ] No references to `basic` or `premium` remain in tests

---

### Task 2.2: Create Frontend UserTier Type [Priority: HIGH]

**Problem:** Frontend has no centralized tier enum

**File:** `apps/frontend/src/types/subscription.ts` (NEW)

```typescript
/**
 * User Subscription Tier System
 * Aligned with backend UserTier enum (apps/bot/models/content_protection.py)
 */

/**
 * User subscription tiers
 * Determines feature access and limits
 */
export type UserTier =
  | 'free'        // Free tier - basic features only
  | 'starter'     // Starter tier - enhanced features
  | 'pro'         // Pro tier - advanced features
  | 'enterprise'; // Enterprise tier - all features + priority support

/**
 * Feature limits per tier
 */
export interface TierLimits {
  maxChannels: number;
  maxPostsPerMonth: number;
  maxFileSize: number; // MB
  watermarksEnabled: boolean;
  theftDetectionEnabled: boolean;
  customEmojisEnabled: boolean;
  prioritySupport: boolean;
  apiAccess: boolean;
}

/**
 * Get feature limits for a tier
 */
export function getTierLimits(tier: UserTier): TierLimits {
  switch (tier) {
    case 'free':
      return {
        maxChannels: 1,
        maxPostsPerMonth: 30,
        maxFileSize: 5,
        watermarksEnabled: false,
        theftDetectionEnabled: false,
        customEmojisEnabled: false,
        prioritySupport: false,
        apiAccess: false
      };

    case 'starter':
      return {
        maxChannels: 3,
        maxPostsPerMonth: 100,
        maxFileSize: 25,
        watermarksEnabled: true,
        theftDetectionEnabled: false,
        customEmojisEnabled: false,
        prioritySupport: false,
        apiAccess: false
      };

    case 'pro':
      return {
        maxChannels: 10,
        maxPostsPerMonth: 500,
        maxFileSize: 100,
        watermarksEnabled: true,
        theftDetectionEnabled: true,
        customEmojisEnabled: true,
        prioritySupport: false,
        apiAccess: true
      };

    case 'enterprise':
      return {
        maxChannels: 9999, // Unlimited
        maxPostsPerMonth: 9999,
        maxFileSize: 500,
        watermarksEnabled: true,
        theftDetectionEnabled: true,
        customEmojisEnabled: true,
        prioritySupport: true,
        apiAccess: true
      };
  }
}

/**
 * Tier display information
 */
export interface TierDisplayInfo {
  name: string;
  displayName: string;
  description: string;
  color: string;
  icon: string;
  popular?: boolean;
}

export const TIER_DISPLAY_INFO: Record<UserTier, TierDisplayInfo> = {
  free: {
    name: 'free',
    displayName: 'Free',
    description: 'Get started with basic features',
    color: '#6B7280',
    icon: '🆓'
  },
  starter: {
    name: 'starter',
    displayName: 'Starter',
    description: 'Perfect for small channels',
    color: '#3B82F6',
    icon: '🚀'
  },
  pro: {
    name: 'pro',
    displayName: 'Pro',
    description: 'Advanced features for growth',
    color: '#8B5CF6',
    icon: '⭐',
    popular: true
  },
  enterprise: {
    name: 'enterprise',
    displayName: 'Enterprise',
    description: 'Full power for large operations',
    color: '#F59E0B',
    icon: '🏢'
  }
};
```

**Update User type:** `apps/frontend/src/types/models.ts`

```typescript
import { UserTier } from './subscription';

export interface User {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  tier: UserTier;        // ✅ ADD: user's subscription tier
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
  preferences?: UserPreferences;
}
```

**Testing Checklist:**
- [ ] Type imports work correctly
- [ ] Tier limits match backend logic
- [ ] UI components can access tier information

---

### Task 2.3: Update All Frontend Tier References [Priority: MEDIUM]

**Search for hardcoded tier strings:**

```bash
cd apps/frontend
grep -r "free" src/ | grep -i tier
grep -r "starter" src/
grep -r "pro" src/ | grep -i tier
grep -r "enterprise" src/
```

**Update components using tiers:**

```typescript
// BEFORE (example):
if (user.plan === "Pro") { ... }

// AFTER:
import { UserTier } from '../../types/subscription';

if (user.tier === 'pro') { ... }
```

**Create tier comparison helper:**

```typescript
// File: apps/frontend/src/utils/tierComparison.ts

import { UserTier } from '../types/subscription';

const TIER_HIERARCHY: Record<UserTier, number> = {
  free: 0,
  starter: 1,
  pro: 2,
  enterprise: 3
};

/**
 * Check if user's tier meets minimum requirement
 */
export function hasTierAccess(userTier: UserTier, requiredTier: UserTier): boolean {
  return TIER_HIERARCHY[userTier] >= TIER_HIERARCHY[requiredTier];
}

/**
 * Check if feature is available for user's tier
 */
export function hasFeatureAccess(userTier: UserTier, feature: string): boolean {
  const limits = getTierLimits(userTier);

  switch (feature) {
    case 'watermarks':
      return limits.watermarksEnabled;
    case 'theft_detection':
      return limits.theftDetectionEnabled;
    case 'custom_emojis':
      return limits.customEmojisEnabled;
    case 'api':
      return limits.apiAccess;
    case 'priority_support':
      return limits.prioritySupport;
    default:
      return false;
  }
}
```

---

## 📋 Phase 3: User Status & Post Status (Week 2-3)

**Goal:** Align user and post status definitions
**Risk:** Low - mostly UI display improvements

### Task 3.1: Expand User Status from Boolean to Enum [Priority: MEDIUM]

**Problem:** Frontend uses `isActive: boolean`, backend has 5-state enum

**Backend (already correct):**
```python
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"
```

**Frontend Update:** `apps/frontend/src/types/models.ts`

```typescript
/**
 * User account status
 * Aligned with backend UserStatus enum
 */
export type UserStatus =
  | 'active'      // Account active and accessible
  | 'inactive'    // Account inactive but not deleted
  | 'suspended'   // Account suspended (violation/payment)
  | 'pending'     // Account pending verification
  | 'deleted';    // Account soft-deleted

export interface User {
  id: string;
  email: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  tier: UserTier;
  status: UserStatus;    // ✅ CHANGED: was isActive: boolean
  createdAt: string;
  updatedAt?: string;
  preferences?: UserPreferences;
}

/**
 * Helper to check if user is active (backward compatibility)
 */
export function isUserActive(user: User): boolean {
  return user.status === 'active';
}
```

**Migration helper for backward compatibility:**

```typescript
// File: apps/frontend/src/utils/userMigration.ts

export interface LegacyUser {
  // ... other fields
  isActive: boolean;
}

export function migrateLegacyUser(legacy: LegacyUser): User {
  return {
    ...legacy,
    status: legacy.isActive ? 'active' : 'inactive',
    // Remove isActive from result
    isActive: undefined as any
  };
}
```

**Update all usage:**

```typescript
// BEFORE:
if (user.isActive) { ... }

// AFTER:
import { isUserActive } from '../../utils/userMigration';

if (isUserActive(user)) { ... }
// or
if (user.status === 'active') { ... }
```

**Add status display component:**

```typescript
// File: apps/frontend/src/components/common/UserStatusBadge.tsx

import React from 'react';
import { Chip } from '@mui/material';
import { UserStatus } from '../../types/models';

interface UserStatusBadgeProps {
  status: UserStatus;
}

export const UserStatusBadge: React.FC<UserStatusBadgeProps> = ({ status }) => {
  const statusConfig: Record<UserStatus, { label: string; color: any }> = {
    active: { label: 'Active', color: 'success' },
    inactive: { label: 'Inactive', color: 'default' },
    suspended: { label: 'Suspended', color: 'error' },
    pending: { label: 'Pending', color: 'warning' },
    deleted: { label: 'Deleted', color: 'error' }
  };

  const config = statusConfig[status];

  return (
    <Chip
      label={config.label}
      color={config.color}
      size="small"
    />
  );
};
```

---

### Task 3.2: Align Post Status [Priority: LOW]

**Problem:** Frontend has `'publishing'`, backend has `'CANCELLED'`

**Decision:** Keep both, document as intentional difference

**File:** `apps/frontend/src/types/models.ts`

```typescript
/**
 * Post status - Frontend includes transition states
 * Backend PostStatus: draft, scheduled, published, failed, cancelled
 */
export type PostStatus =
  | 'draft'       // Post being edited
  | 'scheduled'   // Scheduled for future
  | 'publishing'  // ⚠️ FRONTEND-ONLY: Currently publishing (transition state)
  | 'published'   // Successfully published
  | 'failed'      // Publishing failed
  | 'cancelled';  // ✅ ADDED: Scheduled post cancelled

/**
 * Backend post status (for API compatibility)
 */
export type BackendPostStatus = Exclude<PostStatus, 'publishing'>;

/**
 * Map backend status to frontend display status
 */
export function mapBackendPostStatus(backendStatus: BackendPostStatus): PostStatus {
  // Backend doesn't have 'publishing' state
  // If post is scheduled and current time > scheduled_time, show as 'publishing'
  return backendStatus;
}
```

**Document this in code comments:**

```typescript
/**
 * Note: 'publishing' is a frontend-only transition state
 *
 * Backend flow: scheduled → published (or failed)
 * Frontend flow: scheduled → publishing → published (or failed)
 *
 * The 'publishing' state is shown in UI when:
 * - Post status is 'scheduled'
 * - Current time >= scheduled time
 * - Status hasn't updated to 'published' yet (polling delay)
 */
```

---

## 📋 Phase 4: Type Safety & Validation (Week 3-4)

**Goal:** Prevent future mismatches with automated validation
**Risk:** Low - infrastructure improvements

### Task 4.1: Create Shared OpenAPI Schema

**Generate TypeScript types from backend:**

```bash
# Install openapi-typescript
npm install -D openapi-typescript

# Add script to package.json
"scripts": {
  "generate-types": "openapi-typescript http://localhost:8420/openapi.json -o src/types/api-generated.ts"
}
```

**Create validation script:**

```typescript
// File: scripts/validate-types.ts

import { PaymentStatus as BackendPaymentStatus } from '../src/types/api-generated';
import { PaymentStatus as FrontendPaymentStatus } from '../src/types/payment';

// Compile-time check that frontend type is compatible with backend
const _typeCheck: BackendPaymentStatus = 'succeeded' as FrontendPaymentStatus;

console.log('✅ Type validation passed');
```

---

### Task 4.2: Add Runtime Validation

**Create Zod schemas for runtime validation:**

```typescript
// File: apps/frontend/src/validation/paymentSchemas.ts

import { z } from 'zod';

export const PaymentStatusSchema = z.enum([
  'pending',
  'processing',
  'succeeded',
  'failed',
  'canceled',
  'refunded'
]);

export const SubscriptionStatusSchema = z.enum([
  'active',
  'canceled',
  'past_due',
  'unpaid',
  'trialing',
  'incomplete',
  'paused'
]);

export const UserTierSchema = z.enum([
  'free',
  'starter',
  'pro',
  'enterprise'
]);

/**
 * Validate and normalize API response
 */
export function validatePaymentStatus(status: unknown): PaymentStatus {
  try {
    return PaymentStatusSchema.parse(status);
  } catch (error) {
    console.error(`Invalid payment status: ${status}`, error);
    throw new Error(`Invalid payment status received: ${status}`);
  }
}
```

**Use in API client:**

```typescript
// File: apps/frontend/src/services/apiClient.ts

import { validatePaymentStatus } from '../validation/paymentSchemas';

// Wrap API responses
const response = await fetch('/api/payments/123');
const data = await response.json();

// Validate status before using
data.status = validatePaymentStatus(data.status);
```

---

### Task 4.3: Add Backend Response Validation

**Backend: Add response validation middleware**

```python
# File: apps/api/middleware/response_validation.py

from fastapi import Response
from apps.bot.models.payment import PaymentStatus, SubscriptionStatus

async def validate_status_enums(request, call_next):
    """Ensure API responses only contain valid enum values"""
    response = await call_next(request)

    # Add validation logging
    # Could also add Pydantic validation to all response models

    return response
```

---

## 📊 Testing Strategy

### Phase 1 Testing

**Payment Status Tests:**
```typescript
describe('Payment Status Migration', () => {
  it('should accept succeeded status from backend', () => {
    const payment = { status: 'succeeded' };
    expect(isPaymentSuccessful(payment)).toBe(true);
  });

  it('should normalize legacy completed status', () => {
    const normalized = normalizePaymentStatus('completed');
    expect(normalized).toBe('succeeded');
  });

  it('should handle all valid statuses', () => {
    const statuses: PaymentStatus[] = [
      'pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded'
    ];
    statuses.forEach(status => {
      expect(() => validatePaymentStatus(status)).not.toThrow();
    });
  });
});
```

**Subscription Status Tests:**
```typescript
describe('Subscription Status Migration', () => {
  it('should normalize cancelled to canceled', () => {
    const normalized = normalizeSubscriptionStatus('cancelled');
    expect(normalized).toBe('canceled');
  });

  it('should handle all subscription states', () => {
    const sub = { status: 'trialing' as SubscriptionStatus };
    const message = getSubscriptionStatusMessage(sub.status);
    expect(message).toBeDefined();
    expect(message.title).toContain('Trial');
  });
});
```

### Integration Testing

**End-to-end payment flow:**
1. Create Stripe test subscription
2. Verify frontend receives correct status
3. Verify UI displays correct status
4. Test all status transitions

### Monitoring Plan

**Add logging for deprecated values:**
```typescript
// Log whenever old values are used
if (status === 'completed') {
  analytics.track('deprecated_status_used', {
    old_value: 'completed',
    new_value: 'succeeded',
    component: 'PaymentForm'
  });
}
```

---

## 📅 Implementation Timeline

### Week 1: Critical Fixes
- **Day 1-2:** Task 1.1 - Payment status (2 days)
- **Day 3-4:** Task 1.2 - Subscription spelling (2 days)
- **Day 5:** Task 1.3 - Missing statuses (1 day)

### Week 2: Tier Alignment
- **Day 1:** Task 2.1 - Fix test mocks (1 day)
- **Day 2-3:** Task 2.2 - Frontend tier type (2 days)
- **Day 4-5:** Task 2.3 - Update references (2 days)

### Week 3: Status Expansion
- **Day 1-3:** Task 3.1 - User status enum (3 days)
- **Day 4-5:** Task 3.2 - Post status alignment (2 days)

### Week 4: Infrastructure
- **Day 1-2:** Task 4.1 - OpenAPI schema (2 days)
- **Day 3-4:** Task 4.2 - Runtime validation (2 days)
- **Day 5:** Task 4.3 - Backend validation (1 day)

### Continuous
- Testing throughout each phase
- Documentation updates
- Code review and refinement

---

## 🚨 Risk Mitigation

### Rollback Plan

**If payment issues occur:**
1. Keep backward compatibility functions active
2. Revert frontend to accept both old/new values
3. Add feature flag for new status handling

**Feature Flags:**
```typescript
const USE_NEW_STATUS_TYPES = process.env.REACT_APP_NEW_STATUS_TYPES === 'true';

function getPaymentStatus(payment): PaymentStatus {
  if (USE_NEW_STATUS_TYPES) {
    return normalizePaymentStatus(payment.status);
  }
  return payment.status; // Legacy behavior
}
```

### Monitoring Checklist

**During rollout, monitor:**
- [ ] Payment success rate (should not decrease)
- [ ] API error logs (watch for validation errors)
- [ ] Console warnings (deprecated status usage)
- [ ] User reports (incorrect status displays)
- [ ] Stripe webhook processing (status mapping)

---

## ✅ Success Criteria

### Phase 1 Complete When:
- [ ] All payments show `'succeeded'` instead of `'completed'`
- [ ] All subscriptions use `'canceled'` (1 L) consistently
- [ ] UI handles `trialing`, `incomplete`, `unpaid` statuses
- [ ] No breaking changes to existing functionality
- [ ] Integration tests pass

### Phase 2 Complete When:
- [ ] All code uses `starter`/`pro`, no `basic`/`premium`
- [ ] Frontend has centralized `UserTier` type
- [ ] Feature access checks use tier enum
- [ ] Test mocks use correct tier names

### Phase 3 Complete When:
- [ ] User status is 5-state enum, not boolean
- [ ] Post status differences documented
- [ ] Status badges display correctly

### Phase 4 Complete When:
- [ ] OpenAPI type generation works
- [ ] Runtime validation catches invalid statuses
- [ ] No type mismatches in production logs

---

## 📚 Documentation Updates Needed

1. **API Documentation** - Update all status value lists
2. **Frontend README** - Document new type structure
3. **Developer Guide** - Status enum usage examples
4. **Migration Guide** - For other developers on team
5. **Stripe Integration Doc** - Status mapping table
6. **Testing Guide** - How to test status flows

---

## 🔄 Post-Implementation Cleanup (Week 5)

After monitoring for 1-2 weeks:

1. **Remove backward compatibility code** if no issues
2. **Remove console warnings** for deprecated values
3. **Remove feature flags** for new behavior
4. **Archive old type definitions**
5. **Update all documentation** to remove "migration" notes

---

**Prepared by:** AI Assistant
**Review Required:** Team Lead, Backend Lead, Frontend Lead
**Approval Needed Before:** Starting Phase 1 implementation

**Questions?** Refer to SUBSCRIPTION_STATUS_INVENTORY.md for detailed analysis
