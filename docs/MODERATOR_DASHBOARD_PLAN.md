# Moderator Dashboard Implementation Plan

## Overview

This document outlines the plan for implementing a moderator dashboard at `moderator.analyticbot.org`. The moderator role sits between regular users and admins in the role hierarchy:

```
viewer < user < moderator < admin < owner
```

## Current Role Permissions Analysis

### Moderator Permissions (from permissions.py)
```python
"moderator": RolePermissions(
    role="moderator",
    permissions={
        Permission.VIEW_CONTENT,
        Permission.API_READ,
        Permission.BOT_COMMANDS,
        Permission.VIEW_USERS,
        Permission.MANAGE_USERS,
        Permission.EDIT_CONTENT,
        Permission.MODERATE_CONTENT,
        Permission.VIEW_ANALYTICS,
        Permission.BOT_ANALYTICS,
        Permission.API_WRITE,
    },
    description="Content moderation and user management",
)
```

### What Moderators CAN Do:
- ✅ View users (but limited info)
- ✅ Manage users (suspend/unsuspend, but NOT delete)
- ✅ View content/channels
- ✅ Moderate content (review flagged content)
- ✅ View analytics (read-only)
- ✅ Bot analytics

### What Moderators CANNOT Do:
- ❌ Delete users
- ❌ System configuration
- ❌ Manage settings
- ❌ Database access
- ❌ Bot configuration
- ❌ API admin access
- ❌ View audit logs (admin only)
- ❌ Manage plans/subscriptions
- ❌ MTProto pool management
- ❌ System health management

---

## Moderator Dashboard Features

### 1. Dashboard (Home Page)
**Purpose:** Quick overview of moderation tasks and system status

**Components:**
- Active support tickets count
- Pending user reports
- Flagged content queue
- Recent moderation actions (own actions only)
- Quick stats: Active users today, new signups, suspended users

### 2. User Management (Limited)
**Purpose:** Handle user-related support tasks

**Features:**
- View user list (limited fields: ID, username, email, status, created_at, last_login)
- Search users by ID, username, email
- View user details (no credit adjustment, no role change)
- Suspend/Unsuspend users (with reason)
- View user's channels (read-only)
- View user's subscription status (read-only)
- **Cannot:** Delete users, change roles, adjust credits, view sensitive data

### 3. Channel Management (Limited)
**Purpose:** Review and moderate channels

**Features:**
- View all channels
- Search channels
- View channel details
- Suspend/Unsuspend channels (with reason)
- Force sync channel data
- **Cannot:** Delete channels, change ownership

### 4. Content Moderation
**Purpose:** Review flagged/reported content

**Features:**
- Flagged posts queue
- User reports queue
- Mark content as reviewed/approved
- Hide/remove inappropriate content
- Escalate to admin
- Add moderation notes

### 5. Support Tickets
**Purpose:** Handle user support requests

**Features:**
- View open tickets
- Respond to tickets
- Close/resolve tickets
- Escalate to admin
- Ticket history for each user

### 6. Analytics (Read-Only)
**Purpose:** View system statistics for support context

**Features:**
- User statistics (signup trends, active users)
- Channel statistics
- Bot usage statistics
- **No export functionality**
- **No configuration changes**

### 7. Moderation Log
**Purpose:** Track own moderation actions

**Features:**
- View own actions history
- **Cannot:** View other moderators' actions
- **Cannot:** View admin actions

---

## Technical Implementation

### Phase 1: Project Setup (Day 1)
1. Create new frontend app: `apps/frontend/apps/moderator/`
2. Copy admin template structure
3. Setup Vite configuration
4. Configure nginx for moderator.analyticbot.org
5. Create moderator-specific theme (different accent color)

### Phase 2: Backend APIs (Days 2-3)
1. Create moderator-specific router: `apps/api/routers/moderator_router.py`
2. Add `require_moderator_user()` middleware
3. Create limited endpoints:
   - `GET /moderator/users` (limited fields)
   - `GET /moderator/users/{id}` (limited details)
   - `POST /moderator/users/{id}/suspend`
   - `POST /moderator/users/{id}/unsuspend`
   - `GET /moderator/channels`
   - `POST /moderator/channels/{id}/suspend`
   - `GET /moderator/dashboard/stats`
   - `GET /moderator/moderation/queue`
   - `POST /moderator/moderation/action`

### Phase 3: Frontend Pages (Days 4-6)
1. ModeratorDashboardPage
2. ModeratorUsersPage (limited)
3. ModeratorChannelsPage (limited)
4. ContentModerationPage
5. SupportTicketsPage
6. ModerationLogPage

### Phase 4: Auth & Security (Day 7)
1. Moderator login with role check
2. Prevent admin/owner accounts from using moderator dashboard
3. Session management
4. Audit logging for moderator actions

### Phase 5: Testing & Deploy (Days 8-9)
1. Test all endpoints
2. Test role restrictions
3. Deploy to moderator.analyticbot.org
4. Configure SSL

---

## Directory Structure

```
apps/frontend/apps/moderator/
├── src/
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── UsersPage.tsx
│   │   ├── ChannelsPage.tsx
│   │   ├── ModerationQueuePage.tsx
│   │   ├── SupportTicketsPage.tsx
│   │   ├── ModerationLogPage.tsx
│   │   └── LoginPage.tsx
│   ├── components/
│   │   ├── ModeratorLayout.tsx
│   │   ├── UserCard.tsx
│   │   ├── ChannelCard.tsx
│   │   └── ModerationAction.tsx
│   ├── contexts/
│   │   └── ModeratorAuthContext.tsx
│   ├── config/
│   │   ├── api.ts
│   │   └── routes.ts
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── vite.config.js
├── package.json
└── tsconfig.json
```

---

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/moderator/dashboard/stats` | GET | Dashboard statistics |
| `/moderator/users` | GET | List users (limited fields) |
| `/moderator/users/{id}` | GET | User details (limited) |
| `/moderator/users/{id}/suspend` | POST | Suspend user |
| `/moderator/users/{id}/unsuspend` | POST | Unsuspend user |
| `/moderator/channels` | GET | List channels |
| `/moderator/channels/{id}` | GET | Channel details |
| `/moderator/channels/{id}/suspend` | POST | Suspend channel |
| `/moderator/channels/{id}/unsuspend` | POST | Unsuspend channel |
| `/moderator/moderation/queue` | GET | Flagged content queue |
| `/moderator/moderation/action` | POST | Take moderation action |
| `/moderator/tickets` | GET | Support tickets |
| `/moderator/tickets/{id}` | GET/POST | View/respond ticket |
| `/moderator/log` | GET | Own moderation history |

---

## UI/UX Differences from Admin Panel

| Aspect | Admin Panel | Moderator Dashboard |
|--------|-------------|---------------------|
| Theme Color | Blue (#2196F3) | Teal (#00897B) |
| Branding | "Admin Panel" | "Moderator Dashboard" |
| Navigation | Full menu | Limited menu |
| Actions | Full CRUD | Limited actions |
| Data Access | Complete | Filtered/Limited |
| Audit Log | Full access | Own actions only |

---

## Security Considerations

1. **Role Verification:** Every API endpoint must verify moderator role
2. **Data Filtering:** Never expose sensitive user data (passwords, tokens, etc.)
3. **Action Logging:** All moderator actions logged with timestamp and moderator ID
4. **Rate Limiting:** Prevent abuse of moderation endpoints
5. **Session Timeout:** Shorter session timeout than admin (4 hours vs 24 hours)
6. **IP Logging:** Log IP address for all moderation actions

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 1 day | Project setup, nginx config |
| Phase 2 | 2 days | Backend APIs |
| Phase 3 | 3 days | Frontend pages |
| Phase 4 | 1 day | Auth & security |
| Phase 5 | 2 days | Testing & deployment |
| **Total** | **9 days** | Full implementation |

---

## Quick Start Implementation

To begin implementation:

```bash
# 1. Create moderator frontend app
cd apps/frontend/apps
cp -r admin moderator

# 2. Update package.json name
# 3. Update vite.config.js port (11320)
# 4. Configure nginx for moderator.analyticbot.org
# 5. Create moderator API router
```

---

## Next Steps

1. ✅ Review and approve this plan
2. ⬜ Create moderator frontend app skeleton
3. ⬜ Implement backend moderator router
4. ⬜ Build moderator-specific pages
5. ⬜ Configure nginx and deploy
6. ⬜ Test with moderator accounts
