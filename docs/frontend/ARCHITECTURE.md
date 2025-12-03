# Frontend Architecture

**Last Updated:** October 26, 2025
**Version:** 1.0.0
**Status:** Phase 3 Complete ✅

## Table of Contents

- [Overview](#overview)
- [Architecture Principles](#architecture-principles)
- [Directory Structure](#directory-structure)
- [Feature Structure](#feature-structure)
- [Layer Responsibilities](#layer-responsibilities)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Related Documentation](#related-documentation)

---

## Overview

This frontend follows a **feature-first architecture** inspired by:
- **Domain-Driven Design (DDD)** - Business logic organized by domain
- **Feature-Sliced Design (FSD)** - Features as first-class citizens
- **Clean Architecture** - Clear separation of concerns
- **SOLID Principles** - Maintainable, testable code

### Key Benefits

✅ **High Cohesion** - Related code stays together
✅ **Low Coupling** - Features are independent
✅ **Scalability** - Easy to add new features
✅ **Testability** - Clear boundaries, easy to mock
✅ **Team Collaboration** - Multiple devs can work without conflicts

---

## Architecture Principles

### 1. Feature-First Organization

Code is organized by **business features** (what the app does), not by **technical layers** (how it's built).

```
❌ Layer-First (OLD)          ✅ Feature-First (NEW)
components/                   features/
  UserTable.tsx                 admin/
  ChannelList.tsx                 components/
  Analytics.tsx                      UserTable.tsx
hooks/                               ChannelList.tsx
  useUsers.ts                      hooks/
  useChannels.ts                     useUsers.ts
services/                          services/
  userService.ts                     userService.ts
  channelService.ts                analytics/
                                    components/
                                      AnalyticsDashboard.tsx
                                    hooks/
                                      useAnalytics.ts
```

### 2. Dependency Direction

Dependencies flow **inward** toward business logic:

```
┌─────────────────────────────────────┐
│           Pages (Routes)            │ ← Thin wrappers
├─────────────────────────────────────┤
│          Features (Business)        │ ← Core logic
├─────────────────────────────────────┤
│      Shared (Infrastructure)        │ ← Reusable utils
├─────────────────────────────────────┤
│      Store (State Management)       │ ← Global state
└─────────────────────────────────────┘
```

### 3. Import Rules

- ✅ Features can import from **shared** and **store**
- ✅ Shared can import from **theme** and **config**
- ✅ Pages can import from **features** and **shared**
- ❌ Features **cannot** import from other features
- ❌ Shared **cannot** import from features
- ❌ Store **cannot** import from features

---

## Directory Structure

```
src/
├── features/           # Business Features (11 domains)
│   ├── admin/         # User & channel management
│   ├── analytics/     # Analytics dashboards & insights
│   ├── ai-services/   # AI-powered tools
│   ├── alerts/        # Notification system
│   ├── auth/          # Authentication & authorization
│   ├── dashboard/     # Main dashboard components
│   ├── payment/       # Subscription & billing
│   ├── posts/         # Content creation & management
│   ├── protection/    # Content protection features
│   └── ...
│
├── shared/            # Shared Infrastructure
│   ├── components/   # Reusable UI components
│   │   ├── ui/       # Basic UI elements (buttons, inputs)
│   │   ├── layout/   # Layout components (header, sidebar)
│   │   ├── feedback/ # Loading, errors, empty states
│   │   ├── charts/   # Chart components
│   │   ├── tables/   # Data table components
│   │   └── ...
│   ├── hooks/        # Shared React hooks
│   ├── services/     # API services & utilities
│   │   ├── api/      # API client
│   │   ├── export/   # Export services
│   │   └── validation/ # Validators
│   ├── utils/        # Helper functions
│   └── constants/    # Shared constants
│
├── store/             # Global State (Zustand)
│   ├── slices/       # State slices by domain
│   │   ├── analytics.ts
│   │   ├── auth.ts
│   │   ├── channels.ts
│   │   ├── media.ts
│   │   ├── posts.ts
│   │   └── ui.ts
│   └── index.ts      # Store exports
│
├── theme/             # Design System
│   ├── designTokens.ts
│   ├── spacingSystem.ts
│   └── index.ts
│
├── config/            # Application Configuration
│   ├── env.ts        # Environment variables
│   ├── features.ts   # Feature flags
│   ├── routes.ts     # Route definitions
│   └── index.ts
│
├── types/             # TypeScript Type Definitions
│   ├── api.ts        # API types
│   ├── models.ts     # Domain models
│   ├── components.ts # Component prop types
│   ├── store.ts      # Store types
│   ├── payment.ts    # Payment types
│   ├── subscription.ts # Subscription types
│   └── index.ts      # Type exports
│
├── pages/             # Route Pages (Thin Wrappers)
│   ├── DashboardPage.tsx
│   ├── AnalyticsPage.tsx
│   ├── AdminDashboard.tsx
│   └── ...
│
├── api/               # API Client
│   ├── client.ts     # Unified API client
│   └── index.ts
│
├── contexts/          # React Contexts
│   └── AuthContext.tsx
│
├── utils/             # Root-level utilities
│   ├── formatters.ts
│   ├── errorHandler.ts
│   └── ...
│
├── validation/        # Validation schemas
│   ├── schemas.ts
│   └── apiValidators.ts
│
└── __mocks__/         # Test mocks
    ├── api/
    ├── services/
    └── constants.ts
```

---

## Feature Structure

Each feature is **self-contained** with all necessary code:

```
features/analytics/
├── components/          # Feature-specific components
│   ├── AnalyticsDashboard.tsx
│   ├── MetricsCard.tsx
│   ├── GrowthChart.tsx
│   └── ...
│
├── hooks/              # Feature-specific hooks
│   ├── useAnalytics.ts
│   ├── useRealTimeAnalytics.ts
│   └── ...
│
├── services/           # Feature-specific services
│   ├── analyticsService.ts
│   ├── calculations.ts
│   └── ...
│
├── types/              # Feature-specific types
│   └── analytics.types.ts
│
├── utils/              # Feature-specific utilities
│   └── chartHelpers.ts
│
├── __tests__/          # Feature tests
│   ├── AnalyticsDashboard.test.tsx
│   └── calculations.test.ts
│
└── index.ts            # Public API (Barrel Export)
```

### Feature Public API

Each feature exports a **public API** via `index.ts`:

```typescript
// features/analytics/index.ts
export { AnalyticsDashboard } from './components/AnalyticsDashboard';
export { MetricsCard } from './components/MetricsCard';
export { useAnalytics } from './hooks/useAnalytics';
export * from './types/analytics.types';
```

**Why?**
- ✅ Encapsulation - Internal structure can change
- ✅ Clear API - Only expose what's needed
- ✅ Easy refactoring - Update imports in one place

---

## Layer Responsibilities

### Features Layer

**Responsibility:** Business logic, feature-specific components, domain rules

**Contains:**
- Feature components (e.g., `AnalyticsDashboard`, `UserManagement`)
- Feature hooks (e.g., `useAnalytics`, `useAdminAPI`)
- Feature services (e.g., `analyticsService`, `paymentService`)
- Feature types and utilities

**Rules:**
- Must be self-contained
- Cannot depend on other features
- Can use shared infrastructure
- Can use global state (store)

### Shared Layer

**Responsibility:** Reusable infrastructure, generic components

**Contains:**
- UI components (e.g., `Button`, `DataTable`, `EmptyState`)
- Generic hooks (e.g., `useDebounce`, `useLocalStorage`)
- API client and services
- Utilities and helpers

**Rules:**
- Must be generic and reusable
- Cannot depend on features
- Cannot contain business logic

### Store Layer

**Responsibility:** Global state management

**Contains:**
- Zustand slices (e.g., `auth`, `channels`, `posts`)
- State actions and selectors
- Persistence middleware

**Rules:**
- One slice per domain
- Actions co-located with state
- No business logic (delegate to services)

### Pages Layer

**Responsibility:** Route configuration, **thin wrappers**

**Contains:**
- Page components (one per route)
- Route guards
- Layout composition

**Rules:**
- Should be <50 lines of code
- Delegate logic to features
- Only handle routing concerns

**Example:**

```typescript
// ✅ GOOD - Thin wrapper
export default function AnalyticsPage() {
  return <AnalyticsDashboard />;
}

// ❌ BAD - Business logic in page
export default function AnalyticsPage() {
  const [data, setData] = useState();
  const fetchData = async () => { /* ... */ };
  // ... 200 lines of code
}
```

---

## Data Flow

### 1. User Interaction

```
User clicks button
  ↓
Component handles event
  ↓
Dispatches store action OR calls service
  ↓
Service makes API call
  ↓
Store updates state
  ↓
Component re-renders with new data
```

### 2. Data Flow Diagram

```
┌────────────┐
│   Pages    │ Routes & layout
└─────┬──────┘
      ↓
┌────────────┐
│  Features  │ Business logic
└─────┬──────┘
      ↓
┌────────────┐
│   Store    │ ← State management
└─────┬──────┘
      ↓
┌────────────┐
│  Services  │ ← API calls
└─────┬──────┘
      ↓
┌────────────┐
│  API Client│ ← HTTP requests
└────────────┘
```

---

## Design Patterns

### 1. Barrel Exports

Centralize exports in `index.ts` files:

```typescript
// features/analytics/index.ts
export { AnalyticsDashboard } from './components/AnalyticsDashboard';
export { MetricsCard } from './components/MetricsCard';

// Usage
import { AnalyticsDashboard, MetricsCard } from '@features/analytics';
```

### 2. Custom Hooks

Encapsulate logic in reusable hooks:

```typescript
// features/analytics/hooks/useAnalytics.ts
export function useAnalytics() {
  const { period } = useAnalyticsStore();
  const { data, loading, error } = useQuery(/* ... */);
  return { data, loading, error };
}
```

### 3. Service Layer

Separate API logic from components:

```typescript
// features/analytics/services/analyticsService.ts
export const analyticsService = {
  getOverview: (period) => apiClient.get(`/analytics/overview`, { period }),
  getGrowth: (period) => apiClient.get(`/analytics/growth`, { period }),
};
```

### 4. Compound Components

Build composable component APIs:

```typescript
<DataTable>
  <DataTable.Header />
  <DataTable.Body />
  <DataTable.Pagination />
</DataTable>
```

---

## Related Documentation

- [Import Guidelines](./IMPORT_GUIDELINES.md) - Path aliases & import rules
- [State Management](./STATE_MANAGEMENT.md) - Zustand store patterns
- [Component Guidelines](./COMPONENT_GUIDELINES.md) - Component best practices
- [Testing Guide](./TESTING.md) - Testing strategies

---

## Migration History

### Phase 3 Refactoring (October 2025)

**Before:** Layer-first architecture
```
components/ (269 files)
hooks/ (15 files)
services/ (23 files)
stores/ (6 files)
```

**After:** Feature-first architecture
```
features/ (11 domains, organized)
shared/ (infrastructure)
store/slices/ (6 slices)
pages/ (thin wrappers)
```

**Results:**
- ✅ 0 TypeScript errors
- ✅ Build time: ~44s
- ✅ Better code organization
- ✅ Easier navigation
- ✅ Improved maintainability

---

**Questions?** See [FAQ.md](./FAQ.md) or contact the team.
