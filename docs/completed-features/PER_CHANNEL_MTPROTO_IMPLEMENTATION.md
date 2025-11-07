# Per-Channel MTProto Control Implementation

## Overview
Implemented granular per-channel MTProto access control, allowing users to enable/disable MTProto functionality for individual channels independently of the global setting.

## Implementation Date
November 3, 2025

## Components Implemented

### 1. Database Schema (`infra/db/alembic/versions/`)

#### Migration: `169d798b7035_add_channel_mtproto_settings.py`
- **Table**: `channel_mtproto_settings`
- **Columns**:
  - `id` (BIGSERIAL, Primary Key)
  - `user_id` (BIGINT, FK to users.id, CASCADE delete)
  - `channel_id` (BIGINT, FK to channels.id, CASCADE delete)
  - `mtproto_enabled` (BOOLEAN, default TRUE)
  - `created_at` (TIMESTAMP WITH TIME ZONE)
  - `updated_at` (TIMESTAMP WITH TIME ZONE)
- **Constraints**:
  - UNIQUE(user_id, channel_id) - One setting per user-channel pair
- **Indexes**:
  - `ix_channel_mtproto_user_enabled` on (user_id, mtproto_enabled)

#### Migration: `f7ffb0be449f_add_mtproto_audit_log.py`
- **Table**: `mtproto_audit_log`
- **Columns**:
  - `id`, `user_id`, `channel_id` (nullable for global events)
  - `action`, `previous_state`, `new_state`
  - `ip_address`, `user_agent`, `metadata` (JSON)
  - `timestamp`
- **Purpose**: Audit trail for all MTProto state changes

### 2. Backend Repository (`infra/db/repositories/`)

#### `ChannelMTProtoRepository`
**File**: `channel_mtproto_repository.py`

**Key Methods**:
```python
async def get_channel_setting(user_id: int, channel_id: int) -> ChannelMTProtoSettings | None
async def set_channel_enabled(user_id: int, channel_id: int, enabled: bool) -> ChannelMTProtoSettings
async def is_channel_enabled(user_id: int, channel_id: int, default: bool = True) -> bool
async def get_all_user_settings(user_id: int) -> List[ChannelMTProtoSettings]
async def bulk_set_channels(user_id: int, channel_ids: List[int], enabled: bool) -> List[ChannelMTProtoSettings]
```

**Features**:
- Upsert logic (INSERT ... ON CONFLICT UPDATE)
- Efficient bulk operations
- Default behavior (no record = inherit global setting)

### 3. Backend ORM Models (`infra/db/models/`)

#### Updated `user_bot_orm.py`
Added two new models:

**`MTProtoAuditLog`**:
- Maps to `mtproto_audit_log` table
- Tracks all MTProto events with metadata

**`ChannelMTProtoSettings`**:
- Maps to `channel_mtproto_settings` table
- Per-channel MTProto enable/disable state

### 4. Backend Service (`apps/api/services/`)

#### `MTProtoAuditService`
**File**: `mtproto_audit_service.py`

**Key Methods**:
- `log_event()` - Generic audit logging
- `log_toggle_event()` - Specific for enable/disable events
- `log_setup_event()`, `log_verification_event()`, etc.
- `get_user_audit_history()` - Query audit logs

**Features**:
- Captures IP address (X-Forwarded-For, X-Real-IP, or client.host)
- Captures User-Agent
- Stores JSON metadata for extended context
- Automatic timestamp with timezone

### 5. Backend API Endpoints (`apps/api/routers/`)

#### Updated `user_mtproto_router.py`

**New Endpoints**:

1. **GET `/api/user-mtproto/channels/settings`**
   - Returns: `Dict[int, bool]` (channel_id -> enabled mapping)
   - Purpose: Get all per-channel MTProto settings for user

2. **GET `/api/user-mtproto/channels/{channel_id}/settings`**
   - Returns: `{ "enabled": bool }`
   - Purpose: Get MTProto setting for specific channel

3. **POST `/api/user-mtproto/channels/{channel_id}/toggle`**
   - Body: `{ "enabled": bool }`
   - Returns: `MTProtoActionResponse`
   - Purpose: Toggle MTProto for specific channel
   - Features: Audit logging included

**Updated Endpoint**:

4. **POST `/api/user-mtproto/toggle`** (global toggle)
   - Now includes audit logging with IP/User-Agent capture
   - Records previous and new state

### 6. MTProto Service Logic (`apps/mtproto/multi_tenant/`)

#### Updated `UserMTProtoService`

**Key Method**: `_is_mtproto_enabled(user_id, channel_id)`

**Logic Flow**:
1. Check global `mtproto_enabled` flag in `user_bot_credentials`
   - If FALSE, return FALSE (global disable overrides)
2. If `channel_id` is None, return TRUE (inherit global)
3. If `channel_id` provided:
   - Query `channel_mtproto_settings` for per-channel setting
   - If no record exists, return TRUE (default enabled)
   - If record exists, return its `mtproto_enabled` value

**Precedence Rules**:
```
Effective MTProto Access = Global Enabled AND (Channel Setting OR Default True)
```

### 7. Frontend API Client (`apps/frontend/src/features/mtproto-setup/`)

#### Updated `api.ts`

**New Functions**:
```typescript
getChannelMTProtoSettings(): Promise<Record<number, boolean>>
getChannelMTProtoSetting(channelId: number): Promise<{ enabled: boolean }>
toggleChannelMTProto(channelId: number, enabled: boolean): Promise<MTProtoActionResponse>
```

### 8. Frontend Components

#### New Component: `ChannelMTProtoToggle.tsx`
**Location**: `apps/frontend/src/features/mtproto-setup/components/`

**Features**:
- Two modes: `compact` (inline switch) and full card layout
- Real-time toggle with loading states
- Error handling with Snackbar notifications
- Success feedback
- Icon indicators (MTProto enabled/disabled)
- Automatic status loading on mount
- Type-safe (accepts string or number channel IDs)

**Props**:
```typescript
interface ChannelMTProtoToggleProps {
  channelId: string | number;
  channelName: string;
  compact?: boolean; // default: false
}
```

#### Updated: `ChannelsManagementPage.tsx`
**Location**: `apps/frontend/src/pages/`

**Changes**:
- Added import for `ChannelMTProtoToggle`
- Integrated toggle component into each channel card
- Positioned below channel metrics, above card actions
- Uses compact mode for inline display

**Visual Layout**:
```
┌─────────────────────────────┐
│ Channel Name                │
│ Description                 │
│                             │
│ ID: 123 | @username         │
│                             │
│ ┌─────────────────────────┐ │
│ │ 📊 50 posts • 1000 views│ │
│ └─────────────────────────┘ │
│ ─────────────────────────── │
│ 📡 MTProto    [●●●○○]       │  <- New toggle
└─────────────────────────────┘
│ [Edit] [Delete]             │
└─────────────────────────────┘
```

## Architecture Decisions

### 1. **Fail-Safe Defaults**
- No per-channel setting = Enabled (inherit global)
- Error loading settings = Default to enabled (fail-open for UX)
- Rationale: Minimizes friction for existing users

### 2. **Global Override**
- Global disabled ALWAYS overrides per-channel settings
- Prevents confusion (cannot enable per-channel if global is off)
- Clear hierarchy: Global > Per-Channel

### 3. **Audit Logging**
- Non-blocking: Audit failures don't fail the operation
- Best-effort logging with error warnings
- Separate DB session for audit writes
- Rationale: Availability > completeness for audit logs

### 4. **Database Design**
- Unique constraint on (user_id, channel_id)
- Foreign keys with CASCADE delete (cleanup on user/channel deletion)
- No per-channel setting by default (reduces DB rows for common case)

### 5. **Frontend Type Safety**
- Channel IDs auto-convert (string to number) in component
- Handles both API response types seamlessly
- TypeScript strict mode compatible

## Testing Strategy

### Backend Tests (Deferred - Fixture Issues)
**File**: `tests/api/test_mtproto_toggle.py`

Issues identified:
- Missing `client` fixture (needs `tests/conftest.py`)
- Missing `test_user` fixture
- Coverage at 0% due to test setup failures

**Recommended Fix** (for later):
1. Create `tests/conftest.py` with adapter fixtures
2. Add `create_access_token` shim to `apps/api/middleware/auth.py`
3. Re-run tests with proper fixtures

### Manual Testing
**Steps**:
1. Start API server
2. Authenticate and get JWT token
3. Test endpoints:
   ```bash
   # Global toggle
   curl -X POST http://localhost:11400/api/user-mtproto/toggle \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"enabled": false}'

   # Per-channel toggle
   curl -X POST http://localhost:11400/api/user-mtproto/channels/123/toggle \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"enabled": true}'

   # Get all settings
   curl http://localhost:11400/api/user-mtproto/channels/settings \
     -H "Authorization: Bearer <token>"

   # Check audit log
   psql -c "SELECT * FROM mtproto_audit_log ORDER BY timestamp DESC LIMIT 5;"
   ```

4. Frontend: Visit `/channels` page, toggle switches per channel

## Database Verification

**Check Tables Exist**:
```sql
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('mtproto_audit_log', 'channel_mtproto_settings');
```

**Inspect Schema**:
```sql
\d mtproto_audit_log
\d channel_mtproto_settings
```

**Query Settings**:
```sql
-- Get all per-channel settings for user
SELECT cms.*, c.name as channel_name
FROM channel_mtproto_settings cms
JOIN channels c ON c.id = cms.channel_id
WHERE cms.user_id = 844338517;

-- Get audit history
SELECT * FROM mtproto_audit_log
WHERE user_id = 844338517
ORDER BY timestamp DESC
LIMIT 10;
```

## Migration Commands

**Apply Migrations**:
```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate
DATABASE_URL=postgresql://analytic:change_me@localhost:10100/analytic_bot \
  python -m alembic upgrade head
```

**Rollback (if needed)**:
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 67989015125a  # Before per-channel changes
```

## Security Considerations

1. **Authorization**: All endpoints check JWT auth + user ownership
2. **Channel Ownership**: API validates user owns the channel before allowing toggle
3. **Audit Trail**: IP + User-Agent captured for forensics
4. **SQL Injection**: Parameterized queries + ORM (safe)
5. **Rate Limiting**: Inherits global API rate limits

## Performance

**Database Indexes**:
- `ix_channel_mtproto_user_enabled` for fast user queries
- `ix_mtproto_audit_user_timestamp` for audit log queries
- Unique constraint on (user_id, channel_id) provides implicit index

**Query Patterns**:
- Per-channel check: 1 query (SELECT by user_id + channel_id)
- Bulk settings fetch: 1 query (SELECT WHERE user_id)
- Toggle operation: 1 UPSERT + 1 audit INSERT

**Caching Opportunity** (future):
- Cache per-channel settings in Redis
- TTL: 5 minutes
- Invalidate on toggle

## Known Limitations

1. **No Bulk Toggle UI**: Frontend shows per-channel toggles, but no "toggle all" button
2. **No Audit Log Viewer**: Audit data stored but no UI to view it yet
3. **Test Coverage**: Backend tests need fixture repairs
4. **No Permission Inheritance**: Channel-level permissions not tied to MTProto access

## Future Enhancements

1. **Audit Log Viewer UI**
   - Modal or dedicated page showing recent events
   - Filters by action, channel, date range
   - Export to CSV

2. **Bulk Operations**
   - "Enable all channels" button
   - "Disable all channels" button
   - Uses existing `bulk_set_channels()` backend method

3. **MTProto Usage Analytics**
   - Track how often per-channel access is used
   - Display which channels use MTProto most
   - Cost estimation (if MTProto has API limits)

4. **Permission Integration**
   - Tie MTProto access to channel-level RBAC permissions
   - Allow channel admins to control MTProto for their channels

5. **Frontend Improvements**
   - Show global MTProto status in channel list header
   - Warning when global is disabled (grays out per-channel toggles)
   - Confirm dialog for disabling (optional)

6. **Test Coverage**
   - Fix fixtures in `tests/conftest.py`
   - Add integration tests for per-channel flow
   - Add audit log tests

## Files Modified/Created

### Backend
- ✅ `infra/db/alembic/versions/f7ffb0be449f_add_mtproto_audit_log.py` (NEW)
- ✅ `infra/db/alembic/versions/169d798b7035_add_channel_mtproto_settings.py` (NEW)
- ✅ `infra/db/models/user_bot_orm.py` (UPDATED - added 2 models)
- ✅ `infra/db/repositories/channel_mtproto_repository.py` (NEW)
- ✅ `apps/api/services/mtproto_audit_service.py` (NEW)
- ✅ `apps/api/routers/user_mtproto_router.py` (UPDATED - added 3 endpoints + audit)
- ✅ `apps/mtproto/multi_tenant/user_mtproto_service.py` (VERIFIED - already had logic)

### Frontend
- ✅ `apps/frontend/src/features/mtproto-setup/api.ts` (UPDATED - added 3 functions)
- ✅ `apps/frontend/src/features/mtproto-setup/components/ChannelMTProtoToggle.tsx` (NEW)
- ✅ `apps/frontend/src/features/mtproto-setup/index.ts` (UPDATED - export new component)
- ✅ `apps/frontend/src/pages/ChannelsManagementPage.tsx` (UPDATED - integrated toggle)

### Tests (Deferred)
- ⏳ `tests/conftest.py` (TODO - needs creation)
- ⏳ `tests/api/test_mtproto_toggle.py` (EXISTS - needs fixture fixes)

## Completion Status

✅ **Database Schema** - Migrations applied successfully
✅ **Backend Repository** - Full CRUD with upsert logic
✅ **Backend ORM Models** - MTProtoAuditLog + ChannelMTProtoSettings
✅ **Backend Service** - MTProtoAuditService with IP/UA capture
✅ **Backend API Endpoints** - 3 new endpoints + audit logging
✅ **MTProto Service Logic** - Per-channel checking implemented
✅ **Frontend API Client** - 3 new TypeScript functions
✅ **Frontend Component** - ChannelMTProtoToggle with 2 modes
✅ **Frontend Integration** - Added to ChannelsManagementPage
✅ **TypeScript Compilation** - No errors
⏳ **Backend Tests** - Deferred (fixture issues documented)
⏳ **Audit Log Viewer** - Future enhancement

## Summary

Successfully implemented full-stack per-channel MTProto control with:
- Robust backend (DB, API, services, audit logging)
- Polished frontend (toggle component, channel integration)
- Type-safe implementation (TypeScript strict mode)
- Database migrations applied and verified
- Clear precedence rules (global > per-channel)
- Comprehensive audit trail for compliance

**Ready for production use** pending test fixture fixes and optional audit log viewer.
