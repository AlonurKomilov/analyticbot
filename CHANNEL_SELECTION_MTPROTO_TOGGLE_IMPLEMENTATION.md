# Channel Selection & MTProto Toggle Implementation

## Summary

This implementation includes:
1. **Channel Selection Bugfix** - Ensures analytics are properly isolated per channel
2. **MTProto Enable/Disable Toggle** - Full end-to-end implementation with backend API, database migration, and frontend UI

## 1. Channel Selection Audit ✅

### Finding
The analytics system **correctly isolates data per channel**:
- All API calls include `channelId` parameter
- Analytics components (`useAnalyticsStore`, `AnalyticsDashboard`, `TopPostsTable`, etc.) filter by selected channel
- Switching channels triggers refetch of analytics data for the new channel

### Fix Applied
**File**: `/home/abcdeveloper/projects/analyticbot/apps/frontend/src/pages/EnhancedDashboardPage.tsx`

**Problem**: ChannelSelector (using `useUserChannels`) stored selection locally, but analytics components read from global `useChannelStore.selectedChannel`

**Solution**: Added synchronization so channel selection propagates to global store:

```tsx
onChannelChange={(ch) => {
  setSelectedChannel(ch as any);
  globalSelectChannel && globalSelectChannel(ch as any);
}}
```

**Result**: When user selects a channel, all analytics components receive the selection and fetch data for that specific channel.

## 2. MTProto Toggle Implementation ✅

### Database Layer

**Migration**: `67989015125a_add_mtproto_enabled_flag.py`
- Added `mtproto_enabled` boolean column to `user_bot_credentials` table
- Default value: `TRUE` (maintains existing functionality)
- Applied with Alembic

**Domain Model**: `core/models/user_bot_domain.py`
- Added `mtproto_enabled: bool = True` field to `UserBotCredentials`

**ORM Model**: `infra/db/models/user_bot_orm.py`
- Added mapped column: `mtproto_enabled: Mapped[bool]`
- Server default: `true`

### Backend API

**Endpoint**: `POST /api/user-mtproto/toggle`

**Request**:
```json
{
  "enabled": true  // or false
}
```

**Response**:
```json
{
  "success": true,
  "message": "MTProto enabled successfully. Full history access is now available."
}
```

**Behavior**:
- When disabled: Disconnects MTProto client, prevents history reading
- When enabled: Allows MTProto client to reconnect, restores history access
- Requires existing MTProto configuration (fails with 400 if not configured)

**Updated Endpoints**:
1. **`GET /api/user-mtproto/status`** - Now includes `mtproto_enabled` check in `can_read_history` calculation
2. **`POST /api/user-mtproto/toggle`** - New endpoint for enable/disable
3. **Service Layer** - `UserMTProtoService.get_user_client()` checks `mtproto_enabled` flag before creating client

**Files Modified**:
- `apps/api/routers/user_mtproto_router.py` - Added toggle endpoint and status check
- `apps/mtproto/multi_tenant/user_mtproto_service.py` - Added enabled flag check

### Frontend

**API Client**: `apps/frontend/src/features/mtproto-setup/api.ts`
```typescript
export async function toggleMTProto(enabled: boolean): Promise<MTProtoActionResponse> {
  const response = await apiClient.post<MTProtoActionResponse>(
    '/api/user-mtproto/toggle',
    { enabled }
  );
  return response;
}
```

**UI Component**: `apps/frontend/src/features/mtproto-setup/components/MTProtoStatusCard.tsx`

Added:
- Toggle switch (Material-UI `Switch` component)
- Loading state while toggling
- Error display for toggle failures
- Status indicator showing current state
- Refresh status after toggle completes

**UI Features**:
- Switch shows current MTProto state (enabled/disabled)
- Help text explains what each state means:
  - Enabled: "Full channel history access is available"
  - Disabled: "Only bot-based operations are available"
- Disabled when loading or processing
- Automatically refreshes status after toggle

## 3. Testing

**Test File**: `tests/api/test_mtproto_toggle.py`

**Test Coverage**:
1. `test_toggle_mtproto_disabled` - Verify disabling works
2. `test_toggle_mtproto_enabled` - Verify enabling works
3. `test_toggle_reflects_in_status` - Verify status endpoint reflects toggle state
4. `test_toggle_without_configuration` - Verify proper error when no config
5. `test_toggle_validation` - Verify request validation

**Run Tests**:
```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate
pytest tests/api/test_mtproto_toggle.py -v
```

## 4. User Flow

### Setting Up MTProto
1. User navigates to Settings → MTProto Setup
2. Enters API credentials and phone number
3. Receives verification code
4. Completes verification
5. **MTProto is enabled by default**

### Using the Toggle
1. User views MTProto Status Card
2. Sees current status (enabled/disabled)
3. Clicks toggle switch
4. Backend processes request:
   - If disabling: Disconnects client, updates DB
   - If enabling: Updates DB, allows reconnection
5. UI refreshes to show new state

### Impact on Features
- **Enabled**: Full channel history access, MTProto-based analytics
- **Disabled**: Only bot-based operations, no historical data fetch

## 5. Migration Path

For existing users:
- Migration sets `mtproto_enabled = TRUE` by default
- No action required - existing functionality preserved
- Users can disable at any time via toggle

## 6. Security Considerations

- Toggle requires authentication (JWT token)
- Only affects user's own MTProto configuration
- Disabling immediately disconnects client
- Session data remains in database (only flag changes)
- Can re-enable without re-verification

## 7. Files Changed

### Backend
1. `infra/db/alembic/versions/67989015125a_add_mtproto_enabled_flag.py` - Migration
2. `core/models/user_bot_domain.py` - Domain model
3. `infra/db/models/user_bot_orm.py` - ORM model
4. `apps/api/routers/user_mtproto_router.py` - API endpoint
5. `apps/mtproto/multi_tenant/user_mtproto_service.py` - Service logic

### Frontend
6. `apps/frontend/src/features/mtproto-setup/api.ts` - API client
7. `apps/frontend/src/features/mtproto-setup/components/MTProtoStatusCard.tsx` - UI component
8. `apps/frontend/src/pages/EnhancedDashboardPage.tsx` - Channel selection fix

### Tests
9. `tests/api/test_mtproto_toggle.py` - New test file

## 8. Deployment Checklist

- [x] Database migration created
- [x] Migration applied to dev database
- [x] Backend API implemented
- [x] Service layer updated
- [x] Frontend API client updated
- [x] Frontend UI implemented
- [x] Tests written
- [x] Dev servers restarted
- [ ] Run integration tests
- [ ] Test on staging environment
- [ ] Document for users
- [ ] Deploy to production

## 9. Known Limitations

1. Toggle is per-user (not per-channel)
2. Disabling doesn't clear existing cached history data
3. Re-enabling requires MTProto client to reconnect (may take a few seconds)

## 10. Future Enhancements

1. Add toggle to Settings page (currently only in MTProto Status Card)
2. Add audit log for toggle events
3. Add email notification when MTProto is disabled by admin
4. Add per-channel MTProto control
5. Add scheduled enable/disable (e.g., disable during off-hours)

## Verification Steps

1. **Channel Selection Fix**:
   ```
   - Open frontend dashboard
   - Select a channel from dropdown
   - Verify console no longer shows "No channel selected"
   - Verify analytics display data for selected channel
   - Switch to different channel
   - Verify analytics refresh with new channel's data
   ```

2. **MTProto Toggle**:
   ```
   - Navigate to Settings → MTProto Setup
   - View MTProto Status Card
   - Toggle switch to OFF
   - Verify message: "MTProto disabled successfully..."
   - Check /api/user-mtproto/status - can_read_history should be false
   - Toggle switch to ON
   - Verify message: "MTProto enabled successfully..."
   - Check /api/user-mtproto/status - can_read_history should be true
   ```

3. **Backend Verification**:
   ```bash
   # Check database
   psql -U analytic -d analytic_bot -c "SELECT user_id, mtproto_enabled FROM user_bot_credentials;"

   # Check API logs
   tail -f logs/dev_api.log | grep -i mtproto
   ```

## Support

For issues or questions:
- Check logs: `logs/dev_api.log`, `logs/dev_bot.log`
- Run tests: `pytest tests/api/test_mtproto_toggle.py`
- Review API docs: `http://localhost:11400/docs#/User%20MTProto%20Management`
