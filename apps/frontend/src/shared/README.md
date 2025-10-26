# Shared Directory

This directory contains reusable code shared across multiple features.

## Structure

```
shared/
├── components/       # Reusable UI components
│   ├── base/        # Basic building blocks (Button, Input, Text)
│   ├── layout/      # Layout components (Container, Grid, Stack)
│   ├── feedback/    # Feedback components (Alert, Toast, Spinner)
│   ├── forms/       # Form components (TextField, Select, Checkbox)
│   ├── navigation/  # Navigation (Navbar, Sidebar, Tabs)
│   └── ui/          # Higher-level UI (Card, Modal, Dialog)
├── hooks/           # Reusable React hooks
├── services/        # API and other services
│   └── api/         # API client and utilities
├── utils/           # Utility functions
├── types/           # Shared TypeScript types
├── constants/       # Application constants
├── styles/          # Shared styles and themes
└── assets/          # Static assets (images, fonts)
```

## Component Categories

### Base Components
Fundamental building blocks that implement the design system:
- Button, Input, Text, Icon, Badge, etc.

### Layout Components
Components for page structure and positioning:
- Container, Grid, Stack, Box, Divider

### Feedback Components
Components for user feedback and loading states:
- Alert, Toast, Snackbar, Spinner, Progress, Skeleton

### Form Components
Form inputs and validation:
- TextField, Select, Checkbox, Radio, Switch, DatePicker

### Navigation Components
Navigation and routing:
- Navbar, Sidebar, Tabs, Breadcrumbs, Menu

### UI Components
Higher-level composite components:
- Card, Modal, Dialog, Drawer, Tooltip, Popover

## Import Examples

```typescript
// Import shared components
import { Button, Input } from '@shared/components/base';
import { Card, Modal } from '@shared/components/ui';

// Import shared hooks
import { useDebounce, useLocalStorage } from '@shared/hooks';

// Import utilities
import { formatDate, validateEmail } from '@shared/utils';
```

## Best Practices

1. **Generic & Reusable**: Only put truly reusable code here
2. **No Business Logic**: Shared components should be domain-agnostic
3. **Well Documented**: Document props and usage examples
4. **Tested**: Shared code should have good test coverage
5. **Stable API**: Minimize breaking changes to shared exports
