# ScheduledPostsList Migration

## What Changed

The `ScheduledPostsList` component has been migrated from a single-file component to a modular architecture in `pages/ScheduledPostsPage/`.

## New Location

```
pages/ScheduledPostsPage/
├── components/
│   ├── ScheduledPostsList.tsx    ← NEW modular version
│   ├── ScheduledPostCard.tsx     ← Single post display
│   ├── LoadingState.tsx
│   ├── ErrorAlert.tsx
│   └── EmptyState.tsx
└── hooks/
    ├── useScheduledPosts.ts
    └── usePostActions.ts
```

## For Dashboard Usage

The import path **remains the same**:

```tsx
import { ScheduledPostsList } from '@features/posts';
```

This now automatically uses the NEW modular component from `pages/ScheduledPostsPage/components/ScheduledPostsList`.

## Benefits

✅ Better UX (full text preview, file badges)
✅ Modular architecture (small, focused components)
✅ Loading/error states
✅ Type safe
✅ Reusable across pages

## Old File

The old implementation is preserved as:
- `ScheduledPostsList.old.tsx` (for reference)

## Migration Date

October 29, 2025
