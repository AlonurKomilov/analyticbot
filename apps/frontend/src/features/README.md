# Features Directory

This directory contains all feature modules organized by business domain (feature-first architecture).

## Structure

Each feature follows this pattern:

```
features/
├── [feature-name]/
│   ├── index.ts              # Barrel export for the feature
│   ├── [Feature]Component.tsx # Main feature component
│   ├── components/           # Feature-specific components
│   ├── hooks/               # Feature-specific hooks
│   ├── utils/               # Feature-specific utilities
│   ├── types/               # Feature-specific types
│   └── constants/           # Feature-specific constants
```

## Available Features

### Admin
User and channel administration
- **users/**: User management (CRUD, roles, suspension)
- **channels/**: Channel management (CRUD, validation, statistics)
- **common/**: Shared admin components

### Analytics
Analytics and reporting features
- **overview/**: Analytics dashboard overview
- **growth/**: Growth metrics and trends
- **engagement/**: Engagement analytics

### Protection
Content protection features
- **watermark/**: Watermark management
- **detection/**: Content leak detection
- **alerts/**: Security alerts

### Auth
Authentication and authorization
- **login/**: Login functionality
- **register/**: User registration

### Posts
Post management
- **create/**: Post creation
- **schedule/**: Post scheduling
- **list/**: Post listing and management

### Payment
Payment and billing
- **invoices/**: Invoice management
- **subscriptions/**: Subscription management

### AI Services
AI-powered features
- **chat/**: AI chat interface
- **optimization/**: Content optimization

### Alerts
System alerts and notifications

### Dashboard
Main dashboard views

## Import Examples

```typescript
// Import from a feature
import { UserManagement } from '@features/admin/users';

// Import multiple exports
import { ChannelList, ChannelDetails } from '@features/admin/channels';
```

## Best Practices

1. **Feature Independence**: Features should be as independent as possible
2. **Shared Code**: Use `@shared` for truly reusable components
3. **Barrel Exports**: Export public API through index.ts
4. **Co-location**: Keep related code close together
5. **Flat Structure**: Avoid deep nesting within features
