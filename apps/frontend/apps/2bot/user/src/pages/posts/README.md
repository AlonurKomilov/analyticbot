# Posts Feature Module

**Microservice-style architecture** for post management functionality.

## 📁 Structure

```
pages/posts/
├── index.tsx                      # Main PostsPage (entry point)
├── exports.ts                     # Public API exports
├── README.md                      # This documentation
├── REFACTORING_SUMMARY.md         # Refactoring details
│
├── create/                        # Post creation module
│   ├── index.ts                   # Module exports
│   └── CreatePostPage.tsx         # Post creation page
│
├── edit/                          # Post editing module
│   ├── index.ts                   # Module exports
│   └── EditPostPage.tsx           # Post editing page
│
├── details/                       # Post details module
│   ├── index.ts                   # Module exports
│   └── PostDetailsPage.tsx        # Post details/view page
│
├── types/
│   └── Post.ts                    # TypeScript type definitions
│
├── components/
│   ├── PostsTable.tsx             # Table view with column management
│   ├── PostsGrid.tsx              # Card-based grid view
│   ├── PostsFilters.tsx           # Channel filter & search
│   └── PostsViewControls.tsx      # View mode toggle & column controls
│
└── hooks/
    ├── usePosts.ts                # Data fetching hook
    ├── usePostFilters.ts          # Filter state management
    └── useColumnVisibility.ts     # Column visibility management
```

## 🎯 Design Principles

### Single Responsibility
Each file has ONE clear purpose:
- **index.tsx**: Main posts list page orchestration
- **create/CreatePostPage.tsx**: Post creation workflow with media upload
- **edit/EditPostPage.tsx**: Post editing interface
- **details/PostDetailsPage.tsx**: View individual post details
- **PostsTable.tsx**: Table view rendering
- **PostsGrid.tsx**: Grid/card view rendering
- **PostsFilters.tsx**: Channel selector & search UI
- **PostsViewControls.tsx**: View mode toggle & column management
- **usePosts.ts**: Posts data fetching logic
- **usePostFilters.ts**: Filter state (channel, search, pagination)
- **useColumnVisibility.ts**: Column visibility state

### Self-Contained
- All posts-related code lives in this directory
- External dependencies imported via `@/` aliases
- Internal imports use relative paths (`./components/...`)

### Clean Imports
```tsx
// Import complete pages:
import { PostsPage } from '@/pages/posts';
import { CreatePostPage } from '@/pages/posts/create';
import { EditPostPage } from '@/pages/posts/edit';
import { PostDetailsPage } from '@/pages/posts/details';

// Or via exports file:
import { PostsPage, CreatePostPage, EditPostPage, PostDetailsPage } from '@/pages/posts/exports';

// Import specific components/hooks:
import { usePosts, PostsTable, PostsGrid } from '@/pages/posts/exports';
```

## 📄 Pages

### PostsPage (index.tsx)
Main posts listing page with table/grid views, filtering, and search.

**Features:**
- View all posts from channels
- Filter by channel
- Search by message ID or content
- Toggle between table and grid views
- Column visibility management
- Pagination

### CreatePostPage
Post creation page with media management.

**Features:**
- Post content editor
- Channel selection
- Media upload (drag & drop)
- Telegram storage browser
- Schedule for later option
- Inline buttons (optional)

### EditPostPage
Edit existing posts.

**Features:**
- Edit post content
- Update status (draft/published/scheduled)
- Save changes

### PostDetailsPage
View detailed information about a post.

**Features:**
- View full post content
- Post metadata (author, date, views)
- Status indicator
- Edit button (navigates to EditPostPage)

## 🔧 Components

### PostsTable
Table view with conditional column rendering.

**Props:**
```typescript
{
  posts: Post[];
  visibleColumns: VisibleColumns;
  formatDate: (date: string) => string;
  getTelegramLink: (post: Post) => string;
}
```

### PostsGrid
Card-based grid view for posts.

**Props:**
```typescript
{
  posts: Post[];
  formatDate: (date: string) => string;
  getTelegramLink: (post: Post) => string;
}
```

### PostsFilters
Filter and search controls.

**Props:**
```typescript
{
  selectedChannel: number | 'all';
  searchQuery: string;
  total: number;
  channels: Channel[];
  onChannelChange: (channel: number | 'all') => void;
  onSearchChange: (query: string) => void;
  onSearchClear: () => void;
}
```

### PostsViewControls
View mode toggle and column management menu.

**Props:**
```typescript
{
  viewMode: ViewMode;
  visibleColumns: VisibleColumns;
  visibleCount: number;
  totalCount: number;
  onViewModeChange: (mode: ViewMode) => void;
  onColumnToggle: (column: keyof VisibleColumns) => void;
  onShowAllColumns: () => void;
  onHideAllColumns: () => void;
}
```

## 🪝 Hooks

### usePosts
Fetches posts data with automatic refetch on filter changes.

**Usage:**
```typescript
const { posts, isLoading, error, total, totalPages, refetch } = usePosts(filters);
```

**Returns:**
```typescript
{
  posts: Post[];
  isLoading: boolean;
  error: string | null;
  total: number;
  totalPages: number;
  refetch: () => Promise<void>;
}
```

### usePostFilters
Manages filter state (channel, search, pagination).

**Usage:**
```typescript
const {
  selectedChannel,
  searchQuery,
  page,
  setSelectedChannel,
  setSearchQuery,
  setPage,
  resetFilters
} = usePostFilters();
```

**Features:**
- Auto-reset page to 1 when changing filters
- Convenient reset function

### useColumnVisibility
Manages table column visibility state.

**Usage:**
```typescript
const {
  visibleColumns,
  toggleColumn,
  showAllColumns,
  hideAllColumns,
  visibleCount,
  totalCount
} = useColumnVisibility();
```

**Features:**
- Toggle individual columns
- Show/hide all columns
- Track visible column count

## 📦 Types

### Post
```typescript
interface Post {
  id: number;
  channel_id: number;
  msg_id: number;
  date: string;
  text: string;
  created_at: string;
  updated_at: string;
  metrics?: PostMetrics;
  channel_name?: string;
  channel_username?: string;
}
```

### PostMetrics
```typescript
interface PostMetrics {
  views: number;
  forwards: number;
  replies_count: number;
  reactions_count: number;
  snapshot_time?: string;
}
```

### VisibleColumns
```typescript
interface VisibleColumns {
  channel: boolean;
  messageId: boolean;
  content: boolean;
  views: boolean;
  forwards: boolean;
  replies: boolean;
  reactions: boolean;
  telegram: boolean;
  date: boolean;
}
```

## 🚀 Usage Example

```tsx
import React from 'react';
import { PostsPage, CreatePostPage, EditPostPage } from '@/pages/posts';

// Use the complete pages
function App() {
  return (
    <>
      <PostsPage />
      <CreatePostPage />
      <EditPostPage />
    </>
  );
}

// Or build custom views with exported components
import { usePosts, usePostFilters, PostsTable } from '@/pages/posts/exports';

function CustomPostsView() {
  const filters = usePostFilters();
  const { posts, isLoading } = usePosts(filters);

  return (
    <PostsTable
      posts={posts}
      visibleColumns={{ /* ... */ }}
      formatDate={(date) => new Date(date).toLocaleString()}
      getTelegramLink={(post) => `https://t.me/${post.channel_username}/${post.msg_id}`}
    />
  );
}
```

## ✅ Benefits

1. **Maintainable**: Small, focused files (50-150 lines each)
2. **Testable**: Easy to unit test isolated components/hooks
3. **Reusable**: Components and hooks can be used independently
4. **Type-Safe**: Full TypeScript support with exported types
5. **Scalable**: Easy to add new features without modifying existing code
6. **Discoverable**: Clear structure makes navigation easy

## 🔄 Comparison to Old Structure

**Before** (Multiple scattered files):
```
pages/
├── PostsPage.tsx (632 lines - God Object)
├── CreatePostPage.tsx (122 lines)
├── EditPostPage.tsx (96 lines)
└── PostDetailsPage.tsx (68 lines)
```

**Issues:**
- ❌ Scattered across pages folder
- ❌ No clear module boundary
- ❌ PostsPage was a God Object (632 lines)
- ❌ Hard to find related functionality
- ❌ No shared components or hooks

**After** (Organized microservice module):
```
pages/posts/
├── index.tsx (175 lines)
├── create/
│   ├── index.ts
│   └── CreatePostPage.tsx (122 lines)
├── edit/
│   ├── index.ts
│   └── EditPostPage.tsx (96 lines)
├── details/
│   ├── index.ts
│   └── PostDetailsPage.tsx (68 lines)
├── components/ (4 focused components)
├── hooks/ (3 focused hooks)
├── types/ (clean type definitions)
└── exports.ts (public API)
```

**Benefits:**
- ✅ All post functionality in one place
- ✅ Clear module boundaries
- ✅ Reusable components and hooks
- ✅ Small, focused files
- ✅ Easy to find and modify

## 🎨 Architecture Diagram

```
┌─────────────────────────────────────────┐
│           PostsPage (index.tsx)         │
│  - Page orchestration                   │
│  - Layout structure                     │
└─────────────────────────────────────────┘
           │
           ├─── usePostFilters() ────────── Filter state
           ├─── usePosts(filters) ────────── Data fetching
           ├─── useColumnVisibility() ────── Column state
           │
           ├─── <PostsFilters />  ────────── Channel & search UI
           ├─── <PostsViewControls /> ────── View toggle & columns
           ├─── <PostsTable />  ──────────── Table view
           └─── <PostsGrid />  ───────────── Card grid view
```

## 📝 Development Guidelines

1. **Adding a new component**: Create in `components/` folder
2. **Adding a new hook**: Create in `hooks/` folder
3. **Adding new types**: Update `types/Post.ts`
4. **Exporting new features**: Update `exports.ts`
5. **Keep components pure**: Pass data via props, avoid direct API calls
6. **Keep hooks focused**: One responsibility per hook
7. **Document changes**: Update this README when structure changes
