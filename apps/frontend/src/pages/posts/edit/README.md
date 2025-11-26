# Edit Post Module

Edit existing posts functionality.

## Features

- **Edit Content**: Modify post title and content
- **Status Management**: Update post status (draft/published/scheduled)
- **Save Changes**: Persist modifications to backend

## Usage

```tsx
import { EditPostPage } from '@/pages/posts/edit';

// Or via exports
import { EditPostPage } from '@/pages/posts/exports';
```

## Route

- Path: `/posts/:id/edit`
- Extracts `id` from URL params
- Navigates back to posts list on save

## TODO

- Implement actual API integration for saving changes
- Add validation for required fields
- Add unsaved changes warning
