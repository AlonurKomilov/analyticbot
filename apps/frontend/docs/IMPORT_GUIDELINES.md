# Import Guidelines

**Last Updated:** October 26, 2025
**Version:** 1.0.0

## Table of Contents

- [Quick Reference](#quick-reference)
- [Path Aliases](#path-aliases)
- [Import Rules](#import-rules)
- [Barrel Exports](#barrel-exports)
- [Examples](#examples)
- [Common Mistakes](#common-mistakes)
- [Migration Guide](#migration-guide)

---

## Quick Reference

### ✅ DO

```typescript
// Use path aliases
import { AnalyticsDashboard } from '@features/analytics';
import { Button } from '@shared/components/ui';
import { useAuthStore } from '@store';
import { ENV } from '@config';

// Import from barrel exports
import { MetricsCard, GrowthChart } from '@features/analytics';

// Import types with 'type' keyword
import type { User, Channel } from '@/types';
```

### ❌ DON'T

```typescript
// Don't use relative imports across layers
import { AnalyticsDashboard } from '../../features/analytics/components/AnalyticsDashboard';

// Don't import internal implementations
import { AnalyticsDashboard } from '@features/analytics/components/AnalyticsDashboard';

// Don't cross feature boundaries
// In features/payment/
import { UserTable } from '@features/admin'; // ❌ BAD
```

---

## Path Aliases

All path aliases are configured in `tsconfig.json` and `vite.config.ts`.

### Available Aliases

| Alias | Resolves To | Usage |
|-------|-------------|-------|
| `@/*` | `src/*` | Root-level files (contexts, utils, validation) |
| `@features/*` | `src/features/*` | Business features |
| `@shared/*` | `src/shared/*` | Shared infrastructure |
| `@store/*` | `src/store/*` | State management slices |
| `@store` | `src/store/index.ts` | Store exports |
| `@config/*` | `src/config/*` | Configuration files |
| `@theme/*` | `src/theme/*` | Design system |
| `@api/*` | `src/api/*` | API client |
| `@types/*` | `src/types/*` | Type definitions |
| `@pages/*` | `src/pages/*` | Route pages |

### Configuration

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@features/*": ["./src/features/*"],
      "@shared/*": ["./src/shared/*"],
      "@store/*": ["./src/store/*"],
      "@store": ["./src/store/index.ts"],
      "@config/*": ["./src/config/*"],
      "@theme/*": ["./src/theme/*"],
      "@api/*": ["./src/api/*"],
      "@types/*": ["./src/types/*"],
      "@pages/*": ["./src/pages/*"]
    }
  }
}
```

**vite.config.ts:**
```typescript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
    '@features': path.resolve(__dirname, './src/features'),
    '@shared': path.resolve(__dirname, './src/shared'),
    '@store': path.resolve(__dirname, './src/store'),
    '@config': path.resolve(__dirname, './src/config'),
    '@theme': path.resolve(__dirname, './src/theme'),
    '@api': path.resolve(__dirname, './src/api'),
    '@types': path.resolve(__dirname, './src/types'),
    '@pages': path.resolve(__dirname, './src/pages'),
  },
}
```

---

## Import Rules

### Rule 1: Always Use Path Aliases

**❌ Bad:**
```typescript
import { UserTable } from '../../components/UserTable';
import { useAuth } from '../../../contexts/AuthContext';
import { formatDate } from '../../../../utils/formatters';
```

**✅ Good:**
```typescript
import { UserTable } from '@features/admin';
import { useAuth } from '@/contexts/AuthContext';
import { formatDate } from '@shared/utils/formatters';
```

**Why?**
- Easier to read
- Easier to refactor
- No need to count `../` levels
- Works everywhere regardless of nesting

### Rule 2: Import from Barrel Exports

**❌ Bad:**
```typescript
import { AnalyticsDashboard } from '@features/analytics/components/AnalyticsDashboard';
import { MetricsCard } from '@features/analytics/components/MetricsCard';
import { useAnalytics } from '@features/analytics/hooks/useAnalytics';
```

**✅ Good:**
```typescript
import { AnalyticsDashboard, MetricsCard, useAnalytics } from '@features/analytics';
```

**Why?**
- Cleaner imports
- Internal structure can change
- Clear public API

### Rule 3: Features Are Independent

**❌ Bad:**
```typescript
// In features/payment/
import { UserTable } from '@features/admin';
import { AnalyticsChart } from '@features/analytics';
```

**✅ Good:**
```typescript
// In features/payment/
import { DataTable } from '@shared/components/tables';
import { LineChart } from '@shared/components/charts';

// Or if you really need admin functionality:
// Create a shared service/component instead
```

**Why?**
- Features should be decoupled
- Easier to test in isolation
- Can be extracted to separate packages

### Rule 4: Within-Feature Imports Can Be Relative

Within a single feature, relative imports are acceptable:

**✅ Acceptable:**
```typescript
// In features/analytics/components/MetricsCard.tsx
import { useAnalytics } from '../hooks/useAnalytics';
import { formatMetric } from '../utils/formatters';
import type { Metric } from '../types/analytics.types';
```

**✅ Also Good (using alias):**
```typescript
// In features/analytics/components/MetricsCard.tsx
import { useAnalytics } from '@features/analytics/hooks/useAnalytics';
```

**Recommendation:** Use relative imports within features for easier refactoring.

### Rule 5: Use Type Imports

**❌ Bad:**
```typescript
import { User, Channel, Post } from '@/types';
```

**✅ Good:**
```typescript
import type { User, Channel, Post } from '@/types';
```

**Why?**
- Clearer intent
- Better tree-shaking
- TypeScript can optimize imports

---

## Barrel Exports

### What Is a Barrel Export?

A barrel export is an `index.ts` file that re-exports items from multiple files:

```typescript
// features/analytics/index.ts
export { AnalyticsDashboard } from './components/AnalyticsDashboard';
export { MetricsCard } from './components/MetricsCard';
export { GrowthChart } from './components/GrowthChart';
export { useAnalytics } from './hooks/useAnalytics';
export * from './types/analytics.types';
```

### Creating Barrel Exports

**Feature Level:**
```typescript
// features/analytics/index.ts
export { AnalyticsDashboard } from './components/AnalyticsDashboard';
export { MetricsCard } from './components/MetricsCard';
export { useAnalytics } from './hooks/useAnalytics';
```

**Subdirectory Level:**
```typescript
// shared/components/ui/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { Select } from './Select';

// shared/components/index.ts
export * from './ui';
export * from './feedback';
export * from './layout';
```

### Best Practices

✅ **Do:**
- Export only public API
- Keep exports explicit (avoid `export *` unless needed)
- Document exported items

❌ **Don't:**
- Export everything automatically
- Create circular dependencies
- Export internal utilities

---

## Examples

### Importing from Features

```typescript
// ✅ Import from feature public API
import { AnalyticsDashboard, MetricsCard } from '@features/analytics';
import { UserManagement, ChannelManagement } from '@features/admin';
import { PostCreator, PostList } from '@features/posts';
```

### Importing from Shared

```typescript
// ✅ Import shared components
import { Button, Input, Select } from '@shared/components/ui';
import { DataTable, EmptyState } from '@shared/components';
import { useDebounce, useLocalStorage } from '@shared/hooks';
```

### Importing from Store

```typescript
// ✅ Import store slices
import { useAuthStore } from '@store';
import { useAnalyticsStore, useChannelStore } from '@store';

// Usage
const { user, login, logout } = useAuthStore();
const { analytics, fetchAnalytics } = useAnalyticsStore();
```

### Importing Types

```typescript
// ✅ Import types
import type { User, Channel, Post } from '@/types';
import type { AnalyticsData } from '@features/analytics';
import type { ButtonProps } from '@shared/components/ui';
```

### Importing Config

```typescript
// ✅ Import configuration
import { ENV, ROUTES, FEATURES } from '@config';
import { STORAGE_KEYS, API } from '@shared/constants';
```

### Mixed Imports

```typescript
// ✅ Combine imports logically
import { useState, useEffect } from 'react';
import type { User } from '@/types';
import { useAuthStore } from '@store';
import { Button } from '@shared/components/ui';
import { UserProfile } from '@features/auth';
```

---

## Common Mistakes

### Mistake 1: Deep Imports

**❌ Bad:**
```typescript
import { AnalyticsDashboard } from '@features/analytics/components/dashboard/AnalyticsDashboard';
```

**✅ Good:**
```typescript
import { AnalyticsDashboard } from '@features/analytics';
```

### Mistake 2: Relative Imports Across Features

**❌ Bad:**
```typescript
// In features/payment/
import { UserTable } from '../admin/components/UserTable';
```

**✅ Good:**
```typescript
// Extract to shared if needed by multiple features
import { DataTable } from '@shared/components/tables';
```

### Mistake 3: Circular Dependencies

**❌ Bad:**
```typescript
// features/admin/index.ts
export { UserManagement } from './components/UserManagement';

// features/admin/components/UserManagement.tsx
import { AdminLayout } from '@features/admin'; // Circular!
```

**✅ Good:**
```typescript
// features/admin/components/UserManagement.tsx
import { AdminLayout } from '../layout/AdminLayout'; // Direct import
```

### Mistake 4: Importing Everything

**❌ Bad:**
```typescript
import * as Analytics from '@features/analytics';

// Usage
<Analytics.AnalyticsDashboard />
<Analytics.MetricsCard />
```

**✅ Good:**
```typescript
import { AnalyticsDashboard, MetricsCard } from '@features/analytics';

// Usage
<AnalyticsDashboard />
<MetricsCard />
```

---

## Migration Guide

### From Relative to Absolute Imports

**Step 1:** Find all relative imports
```bash
grep -r "from ['\"]\.\./" src --include="*.ts" --include="*.tsx"
```

**Step 2:** Replace with path aliases

Use the automated script:
```bash
./scripts/fix-imports.sh
```

Or manually:
```typescript
// Before
import { Button } from '../../components/Button';

// After
import { Button } from '@shared/components/ui';
```

**Step 3:** Verify
```bash
npm run type-check
npm run build
```

### Creating Barrel Exports

**Step 1:** Create `index.ts` in feature directory

```typescript
// features/analytics/index.ts
export { AnalyticsDashboard } from './components/AnalyticsDashboard';
export { MetricsCard } from './components/MetricsCard';
export { useAnalytics } from './hooks/useAnalytics';
```

**Step 2:** Update imports

```typescript
// Before
import { AnalyticsDashboard } from '@features/analytics/components/AnalyticsDashboard';

// After
import { AnalyticsDashboard } from '@features/analytics';
```

**Step 3:** Verify no errors

```bash
npm run type-check
```

---

## Validation

### Auto-fix with ESLint

Add ESLint rule to enforce path aliases:

```json
{
  "rules": {
    "no-restricted-imports": [
      "error",
      {
        "patterns": ["../*", "./*"]
      }
    ]
  }
}
```

### Pre-commit Hook

```bash
# .husky/pre-commit
npm run type-check
```

---

## Related Documentation

- [Architecture](./ARCHITECTURE.md) - Overall architecture
- [State Management](./STATE_MANAGEMENT.md) - Store patterns
- [Component Guidelines](./COMPONENT_GUIDELINES.md) - Component best practices

---

**Questions?** Contact the frontend team or open an issue.
