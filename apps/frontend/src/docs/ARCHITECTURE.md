# Frontend Architecture Guide

## Overview

This document describes the frontend architecture patterns and conventions used in the AnalyticBot application.

## Directory Structure

```
src/
├── api/                    # API client (unified)
├── features/               # Feature modules (business logic)
├── pages/                  # Route pages (UI orchestration)
├── shared/                 # Shared components & utilities
├── services/               # AI Service Pages (NOTE: these are pages, not services)
├── store/                  # Zustand state slices
├── hooks/                  # Re-exports from features
├── types/                  # Global TypeScript types
└── utils/                  # Global utilities
```

## Pattern: Pages vs Features

### Pages (`src/pages/`)
- **Purpose**: Route-level UI components
- **Contains**: Layout, data fetching orchestration, error/loading states
- **Imports from**: features, shared, store
- **Example**: `pages/channels/index.tsx` - channels list page

### Features (`src/features/`)
- **Purpose**: Business logic, domain-specific components
- **Contains**: Services, hooks, specialized components
- **Self-contained**: Each feature is independent
- **Example**: `features/posts/create/PostCreator.tsx` - post creation logic

### Relationship
```
AppRouter.tsx
    └── pages/channels/index.tsx (UI layer)
            └── features/admin/channels/* (business logic)
            └── store/slices/channels/* (state)
            └── shared/components/* (reusable UI)
```

## Dashboard Variants

| File | Purpose | Usage |
|------|---------|-------|
| `pages/DashboardPage.tsx` | **Main dashboard** | Default route `/` |
| `pages/EnhancedDashboardPage.tsx` | Premium with animations | Feature flag in DashboardPage |
| `pages/MobileResponsiveDashboard.tsx` | Mobile optimized | Used by EnhancedDashboardPage |
| `pages/AdminDashboard.tsx` | Admin panel | Route `/admin` |
| `pages/BotDashboardPage.tsx` | Bot management | Route `/bot/dashboard` |
| `features/dashboard/*` | Dashboard components | Imported by pages |

## AI Services Pages (Naming Caveat)

Files in `src/services/*.tsx` are **PAGE COMPONENTS**, not service classes:
- `ChurnPredictorService.tsx` → Page at `/services/churn-predictor`
- `ContentOptimizerService.tsx` → Page at `/services/content-optimizer`
- `PredictiveAnalyticsService.tsx` → Page at `/services/predictive-analytics`
- `SecurityMonitoringService.tsx` → Page at `/services/security-monitoring`

The actual service **logic** is in `features/ai-services/services/`:
- `churnPredictor.ts` - ChurnPredictorService class
- `contentOptimizer.ts` - ContentOptimizerService class
- etc.

## Component Folder Pattern

Large pages should use the folder pattern:
```
pages/
├── channels/
│   ├── index.tsx              # Main page
│   ├── components/            # Page-specific components
│   │   ├── ChannelCard.tsx
│   │   └── ChannelDialogs.tsx
│   ├── hooks/                 # Page-specific hooks
│   └── types.ts               # Page-specific types
├── MTProtoMonitoringPage/
│   ├── index.tsx              # Main page (~230 lines)
│   ├── components/            # Extracted cards
│   │   ├── SessionHealthCard.tsx
│   │   ├── CollectionProgressCard.tsx
│   │   └── ...
│   ├── types.ts
│   └── utils.ts
```

## State Management

- **Zustand** for global state (`store/slices/`)
- Each slice is domain-specific:
  - `useAuthStore` - Authentication
  - `useChannelStore` - Channels
  - `usePostStore` - Posts
  - `useAnalyticsStore` - Analytics data

## Archived Code

Legacy code is moved to `src/archive/` with date folders:
- `archive/phase1_cleanup_20251128/`
- `archive/phase2_cleanup_20251130/`
- `archive/legacy_*/` - Various legacy modules

## Best Practices

1. **Page size**: Keep pages under 400 lines. Extract to components folder if larger.
2. **Feature independence**: Features should not import from other features directly.
3. **Shared first**: Reusable components go to `shared/components/`.
4. **Type safety**: Use TypeScript interfaces, avoid `any`.
5. **Barrel exports**: Use `index.ts` for clean imports.

## Migration Notes

- `MainDashboard.tsx` - Archived (was wrapper around DashboardPage)
- `MTProtoMonitoringPage.tsx` - Refactored to folder structure
- `.jsx` extensions fixed to use Vite's auto-resolution
