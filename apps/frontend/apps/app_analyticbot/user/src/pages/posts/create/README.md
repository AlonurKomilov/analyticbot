# Create Post Module

Post creation page with comprehensive media management.

## Features

- **Post Editor**: Rich text content editor
- **Channel Selection**: Choose target channel for posting
- **Media Upload**: Drag & drop file upload
- **Telegram Storage**: Browse and select from Telegram storage
- **Media Preview**: Preview selected media before posting
- **Schedule Later**: Option to schedule posts for future
- **Inline Buttons**: Optional interactive buttons

## Usage

```tsx
import { CreatePostPage } from '@/pages/posts/create';

// Or via exports
import { CreatePostPage } from '@/pages/posts/exports';
```

## Integration

- Uses `PostCreator` component from `@features/posts`
- Uses `EnhancedMediaUploader` for file uploads
- Uses `TelegramStorageBrowser` for storage browsing
- Integrates with `usePostStore` and `useMediaStore`
