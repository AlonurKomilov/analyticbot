# Design Tokens Migration Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Token Categories](#token-categories)
4. [Migration Examples](#migration-examples)
5. [Before & After Comparisons](#before--after-comparisons)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)

---

## Overview

The design tokens system provides a centralized, type-safe way to manage design values across the application. Instead of using inline values or magic numbers, we now use semantic tokens that ensure consistency and make it easier to update designs globally.

### Benefits:
✅ **Consistency**: One source of truth for all design values
✅ **Maintainability**: Change once, update everywhere
✅ **Type Safety**: Full TypeScript support with autocomplete
✅ **Semantic Naming**: Clear, self-documenting token names
✅ **Accessibility**: Built-in WCAG AAA compliant values

---

## Quick Start

### Import Tokens

```typescript
// Import all tokens
import { spacing, colors, shadows, sizing, radius } from '@/theme/tokens';

// Or import specific tokens
import { spacing } from '@/theme/tokens';

// Or import MUI theme
import theme from '@/theme';
```

### Use in Components

```typescript
// Before (inline values)
<Box sx={{ padding: '24px', backgroundColor: '#161b22', borderRadius: '8px' }}>

// After (design tokens)
<Box sx={{
  padding: spacing.lg,
  backgroundColor: colors.background.paper,
  borderRadius: radius.card
}}>
```

---

## Token Categories

### 1. Spacing Tokens (`spacing`)
Use for: padding, margin, gap

| Token | Value | Use Case |
|-------|-------|----------|
| `spacing.xxs` | 4px | Minimal spacing, icon gaps |
| `spacing.xs` | 8px | Compact padding |
| `spacing.sm` | 12px | Small padding, button padding |
| `spacing.md` | 16px | Standard padding |
| `spacing.lg` | 24px | Section padding |
| `spacing.xl` | 32px | Large section padding |
| `spacing.xxl` | 48px | Major section spacing |

**Semantic Tokens:**
- `spacing.section` - Between major sections (32px)
- `spacing.component` - Between components (16px)
- `spacing.element` - Between elements (8px)
- `spacing.inline` - Between inline elements (4px)

### 2. Sizing Tokens (`sizing`)
Use for: width, height, minHeight

| Category | Token | Value | Use Case |
|----------|-------|-------|----------|
| Touch Targets | `sizing.touchTarget.min` | 44px | Minimum WCAG AAA |
| Touch Targets | `sizing.touchTarget.comfortable` | 48px | Comfortable size |
| Inputs | `sizing.input.medium` | 44px | Standard input |
| Buttons | `sizing.button.medium` | 44px | Standard button |
| Icons | `sizing.icon.md` | 24px | Standard icon |
| Dialogs | `sizing.dialog.md` | 800px | Standard dialog |

### 3. Color Tokens (`colors`)
Use for: color, backgroundColor, borderColor

```typescript
// Background colors
colors.background.default  // #0d1117 - Main background
colors.background.paper    // #161b22 - Card backgrounds
colors.background.elevated // #1c2128 - Elevated surfaces

// Text colors
colors.text.primary        // #f0f6fc - Primary text (15:1 contrast)
colors.text.secondary      // #8b949e - Secondary text
colors.text.disabled       // #484f58 - Disabled text

// Border colors
colors.border.default      // #30363d - Standard borders
colors.border.focus        // #58a6ff - Focus states

// Semantic colors with background variants
colors.success.main        // #3fb950
colors.success.bg          // rgba(63, 185, 80, 0.1) - For backgrounds
colors.error.main          // #f85149
colors.error.bg            // rgba(248, 81, 73, 0.1)
```

### 4. Shadow Tokens (`shadows`)
Use for: boxShadow

| Token | Use Case |
|-------|----------|
| `shadows.card` | Cards, panels |
| `shadows.dialog` | Dialogs, modals |
| `shadows.dropdown` | Dropdowns, menus |
| `shadows.focus` | Focus rings |

### 5. Border Radius Tokens (`radius`)
Use for: borderRadius

| Token | Value | Use Case |
|-------|-------|----------|
| `radius.button` | 6px | Buttons |
| `radius.input` | 6px | Input fields |
| `radius.card` | 8px | Cards |
| `radius.dialog` | 12px | Dialogs |
| `radius.badge` | 9999px | Badges, pills |

### 6. Animation Tokens (`animation`)
Use for: transition, animation

```typescript
// Durations
animation.duration.fast    // 150ms
animation.duration.normal  // 250ms
animation.duration.slow    // 350ms

// Pre-built transitions
animation.transition.fast  // 'all 150ms cubic-bezier(0.4, 0, 0.2, 1)'
```

---

## Migration Examples

### Example 1: Card Component

**Before:**
```typescript
<Paper
  sx={{
    padding: '24px',
    margin: '16px',
    backgroundColor: '#161b22',
    borderRadius: '8px',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.4)',
  }}
>
```

**After:**
```typescript
<Paper
  sx={{
    padding: spacing.lg,
    margin: spacing.md,
    backgroundColor: colors.background.paper,
    borderRadius: radius.card,
    boxShadow: shadows.card,
  }}
>
```

### Example 2: Button Component

**Before:**
```typescript
<Button
  sx={{
    padding: '12px 16px',
    minHeight: '44px',
    borderRadius: '6px',
    backgroundColor: '#58a6ff',
    color: '#ffffff',
    transition: 'all 150ms',
  }}
>
```

**After:**
```typescript
<Button
  sx={{
    padding: `${spacing.sm} ${spacing.md}`,
    minHeight: sizing.button.medium,
    borderRadius: radius.button,
    backgroundColor: colors.primary.main,
    color: colors.primary.contrast,
    transition: animation.transition.fast,
  }}
>
```

### Example 3: Dialog Component

**Before:**
```typescript
<Dialog
  sx={{
    '& .MuiDialog-paper': {
      maxWidth: '800px',
      padding: '32px',
      borderRadius: '12px',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
    }
  }}
>
```

**After:**
```typescript
<Dialog
  sx={{
    '& .MuiDialog-paper': {
      maxWidth: sizing.dialog.md,
      padding: spacing.xl,
      borderRadius: radius.dialog,
      boxShadow: shadows.dialog,
    }
  }}
>
```

### Example 4: Alert/Notification

**Before:**
```typescript
<Alert
  sx={{
    padding: '16px',
    marginBottom: '16px',
    borderRadius: '6px',
    backgroundColor: 'rgba(63, 185, 80, 0.1)',
    color: '#3fb950',
    border: '1px solid #3fb950',
  }}
>
```

**After:**
```typescript
<Alert
  sx={{
    padding: spacing.md,
    marginBottom: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.success.bg,
    color: colors.success.main,
    border: `1px solid ${colors.success.main}`,
  }}
>
```

### Example 5: Form Field

**Before:**
```typescript
<TextField
  sx={{
    '& .MuiOutlinedInput-root': {
      height: '44px',
      padding: '0 16px',
      borderRadius: '6px',
      backgroundColor: '#161b22',
      '&:hover': {
        borderColor: '#58a6ff',
      },
      '&.Mui-focused': {
        borderColor: '#58a6ff',
        boxShadow: '0 0 0 3px rgba(88, 166, 255, 0.3)',
      }
    }
  }}
/>
```

**After:**
```typescript
<TextField
  sx={{
    '& .MuiOutlinedInput-root': {
      height: sizing.input.medium,
      padding: `0 ${spacing.md}`,
      borderRadius: radius.input,
      backgroundColor: colors.background.paper,
      '&:hover': {
        borderColor: colors.border.focus,
      },
      '&.Mui-focused': {
        borderColor: colors.border.focus,
        boxShadow: shadows.focus,
      }
    }
  }}
/>
```

---

## Before & After Comparisons

### Full Component Migration

**Before (UserManagement.tsx - Inline Values):**
```typescript
const UserManagement: React.FC = () => {
  return (
    <Box sx={{ padding: '24px' }}>
      <Paper sx={{
        padding: '24px',
        backgroundColor: '#161b22',
        borderRadius: '8px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.4)',
      }}>
        <Typography sx={{
          fontSize: '1.5rem',
          fontWeight: 600,
          marginBottom: '16px',
          color: '#f0f6fc',
        }}>
          User Management
        </Typography>

        <Box sx={{
          display: 'flex',
          gap: '16px',
          marginBottom: '24px',
        }}>
          <TextField
            sx={{
              '& .MuiOutlinedInput-root': {
                height: '44px',
                backgroundColor: '#0d1117',
                borderRadius: '6px',
              }
            }}
          />
          <Button
            sx={{
              padding: '12px 16px',
              minHeight: '44px',
              borderRadius: '6px',
              backgroundColor: '#58a6ff',
              color: '#ffffff',
            }}
          >
            Search
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};
```

**After (UserManagement.tsx - Design Tokens):**
```typescript
import { spacing, colors, radius, shadows, sizing, typography } from '@/theme/tokens';

const UserManagement: React.FC = () => {
  return (
    <Box sx={{ padding: spacing.lg }}>
      <Paper sx={{
        padding: spacing.lg,
        backgroundColor: colors.background.paper,
        borderRadius: radius.card,
        boxShadow: shadows.card,
      }}>
        <Typography sx={{
          fontSize: typography.fontSize.xxl,
          fontWeight: typography.fontWeight.semibold,
          marginBottom: spacing.md,
          color: colors.text.primary,
        }}>
          User Management
        </Typography>

        <Box sx={{
          display: 'flex',
          gap: spacing.md,
          marginBottom: spacing.lg,
        }}>
          <TextField
            sx={{
              '& .MuiOutlinedInput-root': {
                height: sizing.input.medium,
                backgroundColor: colors.background.default,
                borderRadius: radius.input,
              }
            }}
          />
          <Button
            sx={{
              padding: `${spacing.sm} ${spacing.md}`,
              minHeight: sizing.button.medium,
              borderRadius: radius.button,
              backgroundColor: colors.primary.main,
              color: colors.primary.contrast,
            }}
          >
            Search
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};
```

---

## Best Practices

### ✅ DO

1. **Always use semantic tokens first**
   ```typescript
   // Good
   padding: spacing.section  // Clear intent

   // Avoid
   padding: spacing.xl       // Less clear
   ```

2. **Use the right token category**
   ```typescript
   // Good
   minHeight: sizing.button.medium

   // Bad
   minHeight: '44px'
   ```

3. **Combine tokens for complex values**
   ```typescript
   padding: `${spacing.sm} ${spacing.md}` // Vertical/Horizontal
   ```

4. **Use color backgrounds for semantic states**
   ```typescript
   backgroundColor: colors.success.bg  // For success messages
   ```

### ❌ DON'T

1. **Don't mix tokens and hardcoded values**
   ```typescript
   // Bad
   sx={{ padding: spacing.md, margin: '20px' }}

   // Good
   sx={{ padding: spacing.md, margin: spacing.lg }}
   ```

2. **Don't use theme.spacing() with tokens**
   ```typescript
   // Bad
   sx={{ padding: theme.spacing(3) }}

   // Good
   sx={{ padding: spacing.lg }}
   ```

3. **Don't create custom variations inline**
   ```typescript
   // Bad
   sx={{ padding: '18px' }} // Not in system

   // Good - Use closest token
   sx={{ padding: spacing.md }} // 16px
   ```

---

## Common Patterns

### Pattern 1: Card with Header

```typescript
<Paper sx={{
  padding: spacing.lg,
  backgroundColor: colors.background.paper,
  borderRadius: radius.card,
  boxShadow: shadows.card,
}}>
  <Typography sx={{
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.semibold,
    marginBottom: spacing.md,
  }}>
    Card Title
  </Typography>

  <Box sx={{ gap: spacing.element }}>
    {/* Content */}
  </Box>
</Paper>
```

### Pattern 2: Action Bar

```typescript
<Box sx={{
  display: 'flex',
  gap: spacing.md,
  padding: spacing.md,
  backgroundColor: colors.background.elevated,
  borderRadius: radius.md,
}}>
  <TextField sx={{ flex: 1 }} />
  <Button sx={{ minHeight: sizing.button.medium }}>Search</Button>
</Box>
```

### Pattern 3: Status Badge

```typescript
<Chip
  label="Active"
  sx={{
    backgroundColor: colors.success.bg,
    color: colors.success.main,
    borderRadius: radius.badge,
    height: sizing.touchTarget.min,
    fontSize: typography.fontSize.sm,
  }}
/>
```

### Pattern 4: Modal Dialog

```typescript
<Dialog
  sx={{
    '& .MuiDialog-paper': {
      maxWidth: sizing.dialog.md,
      padding: spacing.xl,
      borderRadius: radius.dialog,
      boxShadow: shadows.dialog,
      backgroundColor: colors.background.paper,
    }
  }}
>
  <DialogTitle sx={{
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.semibold,
    padding: 0,
    marginBottom: spacing.lg,
  }}>
    Dialog Title
  </DialogTitle>

  <DialogContent sx={{ padding: 0, marginBottom: spacing.lg }}>
    {/* Content */}
  </DialogContent>

  <DialogActions sx={{
    padding: 0,
    gap: spacing.sm,
  }}>
    <Button>Cancel</Button>
    <Button variant="contained">Confirm</Button>
  </DialogActions>
</Dialog>
```

---

## TypeScript Support

All tokens are fully typed with TypeScript:

```typescript
// Autocomplete works
spacing.       // Shows: xxs, xs, sm, md, lg, xl, xxl, section, component, element, inline
colors.text.   // Shows: primary, secondary, disabled, inverse
sizing.button. // Shows: small, medium, large
```

---

## Migration Checklist

- [ ] Import design tokens in component
- [ ] Replace hardcoded padding/margin with `spacing.*`
- [ ] Replace hardcoded colors with `colors.*`
- [ ] Replace hardcoded sizes with `sizing.*`
- [ ] Replace hardcoded shadows with `shadows.*`
- [ ] Replace hardcoded border-radius with `radius.*`
- [ ] Replace hardcoded transitions with `animation.*`
- [ ] Test component renders correctly
- [ ] Verify accessibility (touch targets, contrast)
- [ ] Remove unused imports

---

## Next Steps

After migrating to design tokens:
1. **Extract Base Components** - Create reusable components using tokens
2. **Refactor God Components** - Break down large components into smaller, token-based components
3. **Create Component Library** - Build a consistent component library with tokens
4. **Set up Linting** - Add ESLint rules to enforce token usage

---

## Questions?

- Check `theme/tokens.ts` for full token reference
- See `theme/index.ts` for exports
- Review existing components for examples
- Ask the team for token suggestions
