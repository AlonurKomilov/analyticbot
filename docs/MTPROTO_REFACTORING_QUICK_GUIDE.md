# MTProto Refactoring Quick Guide
**TL;DR for Developers**

## 🎯 What We're Fixing
```bash
# Current violations
python3 scripts/guard_imports.py
# Result: 7 violations in channels_router.py & telegram_storage_router.py
```

## 🔧 Step-by-Step Implementation

### Step 1: Create Service (30 min)
```bash
# Create the service file
touch apps/api/services/channel_admin_check_service.py
```

```python
# apps/api/services/channel_admin_check_service.py
class ChannelAdminCheckService:
    def __init__(self, mtproto_service, user_bot_repo, encryption_service):
        self.mtproto = mtproto_service
        self.user_repo = user_bot_repo
        self.encryption = encryption_service

    async def check_mtproto_admin_status(
        self, user_id: int, channel_id: int,
        channel_username: str | None = None,
        telegram_id: int | None = None,
    ) -> dict:
        """Check admin rights via MTProto (all telethon imports here)."""
        # Move all the GetParticipantRequest logic here
        # Return: {"is_admin": bool, "admin_rights": dict, "error": str}
```

### Step 2: Update Router (15 min)
```python
# apps/api/routers/channels_router.py

# REMOVE THIS (lines 242-280):
# from telethon.tl.functions.channels import GetParticipantRequest
# ... 50 lines of MTProto logic ...

# ADD THIS:
from apps.api.services.channel_admin_check_service import get_admin_check_service

admin_service = await get_admin_check_service()
result = await admin_service.check_mtproto_admin_status(
    user_id=current_user["id"],
    channel_id=channel.id,
    channel_username=channel_username,
    telegram_id=channel.telegram_id,
)
mtproto_is_admin = result["is_admin"]
```

### Step 3: Add to DI Container (10 min)
```python
# apps/di/bot_container.py

channel_admin_check_service = providers.Factory(
    create_channel_admin_check_service,
    mtproto_service=mtproto_service,
    user_bot_repo=database.user_bot_repo,
    encryption_service=encryption_service,
)
```

### Step 4: Validate (5 min)
```bash
# Test the changes
python3 scripts/guard_imports.py
# Expected: 0 violations in channels_router.py ✅

# Test the endpoint
curl http://localhost:8000/api/channels
```

## 📋 Files to Touch

### Modify These:
1. `apps/api/routers/channels_router.py` (delete 50 lines, add 5)
2. `apps/api/routers/telegram_storage_router.py` (delete 45 lines, add 10)

### Create These:
1. `apps/api/services/channel_admin_check_service.py` (new, ~150 lines)
2. `apps/di/provider_modules/mtproto_providers.py` (new, ~60 lines)

### Update DI:
1. `apps/di/bot_container.py` (add ~15 lines)

## 🎓 Pattern Reference

Follow the same pattern as **AlertsManagementService** refactor:

**Before (Anti-pattern)**:
```python
from apps.di import get_container  # ❌ Service Locator
container = get_container()
service = await container.bot.some_service()
```

**After (Clean)**:
```python
def __init__(self, some_service):  # ✅ Dependency Injection
    self._service = some_service
```

## 🚫 Don't Touch

These are **acceptable** (MTProto feature boundary):
- `apps/api/routers/user_mtproto/setup.py`
- `apps/api/routers/user_mtproto/verification.py`
- `apps/mtproto/*` (infrastructure layer)

## 🧪 Quick Test

```bash
# Before refactoring
python3 scripts/guard_imports.py | grep "MTProto import"
# Output: 7 violations

# After refactoring
python3 scripts/guard_imports.py | grep "MTProto import"
# Output: 0 violations ✅
```

## 💡 Pro Tips

1. **Copy existing patterns**: Look at `TelegramValidationService` for service structure
2. **Use DI factories**: Check `bot_container.py` for provider examples
3. **Guard imports**: Always wrap `import telethon` in try/except
4. **Test incrementally**: Fix one router at a time
5. **Keep fallbacks**: Service should gracefully handle missing telethon

## 📞 Quick Reference

**Related PRs**:
- AlertsManagementService refactor (Service Locator fix)
- Smart Rules Generator (DI pattern example)

**Import Guard Script**: `scripts/guard_imports.py`
**DI Container**: `apps/di/bot_container.py`
**Service Examples**: `apps/api/services/telegram_validation_service.py`

---

**Estimated Time**: 1-2 hours for first router, 30 min for second
**Difficulty**: Medium (follow existing patterns)
