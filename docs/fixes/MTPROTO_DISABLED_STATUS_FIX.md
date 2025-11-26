# MTProto Disabled Status Fix

**Date**: 2025-11-24
**Issue**: Frontend showing "⏳ Pending" for channels with MTProto disabled instead of indicating the channel is intentionally disabled

## Problem

When users disabled MTProto for specific channels via the per-channel toggle:
- ✅ Backend collector properly skipped the channel (verified in logs)
- ✅ Database correctly stored `mtproto_enabled = false`
- ❌ Frontend admin status showed "⏳ Pending - Connect MTProto session"
- ❌ No visual indication that channel was intentionally disabled vs actually pending

**Root Cause**: The `/channels/admin-status/check-all` endpoint didn't query the `channel_mtproto_settings` table to check if MTProto was disabled per-channel.

## Solution

### Backend Changes

**File**: `apps/api/routers/channels/admin_status.py`

1. **Added per-channel settings query**:
   ```python
   # Get per-channel MTProto settings
   from apps.di import get_container
   container = get_container()
   db_pool = await container.database.asyncpg_pool()

   channel_mtproto_settings = {}
   async with db_pool.acquire() as conn:
       for channel in channels:
           setting = await conn.fetchrow(
               """
               SELECT mtproto_enabled
               FROM channel_mtproto_settings
               WHERE channel_id = $1 AND user_id = $2
               """,
               channel.id,
               current_user["id"]
           )
           # None = default enabled (backward compatibility)
           # False = explicitly disabled
           channel_mtproto_settings[channel.id] = setting['mtproto_enabled'] if setting else True
   ```

2. **Added disabled state handling**:
   ```python
   # Check if MTProto is disabled for this channel
   mtproto_disabled = not channel_mtproto_settings.get(channel.id, True)

   if mtproto_disabled:
       logger.info(f"  🚫 Channel {channel.id} has MTProto disabled - skipping admin check")
       mtproto_is_admin = None
   ```

3. **Updated response to include `mtproto_disabled` field**:
   ```python
   status_results[channel.id] = {
       "channel_id": channel.id,
       "channel_name": channel.name,
       "bot_is_admin": bot_is_admin,
       "mtproto_is_admin": mtproto_is_admin,
       "mtproto_disabled": mtproto_disabled,  # NEW
       "can_collect_data": bool(bot_is_admin or mtproto_is_admin),
       "is_inactive": bot_is_admin is False and mtproto_is_admin is False,
       "message": message,
   }
   ```

4. **Added special messages for disabled channels**:
   ```python
   if mtproto_disabled:
       if bot_is_admin is True:
           message = "✓ Bot has admin access - MTProto disabled for this channel"
       elif bot_is_admin is False:
           message = "🚫 Bot has no admin access - MTProto disabled for this channel"
       elif bot_is_admin is None:
           message = "🚫 MTProto disabled for this channel - Configure bot for data collection"
       else:
           message = "🚫 MTProto disabled for this channel"
   ```

### Frontend Changes

**Files**:
- `apps/frontend/src/pages/channels/hooks/useChannelAdminStatus.ts`
- `apps/frontend/src/pages/channels/components/ChannelAdminStatusIndicator.tsx`
- `apps/frontend/src/pages/channels/components/ChannelCard.tsx`

1. **Updated TypeScript interface**:
   ```typescript
   export interface ChannelAdminStatus {
       bot_is_admin: boolean | null;
       mtproto_is_admin: boolean | null;
       mtproto_disabled?: boolean;  // NEW
       is_inactive?: boolean;
       message?: string;
   }
   ```

2. **Updated hook to include new field**:
   ```typescript
   statusMap[result.channel_id] = {
       bot_is_admin: result.bot_is_admin,
       mtproto_is_admin: result.mtproto_is_admin,
       mtproto_disabled: result.mtproto_disabled,  // NEW
       is_inactive: result.is_inactive,
       message: result.message
   };
   ```

3. **Updated component to show disabled state**:
   ```tsx
   <Tooltip
       title={
           mtprotoDisabled
               ? 'MTProto: 🚫 Disabled for this channel'
               : `MTProto: ${mtprotoIsAdmin === true ? '✅ Admin' : mtprotoIsAdmin === false ? '❌ No Access' : '⏳ Pending - Connect MTProto session'}`
       }
       arrow
   >
       <Box sx={{
           bgcolor: mtprotoDisabled ? 'grey.600' : ...,
           borderColor: mtprotoDisabled ? 'grey.800' : ...
       }} />
   </Tooltip>
   ```

## Verification Steps

### 1. Disable MTProto for a channel
```sql
-- Via database
UPDATE channel_mtproto_settings
SET mtproto_enabled = false
WHERE channel_id = 1002678877654;
```

Or use the frontend toggle in the channel card.

### 2. Check admin status API response
```bash
# Get JWT token from browser DevTools (Application > Local Storage > token)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:11400/channels/admin-status/check-all \
  | jq '.results[] | {channel_id, mtproto_disabled, message}'
```

Expected output for disabled channel:
```json
{
  "channel_id": 1002678877654,
  "mtproto_disabled": true,
  "message": "🚫 MTProto disabled for this channel - Configure bot for data collection"
}
```

### 3. Check MTProto worker logs
```bash
tail -f logs/dev_mtproto_worker.log | grep -E "(Skipping channel|MTProto disabled|channels \(skipped)"
```

Expected output:
```
2025-11-24 10:09:51,700 - apps.mtproto.services.data_collection_service - INFO -
  ⏭️  Skipping channel ABC LEGACY NEWS - MTProto disabled per channel setting
2025-11-24 10:09:51,700 - apps.mtproto.services.data_collection_service - INFO -
  📥 Collecting history for user 844338517: 0 channels (skipped 1)
```

### 4. Check frontend display
1. Open channels page: http://localhost:11300/channels
2. Look for the MTProto status dot (antenna icon)
3. Hover over it - should show: "MTProto: 🚫 Disabled for this channel"
4. Dot should be dark grey (not yellow/pending)

## Status Indicator Colors

| State | Color | Tooltip | Meaning |
|-------|-------|---------|---------|
| ✅ Admin | Green | "MTProto: ✅ Admin" | Session has admin access |
| ❌ No Access | Red | "MTProto: ❌ No Access" | Session exists but not admin |
| ⏳ Pending | Grey (light) | "MTProto: ⏳ Pending - Connect MTProto session" | Not configured or check pending |
| 🚫 Disabled | Grey (dark) | "MTProto: 🚫 Disabled for this channel" | Intentionally disabled |

## Data Flow

```
User toggles MTProto →
  Frontend API call →
    Database: UPDATE channel_mtproto_settings SET mtproto_enabled = false →
      Worker: Reads table, skips channel →
        Admin Status API: Reads table, returns mtproto_disabled=true →
          Frontend: Shows "🚫 Disabled" status
```

## Related Files

- **Backend**: `apps/api/routers/channels/admin_status.py`
- **Worker**: `apps/mtproto/services/data_collection_service.py` (already had per-channel filtering)
- **Frontend Hook**: `apps/frontend/src/pages/channels/hooks/useChannelAdminStatus.ts`
- **Frontend Component**: `apps/frontend/src/pages/channels/components/ChannelAdminStatusIndicator.tsx`
- **Database Migration**: `infra/db/alembic/versions/0026b_add_channel_mtproto_settings.py`

## Testing

✅ Backend code: No Python errors
✅ Frontend code: No TypeScript errors
✅ API startup: Clean logs, no errors
✅ Worker startup: Running, collecting from enabled channels
✅ Database query: Working, returns correct disabled status
⏳ End-to-end: Awaiting next worker cycle (10:09) to verify skip logging

## Next Actions

1. Re-enable MTProto for the test channel after verification:
   ```sql
   UPDATE channel_mtproto_settings
   SET mtproto_enabled = true
   WHERE channel_id = 1002678877654;
   ```

2. Test the frontend toggle to ensure it properly updates the database

3. Monitor worker logs in next cycle to confirm channel is skipped

## Success Criteria

- [x] Backend queries `channel_mtproto_settings` table
- [x] Response includes `mtproto_disabled` field
- [x] Frontend TypeScript types updated
- [x] Component renders disabled state with dark grey color
- [x] Tooltip shows "🚫 Disabled" message
- [x] No TypeScript or Python errors
- [ ] Worker logs show channel being skipped (awaiting next cycle)
- [ ] Frontend displays correct status when viewing channels page

---

**Status**: ✅ Implementation complete, awaiting end-to-end verification
