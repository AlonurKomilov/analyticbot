# Post Details Module

View detailed information about individual posts.

## Features

- **Full Content View**: Display complete post content
- **Metadata Display**: Author, date, views, status
- **Status Indicator**: Visual chip showing post status
- **Edit Action**: Navigate to edit page

## Usage

```tsx
import { PostDetailsPage } from '@/pages/posts/details';

// Or via exports
import { PostDetailsPage } from '@/pages/posts/exports';
```

## Route

- Path: `/posts/:id`
- Extracts `id` from URL params
- Provides "Back to Posts" navigation
- Provides "Edit Post" action button

## TODO

- Implement actual API integration to fetch post data
- Add loading state
- Add error handling
- Add delete functionality
