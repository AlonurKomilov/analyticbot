# Multi-Tenant Bot & MTProto Architecture Analysis

## Your Question
Can you create a system where:
1. Each user gets their own dedicated Telegram bot
2. Each user gets their own MTProto client
3. Each bot/client is isolated to only that user (not shared across 1000 users)
4. Admin and owner maintain full access to all bots
5. Users can only control their own bot

## Answer: YES, This Is Possible! ✅

Both **Telegram Bot API** and **MTProto** support multi-tenant architectures. Here's how:

---

## Current Architecture (Shared Model)

### What You Have Now:
```
┌─────────────────────────────────────────┐
│   Single Bot Token (BOT_TOKEN)         │
│   All 1000 users → Same Bot            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│   Single MTProto Session                │
│   API_ID + API_HASH (one session)      │
│   All users → Same client               │
└─────────────────────────────────────────┘
```

**Problems:**
- Rate limits shared across all users
- One user's actions affect others
- Security: users can potentially see each other's data
- Scalability: bottleneck at 1000+ users

---

## Recommended Architecture (Multi-Tenant Isolated Model)

### What You Should Build:

```
┌──────────────────────────────────────────────────────┐
│                  Platform (Your System)              │
│  Owner/Admin: Full control over all bots            │
└──────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼─────┐     ┌─────▼────┐     ┌─────▼────┐
   │ User 1   │     │ User 2   │     │ User N   │
   │          │     │          │     │          │
   │ Bot₁     │     │ Bot₂     │     │ BotN     │
   │ MTProto₁ │     │ MTProto₂ │     │ MTProtoN │
   └──────────┘     └──────────┘     └──────────┘
```

---

## Implementation Strategy

### 1. Multi-Tenant Bot System

#### Database Schema Addition:
```sql
-- Add to existing database
CREATE TABLE user_bot_credentials (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,

    -- Telegram Bot credentials (one per user)
    bot_token VARCHAR(255) UNIQUE NOT NULL,
    bot_username VARCHAR(255) UNIQUE,
    bot_id BIGINT UNIQUE,

    -- MTProto credentials (one per user)
    telegram_api_id INTEGER NOT NULL,
    telegram_api_hash VARCHAR(255) NOT NULL,
    telegram_phone VARCHAR(20),
    session_string TEXT,  -- Encrypted session data

    -- Status & Control
    status VARCHAR(50) DEFAULT 'active',  -- active, suspended, rate_limited
    is_verified BOOLEAN DEFAULT FALSE,

    -- Ownership & Permissions
    created_by_user_id BIGINT REFERENCES users(id),  -- Who created this bot
    managed_by_admin_id BIGINT,  -- Optional admin assignment

    -- Rate Limiting (per-user bot)
    rate_limit_rps FLOAT DEFAULT 1.0,
    max_concurrent_requests INTEGER DEFAULT 3,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,

    CONSTRAINT one_bot_per_user UNIQUE(user_id)
);

-- Index for admin queries
CREATE INDEX idx_bot_credentials_admin ON user_bot_credentials(managed_by_admin_id);
CREATE INDEX idx_bot_credentials_status ON user_bot_credentials(status);
```

#### Bot Instance Manager:
```python
# apps/bot/multi_tenant/bot_manager.py
from typing import Dict
from aiogram import Bot, Dispatcher
from pyrogram import Client

class UserBotInstance:
    """Isolated bot instance for a single user"""
    def __init__(self, user_id: int, credentials: dict):
        self.user_id = user_id
        self.bot_token = credentials['bot_token']
        self.api_id = credentials['telegram_api_id']
        self.api_hash = credentials['telegram_api_hash']

        # Aiogram bot (for bot API)
        self.bot: Bot = None
        self.dp: Dispatcher = None

        # Pyrogram client (for MTProto)
        self.mtproto_client: Client = None

        # Rate limiter (per user)
        self.rate_limiter = UserRateLimiter(
            rps=credentials.get('rate_limit_rps', 1.0)
        )

    async def initialize(self):
        """Initialize both bot and MTProto client"""
        # Initialize Bot API
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher()

        # Initialize MTProto client
        self.mtproto_client = Client(
            name=f"user_{self.user_id}_session",
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_string=self.session_string,  # Load from DB
        )
        await self.mtproto_client.start()

    async def shutdown(self):
        """Graceful shutdown"""
        if self.mtproto_client:
            await self.mtproto_client.stop()
        if self.bot:
            await self.bot.session.close()


class MultiTenantBotManager:
    """Manages all user bot instances"""

    def __init__(self):
        self.active_bots: Dict[int, UserBotInstance] = {}
        self.admin_access_tokens: Dict[int, str] = {}  # Admin override tokens

    async def get_or_create_user_bot(self, user_id: int) -> UserBotInstance:
        """Get existing or create new bot instance for user"""
        if user_id in self.active_bots:
            return self.active_bots[user_id]

        # Load from database
        credentials = await self.db.get_user_bot_credentials(user_id)
        if not credentials:
            raise ValueError(f"No bot configured for user {user_id}")

        # Create and initialize
        bot_instance = UserBotInstance(user_id, credentials)
        await bot_instance.initialize()

        self.active_bots[user_id] = bot_instance
        return bot_instance

    async def admin_access_user_bot(
        self,
        admin_id: int,
        target_user_id: int
    ) -> UserBotInstance:
        """Allow admin to access any user's bot"""
        # Verify admin permissions
        if not await self.is_admin(admin_id):
            raise PermissionError("Not authorized")

        # Return user's bot instance
        return await self.get_or_create_user_bot(target_user_id)

    async def shutdown_user_bot(self, user_id: int):
        """Shutdown and remove user bot from memory"""
        if user_id in self.active_bots:
            await self.active_bots[user_id].shutdown()
            del self.active_bots[user_id]
```

---

### 2. How Users Get Their Own Bot

#### User Onboarding Flow:

```python
# apps/api/routers/user_bot_setup.py
from fastapi import APIRouter, Depends
from apps.bot.multi_tenant.bot_manager import MultiTenantBotManager

router = APIRouter(prefix="/api/user-bot", tags=["User Bot Setup"])

@router.post("/create")
async def create_user_bot(
    bot_token: str,  # User provides from @BotFather
    telegram_api_id: int,  # User provides from my.telegram.org
    telegram_api_hash: str,  # User provides
    telegram_phone: str | None = None,  # Optional for MTProto
    current_user = Depends(get_current_user)
):
    """
    User provides their own bot credentials

    Steps:
    1. User creates bot via @BotFather → gets bot_token
    2. User gets API credentials from https://my.telegram.org
    3. User submits credentials here
    4. System validates and stores encrypted
    5. System initializes isolated bot instance
    """

    # Validate bot token
    bot_info = await validate_telegram_bot_token(bot_token)

    # Store credentials (encrypted)
    credentials = await db.create_user_bot_credentials(
        user_id=current_user.id,
        bot_token=encrypt(bot_token),  # Encrypt sensitive data!
        bot_username=bot_info['username'],
        bot_id=bot_info['id'],
        telegram_api_id=telegram_api_id,
        telegram_api_hash=encrypt(telegram_api_hash),
        telegram_phone=telegram_phone,
        created_by_user_id=current_user.id
    )

    # Initialize bot instance
    bot_manager = get_bot_manager()
    user_bot = await bot_manager.get_or_create_user_bot(current_user.id)

    return {
        "success": True,
        "bot_username": bot_info['username'],
        "message": "Your dedicated bot is now active!"
    }


@router.get("/status")
async def get_my_bot_status(current_user = Depends(get_current_user)):
    """Get current user's bot status"""
    credentials = await db.get_user_bot_credentials(current_user.id)

    if not credentials:
        return {"has_bot": False}

    return {
        "has_bot": True,
        "bot_username": credentials['bot_username'],
        "status": credentials['status'],
        "is_verified": credentials['is_verified'],
        "last_used": credentials['last_used_at'],
        "rate_limit": credentials['rate_limit_rps']
    }


@router.delete("/remove")
async def remove_my_bot(current_user = Depends(get_current_user)):
    """Remove user's bot (user can delete their own bot)"""
    bot_manager = get_bot_manager()

    # Shutdown bot instance
    await bot_manager.shutdown_user_bot(current_user.id)

    # Remove from database
    await db.delete_user_bot_credentials(current_user.id)

    return {"success": True, "message": "Bot removed successfully"}
```

---

### 3. Admin/Owner Control Panel

```python
# apps/api/routers/admin_bot_management.py
from fastapi import APIRouter, Depends
from apps.shared.auth import require_admin

router = APIRouter(prefix="/api/admin/bots", tags=["Admin Bot Management"])

@router.get("/list")
async def list_all_user_bots(
    admin = Depends(require_admin),
    status: str | None = None,
    page: int = 1,
    limit: int = 50
):
    """Admin: View all user bots in system"""
    bots = await db.get_all_user_bot_credentials(
        status=status,
        limit=limit,
        offset=(page - 1) * limit
    )

    return {
        "total": await db.count_user_bots(),
        "page": page,
        "bots": bots
    }


@router.post("/{user_id}/access")
async def admin_access_user_bot(
    user_id: int,
    admin = Depends(require_admin)
):
    """Admin: Get access to specific user's bot"""
    bot_manager = get_bot_manager()
    user_bot = await bot_manager.admin_access_user_bot(
        admin_id=admin.id,
        target_user_id=user_id
    )

    return {
        "success": True,
        "user_id": user_id,
        "bot_username": user_bot.credentials['bot_username'],
        "access_granted": True
    }


@router.patch("/{user_id}/suspend")
async def suspend_user_bot(
    user_id: int,
    reason: str,
    admin = Depends(require_admin)
):
    """Admin: Suspend user's bot"""
    await db.update_user_bot_status(
        user_id=user_id,
        status='suspended',
        reason=reason,
        suspended_by_admin_id=admin.id
    )

    # Shutdown bot instance
    bot_manager = get_bot_manager()
    await bot_manager.shutdown_user_bot(user_id)

    return {"success": True, "status": "suspended"}


@router.patch("/{user_id}/rate-limit")
async def update_user_bot_rate_limit(
    user_id: int,
    rps: float,
    max_concurrent: int,
    admin = Depends(require_admin)
):
    """Admin: Adjust user's bot rate limits"""
    await db.update_user_bot_rate_limit(
        user_id=user_id,
        rate_limit_rps=rps,
        max_concurrent_requests=max_concurrent
    )

    return {"success": True, "new_limits": {"rps": rps, "max_concurrent": max_concurrent}}
```

---

### 4. MTProto Multi-Tenant Implementation

```python
# apps/mtproto/multi_tenant/mtproto_manager.py
from pyrogram import Client
from typing import Dict

class UserMTProtoClient:
    """Isolated MTProto client for one user"""

    def __init__(self, user_id: int, credentials: dict):
        self.user_id = user_id
        self.client = Client(
            name=f"user_{user_id}_mtproto",
            api_id=credentials['telegram_api_id'],
            api_hash=credentials['telegram_api_hash'],
            phone_number=credentials.get('telegram_phone'),
            session_string=credentials.get('session_string'),
            workdir=f"./sessions/user_{user_id}/"  # Isolated session storage
        )

        self.rate_limiter = MTProtoRateLimiter(
            rps=credentials.get('rate_limit_rps', 0.5)
        )

    async def start(self):
        """Start MTProto client"""
        await self.client.start()

        # Save session string to database
        session_string = await self.client.export_session_string()
        await db.save_user_session_string(self.user_id, session_string)

    async def get_channel_stats(self, channel_id: str):
        """Get stats for user's channel (rate-limited)"""
        async with self.rate_limiter:
            return await self.client.get_chat(channel_id)


class MultiTenantMTProtoManager:
    """Manages MTProto clients for all users"""

    def __init__(self):
        self.active_clients: Dict[int, UserMTProtoClient] = {}

    async def get_user_client(self, user_id: int) -> UserMTProtoClient:
        """Get or create MTProto client for user"""
        if user_id not in self.active_clients:
            credentials = await db.get_user_bot_credentials(user_id)
            client = UserMTProtoClient(user_id, credentials)
            await client.start()
            self.active_clients[user_id] = client

        return self.active_clients[user_id]
```

---

## Security & Isolation

### 1. Credential Encryption
```python
from cryptography.fernet import Fernet

class CredentialVault:
    """Encrypt/decrypt user credentials"""

    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)

    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

### 2. User Isolation Middleware
```python
# Ensure users can only access their own bot
async def verify_user_bot_access(user_id: int, target_user_id: int, is_admin: bool = False):
    if not is_admin and user_id != target_user_id:
        raise PermissionError("Access denied: You can only control your own bot")
    return True
```

### 3. Admin Override System
```python
# Admin can access any user's bot with audit logging
async def admin_access_log(admin_id: int, target_user_id: int, action: str):
    await db.log_admin_action(
        admin_id=admin_id,
        target_user_id=target_user_id,
        action=action,
        timestamp=datetime.now()
    )
```

---

## Scaling Considerations

### For 1000+ Users:

1. **Connection Pooling**
   - Don't keep all 1000 bots in memory
   - Use LRU cache: keep most recently used 50-100 active
   - Lazy load: initialize bot only when user makes request

2. **Resource Limits**
   ```python
   class BotInstanceCache:
       def __init__(self, max_size=100):
           self.cache = LRUCache(max_size)

       async def get_bot(self, user_id: int):
           if user_id not in self.cache:
               # Load and evict least recently used
               bot = await self.load_user_bot(user_id)
               self.cache[user_id] = bot
           return self.cache[user_id]
   ```

3. **Distributed Architecture** (for 10,000+ users)
   ```
   ┌─────────────────────────────────┐
   │   Load Balancer                 │
   └──────────┬──────────────────────┘
              │
      ┌───────┼───────┐
      │       │       │
   ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
   │ Bot │ │ Bot │ │ Bot │
   │ Pod1│ │ Pod2│ │ Pod3│
   └─────┘ └─────┘ └─────┘
   Users   Users   Users
   1-333   334-666 667-1000
   ```

---

## Cost Analysis

### Per User:
- **Bot Token**: FREE (from @BotFather)
- **MTProto API credentials**: FREE (from Telegram)
- **Your Infrastructure**:
  - Database storage: ~1KB per user
  - Memory (when active): ~10MB per bot instance
  - CPU: Minimal (event-driven)

### For 1000 Users:
- **Storage**: ~1MB (negligible)
- **Memory** (if all active): ~10GB
- **Memory** (with LRU cache of 100): ~1GB ✅ Affordable

---

## Migration Path

### Phase 1: Database Setup
1. Create `user_bot_credentials` table
2. Add encryption keys to environment

### Phase 2: Bot Manager
1. Implement `MultiTenantBotManager`
2. Add user bot setup endpoints

### Phase 3: Frontend UI
1. Create "Setup Your Bot" page
2. Add admin bot management panel

### Phase 4: Migration
1. Keep existing shared bot for legacy users
2. New users get isolated bots
3. Gradually migrate old users

---

## Answer to Your Specific Questions

### ✅ Can one bot/MTProto work for only one user?
**YES!** Each user gets their own:
- Bot token (from @BotFather)
- MTProto session (separate API credentials)
- Isolated instance (no sharing)

### ✅ Can admin/owner access all bots?
**YES!** Admins can:
- View all user bots
- Access any user's bot
- Suspend/unsuspend bots
- Adjust rate limits
- View bot usage analytics

### ✅ Can users only control their own bot?
**YES!** Users can:
- Only access their bot instance
- View their bot's status
- Configure their bot settings
- Cannot see/access other users' bots

### ✅ Is this possible with Telegram?
**YES!** Telegram specifically designed for this:
- Unlimited bot creation (via @BotFather)
- Each bot is independent
- MTProto supports multiple sessions
- No restriction on number of apps

---

## Recommendation

**Implement the multi-tenant architecture!**

Benefits:
- ✅ True isolation per user
- ✅ No rate limit sharing
- ✅ Better security
- ✅ Scales to millions of users
- ✅ Admin maintains control
- ✅ Users manage their own bots

Start with:
1. Database schema (1 day)
2. Bot manager implementation (2 days)
3. API endpoints (1 day)
4. Frontend UI (2 days)

**Total: ~1 week to implement** 🚀
