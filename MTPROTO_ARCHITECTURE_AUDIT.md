# MTProto Architecture Audit & Recommendations
**Date:** October 29, 2025
**Project:** AnalyticBot
**Focus:** Bot API vs MTProto User Client Separation

---

## 🎯 **EXECUTIVE SUMMARY**

Your project **ALREADY HAS** the correct architecture for separating:
1. **Telegram Bot API** (for sending posts) - per user
2. **MTProto User Clients** (for reading channel history) - per user

However, there are some areas that need clarification and potential improvement.

---

## ✅ **WHAT'S CORRECTLY IMPLEMENTED**

### 1. User-Specific Bot Credentials Table

**Table:** `user_bot_credentials`

```sql
Columns:
- id                       (Primary Key)
- user_id                  (Links to specific user)
- bot_token                (Telegram Bot API token)
- bot_username             (Bot username)
- bot_id                   (Telegram bot ID)
- telegram_api_id          (MTProto API ID) ✅
- telegram_api_hash        (MTProto API Hash) ✅
- telegram_phone           (User's phone for MTProto) ✅
- session_string           (MTProto session data) ✅
- status                   (active/suspended)
- is_verified              (verification status)
- rate_limit_rps           (rate limiting)
- max_concurrent_requests  (concurrent limit)
```

**This is PERFECT** - You have:
- ✅ Per-user bot tokens (Bot API)
- ✅ Per-user MTProto credentials (API ID, API Hash, Phone)
- ✅ Per-user session storage
- ✅ Proper isolation between users

### 2. Frontend Bot Setup Flow

**Located:** `apps/frontend/src/features/...` (as shown in screenshots)

Your UI already has:
- ✅ Step 1: Bot Credentials (Bot Token)
- ✅ Step 2: API Configuration (Telegram API ID/Hash for MTProto)
- ✅ Step 3: Rate Limits
- ✅ Step 4: Verification

This is the **CORRECT** separation!

### 3. Multi-Tenant Bot Manager

**File:** `apps/bot/multi_tenant/bot_manager.py`

From startup logs:
```
✅ Multi-tenant bot manager initialized
```

This suggests you have a system for managing multiple user bots.

---

## ⚠️ **ISSUES & CONFUSION POINTS**

### Issue 1: Global MTProto Config vs Per-User MTProto

**Problem:** The `apps/mtproto/config.py` has **GLOBAL** settings:

```python
# Global MTProto settings (apps/mtproto/config.py)
MTPROTO_ENABLED: bool = False
TELEGRAM_API_ID: int | None = None  # <-- GLOBAL
TELEGRAM_API_HASH: str | None = None  # <-- GLOBAL
TELEGRAM_SESSION_NAME: str = "mtproto_session"  # <-- GLOBAL
MTPROTO_PEERS: list[str] = []  # <-- GLOBAL channels
```

But you also have **PER-USER** MTProto credentials in `user_bot_credentials`:
```sql
telegram_api_id    | bigint  <-- PER USER
telegram_api_hash  | varchar <-- PER USER
telegram_phone     | varchar <-- PER USER
session_string     | text    <-- PER USER
```

**This creates confusion:**
- Should MTProto use global config or per-user credentials?
- How does the system know which session to use for which user?

### Issue 2: Single TelethonTGClient vs Multi-User

**File:** `infra/tg/telethon_client.py`

```python
class TelethonTGClient:
    def __init__(self, settings: MTProtoConfigProtocol):
        # Uses GLOBAL settings
        self.settings = settings
        self._client = TelegramClient(
            session=self.settings.TELEGRAM_SESSION_NAME,  # <-- One session
            api_id=self.settings.TELEGRAM_API_ID,
            api_hash=self.settings.TELEGRAM_API_HASH,
        )
```

**Problem:**
- This creates ONE Telegram client with ONE session
- But you have MULTIPLE users with MULTIPLE MTProto credentials
- How do you handle user-specific MTProto sessions?

### Issue 3: Bot Manager Logs But No Visible Multi-Tenant MTProto

When I tested your system:
- ✅ Bot manager initialized
- ✅ User has bot configured (@abc_control_copyright_bot)
- ✅ user_bot_credentials table exists
- ❌ NO per-user MTProto session management visible
- ❌ NO way for users to add their API ID/Hash via API

---

## 📋 **RECOMMENDED ARCHITECTURE**

### Separation of Concerns:

```
┌─────────────────────────────────────────────────────────┐
│                        USER                              │
│                                                          │
│  ┌────────────────────┐    ┌─────────────────────────┐  │
│  │  TELEGRAM BOT API  │    │   MTPROTO USER CLIENT   │  │
│  │  (Send Posts)      │    │   (Read History)        │  │
│  ├────────────────────┤    ├─────────────────────────┤  │
│  │ • Bot Token        │    │ • API ID                │  │
│  │ • Bot Username     │    │ • API Hash              │  │
│  │ • Bot ID           │    │ • Phone Number          │  │
│  │                    │    │ • Session String        │  │
│  ├────────────────────┤    ├─────────────────────────┤  │
│  │ USES:              │    │ USES:                   │  │
│  │ • Send messages    │    │ • Read channel history  │  │
│  │ • Post content     │    │ • Fetch posts           │  │
│  │ • Manage channels  │    │ • Get analytics         │  │
│  │ • Receive commands │    │ • Monitor updates       │  │
│  └────────────────────┘    └─────────────────────────┘  │
│                                                          │
│  STORED IN: user_bot_credentials (id=1)                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     ADMIN/SYSTEM                         │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         GLOBAL MTPROTO (Optional)                   │ │
│  │         For system-wide operations                  │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ • System API ID/Hash                                │ │
│  │ • System Session                                    │ │
│  │ • Background jobs                                   │ │
│  │ • Demo mode                                         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  STORED IN: Environment (.env) OR admin settings        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 **IMPLEMENTATION RECOMMENDATIONS**

### 1. Create User MTProto Service

**New File:** `apps/bot/services/user_mtproto_service.py`

```python
class UserMTProtoService:
    """Manages user-specific MTProto clients"""

    def __init__(self):
        self._client_pool: dict[int, TelethonTGClient] = {}

    async def get_user_client(self, user_id: int) -> TelethonTGClient | None:
        """Get or create MTProto client for specific user"""

        # Check if client already exists
        if user_id in self._client_pool:
            return self._client_pool[user_id]

        # Load user credentials from database
        creds = await self._load_user_credentials(user_id)

        if not creds or not creds.telegram_api_id:
            return None  # User hasn't configured MTProto

        # Create user-specific settings
        user_settings = MTProtoUserSettings(
            api_id=creds.telegram_api_id,
            api_hash=creds.telegram_api_hash,
            phone=creds.telegram_phone,
            session_string=creds.session_string,
            session_name=f"user_{user_id}_session"
        )

        # Create client
        client = TelethonTGClient(user_settings)
        await client.start()

        # Cache it
        self._client_pool[user_id] = client

        return client

    async def _load_user_credentials(self, user_id: int):
        """Load from user_bot_credentials table"""
        # Query database for user's MTProto credentials
        pass
```

### 2. Add API Endpoints for User MTProto Setup

**New File:** `apps/api/routers/user_mtproto_router.py`

```python
@router.post("/api/user-mtproto/setup")
async def setup_user_mtproto(
    data: UserMTProtoSetup,
    current_user: User = Depends(get_current_user)
):
    """
    Allow users to configure their MTProto credentials

    Body:
    {
        "telegram_api_id": 12345,
        "telegram_api_hash": "abc123...",
        "telegram_phone": "+1234567890"
    }
    """
    # Store in user_bot_credentials table
    # Initiate Telegram auth flow
    # Return verification code request
    pass

@router.post("/api/user-mtproto/verify")
async def verify_user_mtproto(
    data: UserMTProtoVerify,
    current_user: User = Depends(get_current_user)
):
    """
    Verify MTProto setup with code from Telegram

    Body:
    {
        "verification_code": "12345"
    }
    """
    # Complete Telegram auth
    # Store session_string in database
    # Mark as verified
    pass

@router.get("/api/user-mtproto/status")
async def get_user_mtproto_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's MTProto configuration status

    Returns:
    {
        "configured": true,
        "verified": true,
        "phone": "+123****890",
        "last_used": "2025-10-29T12:00:00Z"
    }
    """
    pass
```

### 3. Separate Frontend Components

**Bot Setup (existing):**
```
apps/frontend/src/features/bot-setup/
├── BotCredentials.tsx          (Bot Token - for Bot API)
├── BotAPIConfiguration.tsx     (REMOVE - move to MTProto)
├── BotRateLimits.tsx
└── BotVerification.tsx
```

**MTProto Setup (new):**
```
apps/frontend/src/features/mtproto-setup/
├── MTProtoCredentials.tsx      (API ID, API Hash, Phone)
├── MTProtoVerification.tsx     (Verification code input)
├── MTProtoStatus.tsx           (Connection status)
└── MTProtoSettings.tsx         (Session management)
```

### 4. Update Database Model

**File:** `infra/db/models/user_bot.py` (if exists, or create it)

```python
class UserBotCredentials(Base):
    __tablename__ = "user_bot_credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Bot API credentials (for sending)
    bot_token = Column(String)
    bot_username = Column(String)
    bot_id = Column(BigInteger)

    # MTProto credentials (for reading)
    telegram_api_id = Column(BigInteger, nullable=True)
    telegram_api_hash = Column(String, nullable=True)
    telegram_phone = Column(String, nullable=True)
    session_string = Column(Text, nullable=True)  # Encrypted session

    # Status
    status = Column(String, default="pending")
    is_bot_verified = Column(Boolean, default=False)
    is_mtproto_verified = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### 5. Clear Naming Convention

**Use Case 1: Send Posts (Bot API)**
- Service: `BotService` or `TelegramBotService`
- Config: Bot Token
- User sees: "Bot Setup" section
- Purpose: Send scheduled posts, manage channel

**Use Case 2: Read History (MTProto)**
- Service: `MTProtoService` or `UserMTProtoService`
- Config: API ID, API Hash, Phone, Session
- User sees: "MTProto Setup" or "Telegram User Client" section
- Purpose: Fetch channel history, analyze posts

---

## 🎨 **UI/UX RECOMMENDATIONS**

### Current Confusion:

Your screenshot shows "API Configuration" in Bot Setup, which mixes concepts:
- Bot Token (Bot API) ← belongs in "Bot Setup"
- API ID/Hash (MTProto) ← belongs in separate "MTProto Setup"

### Recommended UI Flow:

```
Settings → Integrations
├── 📱 Telegram Bot
│   ├── Bot Token: 8468166027:AAHwR...
│   ├── Username: @abc_control_copyright_bot
│   ├── Status: ✅ Active
│   ├── Permissions: Send Messages, Manage Chat
│   └── [Test Bot Connection]
│
└── 👤 Telegram User Client (MTProto)
    ├── API ID: (not configured)
    ├── API Hash: (not configured)
    ├── Phone: (not configured)
    ├── Status: ❌ Not Configured
    ├── [Setup MTProto]
    └── ℹ️ "Required for: Channel history, Post analytics, Read messages"
```

---

## 📝 **STEP-BY-STEP IMPLEMENTATION PLAN**

### Phase 1: Clarify Existing Code (1-2 days)

1. **Audit current code:**
   - Check if `UserMTProtoService` or similar exists
   - Verify how `user_bot_credentials` table is currently used
   - Find existing API endpoints for bot/mtproto setup

2. **Document current state:**
   - Map out which files handle Bot API vs MTProto
   - Identify any mixed concerns

### Phase 2: Backend Separation (3-5 days)

1. **Create user MTProto service:**
   - `apps/bot/services/user_mtproto_service.py`
   - Pool management for user-specific clients
   - Session lifecycle management

2. **Add API endpoints:**
   - `/api/user-mtproto/setup` (POST)
   - `/api/user-mtproto/verify` (POST)
   - `/api/user-mtproto/status` (GET)
   - `/api/user-mtproto/disconnect` (POST)

3. **Update bot manager:**
   - Separate bot pool from MTProto client pool
   - Ensure proper isolation

### Phase 3: Frontend Separation (2-3 days)

1. **Create new MTProto setup flow:**
   - New page: `/settings/mtproto-setup`
   - Separate from bot setup
   - Clear visual distinction

2. **Update bot setup:**
   - Remove API ID/Hash fields
   - Keep only Bot Token
   - Add link to MTProto setup with explanation

### Phase 4: Testing & Documentation (2-3 days)

1. **Test scenarios:**
   - User with only Bot (can send, can't read history)
   - User with only MTProto (can read, can't send)
   - User with both (full functionality)
   - Multiple users with their own credentials

2. **Create user documentation:**
   - "How to get Bot Token from @BotFather"
   - "How to get API ID/Hash from my.telegram.org"
   - "Difference between Bot and MTProto"

---

## 🚨 **CRITICAL SECURITY NOTES**

### 1. Encrypt Sensitive Data

```python
# NEVER store in plaintext!
session_string = Column(Text)  # ← Should be encrypted!
telegram_api_hash = Column(String)  # ← Should be encrypted!
bot_token = Column(String)  # ← Should be encrypted!
```

**Recommendation:** Use encryption at rest:
```python
from cryptography.fernet import Fernet

class EncryptedField:
    def encrypt(self, value: str) -> str:
        # Encrypt using app secret key
        pass

    def decrypt(self, value: str) -> str:
        # Decrypt when needed
        pass
```

### 2. User Isolation

**CRITICAL:** Each user's MTProto client must ONLY access:
- Their own channels
- Their own data
- Their own permissions

**Implement:**
```python
async def fetch_channel_history(user_id: int, channel_id: int):
    # Verify user owns this channel
    if not await verify_channel_ownership(user_id, channel_id):
        raise PermissionError("Channel not owned by user")

    # Get user's MTProto client
    client = await mtproto_service.get_user_client(user_id)

    # Fetch history
    history = await client.iter_history(channel_id)
```

### 3. Rate Limiting Per User

```python
# In user_bot_credentials table
rate_limit_rps = Column(Numeric)  # ← Already exists! ✅
max_concurrent_requests = Column(Integer)  # ← Already exists! ✅

# Apply per user:
@rate_limit(key=lambda user_id: f"user_{user_id}_mtproto", limit="30/minute")
async def fetch_posts(user_id: int, channel_id: int):
    pass
```

---

## 💡 **QUICK WINS**

### 1. Add MTProto Status Endpoint (30 min)

```python
# apps/api/routers/user_bot_router.py

@router.get("/api/user-bot/mtproto-status")
async def get_mtproto_status(current_user: User = Depends(get_current_user)):
    """Check if user has MTProto configured"""
    # Query user_bot_credentials
    creds = await db.fetch_one(
        "SELECT telegram_api_id, telegram_api_hash, session_string FROM user_bot_credentials WHERE user_id = $1",
        current_user.id
    )

    return {
        "configured": bool(creds and creds['telegram_api_id']),
        "verified": bool(creds and creds['session_string']),
        "can_read_history": bool(creds and creds['session_string']),
        "needs_setup": not (creds and creds['telegram_api_id'])
    }
```

### 2. Update Frontend to Show Status (1 hour)

```typescript
// In dashboard or settings
const { data: mtprotoStatus } = useQuery('mtproto-status', () =>
  apiClient.get('/api/user-bot/mtproto-status')
);

{!mtprotoStatus?.configured && (
  <Alert severity="info">
    <AlertTitle>Enable Channel History Analysis</AlertTitle>
    To analyze your channel's post history, set up MTProto User Client.
    <Button href="/settings/mtproto-setup">Configure Now</Button>
  </Alert>
)}
```

### 3. Clear Documentation in UI (2 hours)

Add info boxes explaining the difference:

```tsx
<InfoCard>
  <Typography variant="h6">🤖 Telegram Bot</Typography>
  <Typography>
    Used for: Sending scheduled posts, managing your channel
    <br />
    Requires: Bot Token from @BotFather
    <br />
    Status: ✅ Active
  </Typography>
</InfoCard>

<InfoCard>
  <Typography variant="h6">👤 MTProto User Client</Typography>
  <Typography>
    Used for: Reading channel history, analyzing posts, fetching metrics
    <br />
    Requires: API ID & Hash from my.telegram.org
    <br />
    Status: ❌ Not configured
    <br />
    <Button>Set Up Now</Button>
  </Typography>
</InfoCard>
```

---

## 📊 **EXPECTED OUTCOMES**

After implementing these recommendations:

✅ **Users will understand:**
- Bot Token = for sending messages
- MTProto = for reading channel history
- They are separate and serve different purposes

✅ **Architecture will be clear:**
- One bot per user (Bot API)
- One MTProto client per user (optional)
- Proper isolation between users

✅ **Security will improve:**
- Per-user credentials
- Encrypted storage
- Proper access control

✅ **Functionality will work:**
- Users can send posts (Bot API)
- Users can analyze history (MTProto)
- System can operate in "send-only" mode without MTProto

---

## 🎯 **SUMMARY & NEXT STEPS**

### What You Have (Good!):
- ✅ Database schema supports per-user MTProto
- ✅ Frontend has setup wizard (but mixing concepts)
- ✅ Multi-tenant bot manager exists

### What Needs Fixing:
- ⚠️ Clarify Global vs Per-User MTProto
- ⚠️ Separate Bot Setup from MTProto Setup in UI
- ⚠️ Create user MTProto service/pool
- ⚠️ Add API endpoints for MTProto management
- ⚠️ Encrypt sensitive credentials

### Priority Order:
1. **High:** Add MTProto status endpoint (shows what's missing)
2. **High:** Update UI to separate Bot vs MTProto setup
3. **Medium:** Implement user MTProto service
4. **Medium:** Add MTProto setup/verification endpoints
5. **Low:** Optimize caching/pooling

---

## 🚀 **DETAILED IMPLEMENTATION PLAN**

### **PHASE 1: Foundation & Audit (Day 1-2)**

#### Task 1.1: Code Discovery & Mapping (4 hours)
**Goal:** Understand what already exists

```bash
# Search for existing MTProto user management
grep -r "user_bot_credentials" apps/ infra/
grep -r "UserMTProto" apps/
grep -r "get_user_client" apps/

# Check existing API endpoints
grep -r "@router.*mtproto" apps/api/routers/
grep -r "@router.*user.*bot" apps/api/routers/

# Find frontend bot setup pages
find apps/frontend/src -name "*bot*" -o -name "*mtproto*"
```

**Deliverables:**
- [ ] Document of existing MTProto-related code
- [ ] List of files that need modification
- [ ] Identification of code duplication/confusion

#### Task 1.2: Database Schema Verification (2 hours)
**Goal:** Confirm database structure

```sql
-- Verify user_bot_credentials structure
\d+ user_bot_credentials

-- Check for existing MTProto sessions
SELECT
    user_id,
    bot_username,
    telegram_api_id IS NOT NULL as has_mtproto_id,
    telegram_api_hash IS NOT NULL as has_mtproto_hash,
    session_string IS NOT NULL as has_session,
    status
FROM user_bot_credentials;

-- Check if encryption is used
SELECT
    LENGTH(session_string) as session_length,
    LEFT(session_string, 10) as session_preview
FROM user_bot_credentials
WHERE session_string IS NOT NULL;
```

**Deliverables:**
- [ ] Confirmed table structure
- [ ] Sample data analysis
- [ ] Encryption status report
- [ ] Migration scripts (if schema changes needed)

#### Task 1.3: Create Test Plan (2 hours)
**Goal:** Define success criteria

**Test Scenarios:**
1. User without any setup
2. User with only Bot Token
3. User with only MTProto
4. User with both Bot + MTProto
5. Multiple users with separate credentials
6. User disconnecting/reconnecting MTProto

**Deliverables:**
- [ ] Test case document
- [ ] Test data creation script
- [ ] Acceptance criteria checklist

---

### **PHASE 2: Backend - MTProto Service (Day 3-5)**

#### Task 2.1: Create User MTProto Service (6 hours)

**File:** `apps/bot/services/user_mtproto_service.py`

```python
"""
User-specific MTProto client management service.
Each user gets their own isolated Telegram client for reading channel history.
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from telethon import TelegramClient
from telethon.sessions import StringSession

from infra.db.repositories.user_bot_repository import UserBotRepository

logger = logging.getLogger(__name__)


class UserMTProtoClient:
    """Wrapper for user-specific Telethon client"""

    def __init__(
        self,
        user_id: int,
        api_id: int,
        api_hash: str,
        session_string: str,
    ):
        self.user_id = user_id
        self.api_id = api_id
        self.api_hash = api_hash
        self._client: Optional[TelegramClient] = None
        self._session_string = session_string
        self._last_used = datetime.utcnow()
        self._is_connected = False

    async def connect(self) -> bool:
        """Connect to Telegram"""
        try:
            if self._client and self._is_connected:
                return True

            # Create client with StringSession
            session = StringSession(self._session_string)
            self._client = TelegramClient(
                session,
                api_id=self.api_id,
                api_hash=self.api_hash,
            )

            await self._client.connect()

            # Verify authorization
            if not await self._client.is_user_authorized():
                logger.error(f"User {self.user_id} MTProto session expired")
                return False

            self._is_connected = True
            self._last_used = datetime.utcnow()

            logger.info(f"User {self.user_id} MTProto client connected")
            return True

        except Exception as e:
            logger.error(f"Failed to connect user {self.user_id} MTProto: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Telegram"""
        if self._client:
            await self._client.disconnect()
            self._is_connected = False
            logger.info(f"User {self.user_id} MTProto client disconnected")

    @property
    def client(self) -> TelegramClient:
        """Get underlying Telethon client"""
        if not self._client or not self._is_connected:
            raise RuntimeError("Client not connected. Call connect() first.")

        self._last_used = datetime.utcnow()
        return self._client

    @property
    def last_used(self) -> datetime:
        return self._last_used


class UserMTProtoService:
    """
    Manages pool of user-specific MTProto clients.
    Ensures proper isolation between users.
    """

    def __init__(self, user_bot_repo: UserBotRepository):
        self.user_bot_repo = user_bot_repo
        self._client_pool: Dict[int, UserMTProtoClient] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._max_idle_minutes = 30

    async def get_user_client(self, user_id: int) -> Optional[UserMTProtoClient]:
        """
        Get or create MTProto client for user.
        Returns None if user hasn't configured MTProto.
        """
        # Check pool first
        if user_id in self._client_pool:
            client = self._client_pool[user_id]
            if client._is_connected:
                return client
            # Reconnect if disconnected
            if await client.connect():
                return client
            # Connection failed, remove from pool
            del self._client_pool[user_id]

        # Load credentials from database
        credentials = await self.user_bot_repo.get_user_credentials(user_id)

        if not credentials:
            logger.warning(f"No credentials found for user {user_id}")
            return None

        # Check if MTProto is configured
        if not all([
            credentials.get('telegram_api_id'),
            credentials.get('telegram_api_hash'),
            credentials.get('session_string'),
        ]):
            logger.info(f"User {user_id} has not configured MTProto")
            return None

        # Create new client
        try:
            client = UserMTProtoClient(
                user_id=user_id,
                api_id=credentials['telegram_api_id'],
                api_hash=credentials['telegram_api_hash'],
                session_string=credentials['session_string'],
            )

            # Connect
            if not await client.connect():
                logger.error(f"Failed to connect MTProto client for user {user_id}")
                return None

            # Add to pool
            self._client_pool[user_id] = client

            logger.info(f"Created and cached MTProto client for user {user_id}")
            return client

        except Exception as e:
            logger.error(f"Error creating MTProto client for user {user_id}: {e}")
            return None

    async def disconnect_user(self, user_id: int):
        """Disconnect and remove user's MTProto client"""
        if user_id in self._client_pool:
            client = self._client_pool[user_id]
            await client.disconnect()
            del self._client_pool[user_id]
            logger.info(f"Disconnected and removed MTProto client for user {user_id}")

    async def cleanup_idle_clients(self):
        """Remove idle clients to free resources"""
        from datetime import timedelta

        now = datetime.utcnow()
        max_idle = timedelta(minutes=self._max_idle_minutes)

        to_remove = []
        for user_id, client in self._client_pool.items():
            if now - client.last_used > max_idle:
                to_remove.append(user_id)

        for user_id in to_remove:
            await self.disconnect_user(user_id)
            logger.info(f"Cleaned up idle MTProto client for user {user_id}")

    async def start_cleanup_task(self):
        """Start background task to cleanup idle clients"""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(300)  # Every 5 minutes
                try:
                    await self.cleanup_idle_clients()
                except Exception as e:
                    logger.error(f"Error in cleanup task: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop_cleanup_task(self):
        """Stop cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def shutdown(self):
        """Disconnect all clients and stop cleanup"""
        await self.stop_cleanup_task()

        for user_id in list(self._client_pool.keys()):
            await self.disconnect_user(user_id)

        logger.info("UserMTProtoService shutdown complete")


# Global instance (initialized in DI container)
_user_mtproto_service: Optional[UserMTProtoService] = None


async def get_user_mtproto_service() -> UserMTProtoService:
    """Dependency injection helper"""
    global _user_mtproto_service
    if not _user_mtproto_service:
        from apps.di import get_container
        container = get_container()
        user_bot_repo = await container.user_bot.user_bot_repository()
        _user_mtproto_service = UserMTProtoService(user_bot_repo)
        await _user_mtproto_service.start_cleanup_task()
    return _user_mtproto_service
```

**Implementation Steps:**
1. [ ] Create file and basic structure
2. [ ] Implement UserMTProtoClient class
3. [ ] Implement UserMTProtoService with pool management
4. [ ] Add connection/disconnection logic
5. [ ] Add idle client cleanup
6. [ ] Add comprehensive logging
7. [ ] Write unit tests

**Testing:**
```python
# Test script
async def test_user_mtproto_service():
    service = await get_user_mtproto_service()

    # Test user without MTProto
    client1 = await service.get_user_client(999999)
    assert client1 is None

    # Test user with MTProto
    client2 = await service.get_user_client(844338517)
    assert client2 is not None
    assert client2._is_connected

    # Test pool caching
    client3 = await service.get_user_client(844338517)
    assert client3 is client2  # Same instance

    # Test disconnect
    await service.disconnect_user(844338517)
    assert 844338517 not in service._client_pool
```

#### Task 2.2: Create MTProto API Endpoints (8 hours)

**File:** `apps/api/routers/user_mtproto_router.py`

```python
"""
User MTProto Management API
Allows users to configure their personal MTProto credentials
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError

from apps.api.auth_utils import get_current_user
from apps.mtproto.multi_tenant.user_mtproto_service import get_user_mtproto_service
from infra.db.repositories.user_bot_repository import UserBotRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user-mtproto", tags=["User MTProto"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MTProtoSetupRequest(BaseModel):
    """Initial MTProto setup with API credentials"""
    telegram_api_id: int = Field(..., description="Telegram API ID from my.telegram.org")
    telegram_api_hash: str = Field(..., description="Telegram API Hash from my.telegram.org")
    telegram_phone: str = Field(..., description="Phone number with country code")

    @validator('telegram_phone')
    def validate_phone(cls, v):
        # Basic validation
        if not v.startswith('+'):
            raise ValueError('Phone must start with +')
        if len(v) < 10:
            raise ValueError('Phone number too short')
        return v


class MTProtoVerifyRequest(BaseModel):
    """Verification code from Telegram"""
    verification_code: str = Field(..., description="Code received via Telegram")
    phone_code_hash: str = Field(..., description="Hash from initial request")
    password: Optional[str] = Field(None, description="2FA password if enabled")


class MTProtoStatusResponse(BaseModel):
    """Current MTProto configuration status"""
    configured: bool
    verified: bool
    phone: Optional[str] = None  # Masked
    api_id: Optional[int] = None
    connected: bool = False
    last_used: Optional[datetime] = None
    can_read_history: bool = False


class MTProtoSetupResponse(BaseModel):
    """Response after initiating setup"""
    success: bool
    phone_code_hash: str
    message: str


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_user_bot_repo() -> UserBotRepository:
    """Get user bot repository"""
    from apps.di import get_container
    container = get_container()
    return await container.user_bot.user_bot_repository()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/status", response_model=MTProtoStatusResponse)
async def get_mtproto_status(
    current_user = Depends(get_current_user),
    user_bot_repo: UserBotRepository = Depends(get_user_bot_repo),
):
    """
    Get user's MTProto configuration status

    Returns information about whether MTProto is configured and working.
    """
    try:
        # Get credentials from database
        credentials = await user_bot_repo.get_user_credentials(current_user.id)

        if not credentials:
            return MTProtoStatusResponse(
                configured=False,
                verified=False,
                can_read_history=False,
            )

        has_api_id = credentials.get('telegram_api_id') is not None
        has_api_hash = credentials.get('telegram_api_hash') is not None
        has_session = credentials.get('session_string') is not None

        configured = has_api_id and has_api_hash
        verified = configured and has_session

        # Check if client is connected
        connected = False
        last_used = None

        if verified:
            mtproto_service = await get_user_mtproto_service()
            client = await mtproto_service.get_user_client(current_user.id)
            if client:
                connected = client._is_connected
                last_used = client.last_used

        # Mask phone number
        phone = credentials.get('telegram_phone')
        if phone and len(phone) > 6:
            phone = phone[:4] + "****" + phone[-3:]

        return MTProtoStatusResponse(
            configured=configured,
            verified=verified,
            phone=phone,
            api_id=credentials.get('telegram_api_id') if configured else None,
            connected=connected,
            last_used=last_used,
            can_read_history=verified and connected,
        )

    except Exception as e:
        logger.error(f"Error getting MTProto status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MTProto status"
        )


@router.post("/setup", response_model=MTProtoSetupResponse)
async def setup_mtproto(
    request: MTProtoSetupRequest,
    current_user = Depends(get_current_user),
    user_bot_repo: UserBotRepository = Depends(get_user_bot_repo),
):
    """
    Initiate MTProto setup by sending verification code to phone

    Steps:
    1. User provides API ID, API Hash, and Phone
    2. System sends verification code to phone
    3. User receives code and calls /verify endpoint
    """
    try:
        # Create temporary Telethon client
        client = TelegramClient(
            StringSession(),
            api_id=request.telegram_api_id,
            api_hash=request.telegram_api_hash,
        )

        await client.connect()

        # Send code request
        phone_code_hash = await client.send_code_request(request.telegram_phone)

        await client.disconnect()

        # Store pending configuration (without session yet)
        await user_bot_repo.update_user_mtproto_credentials(
            user_id=current_user.id,
            telegram_api_id=request.telegram_api_id,
            telegram_api_hash=request.telegram_api_hash,
            telegram_phone=request.telegram_phone,
            session_string=None,  # Will be set after verification
        )

        logger.info(f"MTProto setup initiated for user {current_user.id}")

        return MTProtoSetupResponse(
            success=True,
            phone_code_hash=phone_code_hash.phone_code_hash,
            message=f"Verification code sent to {request.telegram_phone}"
        )

    except Exception as e:
        logger.error(f"Error setting up MTProto for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup MTProto: {str(e)}"
        )


@router.post("/verify")
async def verify_mtproto(
    request: MTProtoVerifyRequest,
    current_user = Depends(get_current_user),
    user_bot_repo: UserBotRepository = Depends(get_user_bot_repo),
):
    """
    Verify MTProto setup with code from Telegram

    Completes the authentication flow and stores the session.
    """
    try:
        # Get pending credentials
        credentials = await user_bot_repo.get_user_credentials(current_user.id)

        if not credentials or not credentials.get('telegram_api_id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending MTProto setup found. Call /setup first."
            )

        # Create client with stored credentials
        session = StringSession()
        client = TelegramClient(
            session,
            api_id=credentials['telegram_api_id'],
            api_hash=credentials['telegram_api_hash'],
        )

        await client.connect()

        try:
            # Sign in with verification code
            await client.sign_in(
                phone=credentials['telegram_phone'],
                code=request.verification_code,
                phone_code_hash=request.phone_code_hash,
            )

        except SessionPasswordNeededError:
            # 2FA is enabled
            if not request.password:
                await client.disconnect()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="2FA is enabled. Please provide password."
                )

            # Sign in with password
            await client.sign_in(password=request.password)

        except PhoneCodeInvalidError:
            await client.disconnect()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Get session string
        session_string = session.save()

        await client.disconnect()

        # Store session in database
        await user_bot_repo.update_user_mtproto_credentials(
            user_id=current_user.id,
            telegram_api_id=credentials['telegram_api_id'],
            telegram_api_hash=credentials['telegram_api_hash'],
            telegram_phone=credentials['telegram_phone'],
            session_string=session_string,
        )

        logger.info(f"MTProto verification successful for user {current_user.id}")

        return {
            "success": True,
            "message": "MTProto setup completed successfully",
            "verified": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MTProto for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify MTProto: {str(e)}"
        )


@router.post("/disconnect")
async def disconnect_mtproto(
    current_user = Depends(get_current_user),
    user_bot_repo: UserBotRepository = Depends(get_user_bot_repo),
):
    """
    Disconnect and remove MTProto configuration

    This will:
    1. Disconnect active client
    2. Remove session from database
    3. Keep API ID/Hash for easy reconnection
    """
    try:
        # Disconnect from service
        mtproto_service = await get_user_mtproto_service()
        await mtproto_service.disconnect_user(current_user.id)

        # Clear session from database (keep API credentials)
        await user_bot_repo.update_user_mtproto_credentials(
            user_id=current_user.id,
            session_string=None,
        )

        logger.info(f"MTProto disconnected for user {current_user.id}")

        return {
            "success": True,
            "message": "MTProto disconnected successfully"
        }

    except Exception as e:
        logger.error(f"Error disconnecting MTProto for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect MTProto"
        )


@router.delete("/remove")
async def remove_mtproto(
    current_user = Depends(get_current_user),
    user_bot_repo: UserBotRepository = Depends(get_user_bot_repo),
):
    """
    Completely remove MTProto configuration

    This will remove all MTProto credentials including API ID/Hash.
    """
    try:
        # Disconnect first
        mtproto_service = await get_user_mtproto_service()
        await mtproto_service.disconnect_user(current_user.id)

        # Remove all MTProto data from database
        await user_bot_repo.update_user_mtproto_credentials(
            user_id=current_user.id,
            telegram_api_id=None,
            telegram_api_hash=None,
            telegram_phone=None,
            session_string=None,
        )

        logger.info(f"MTProto configuration removed for user {current_user.id}")

        return {
            "success": True,
            "message": "MTProto configuration removed successfully"
        }

    except Exception as e:
        logger.error(f"Error removing MTProto for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove MTProto configuration"
        )
```

**Implementation Steps:**
1. [ ] Create router file
2. [ ] Implement status endpoint
3. [ ] Implement setup endpoint (send code)
4. [ ] Implement verify endpoint (complete auth)
5. [ ] Implement disconnect/remove endpoints
6. [ ] Add error handling
7. [ ] Write API tests

**Testing:**
```bash
# Test status (not configured)
curl -X GET http://localhost:11400/api/user-mtproto/status \
  -H "Authorization: Bearer $TOKEN"

# Test setup
curl -X POST http://localhost:11400/api/user-mtproto/setup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_api_id": 12345,
    "telegram_api_hash": "abc123...",
    "telegram_phone": "+1234567890"
  }'

# Test verify
curl -X POST http://localhost:11400/api/user-mtproto/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "verification_code": "12345",
    "phone_code_hash": "..."
  }'
```

#### Task 2.3: Update Repository (2 hours)

**File:** `infra/db/repositories/user_bot_repository.py`

Add these methods:

```python
async def get_user_credentials(self, user_id: int) -> dict | None:
    """Get user's bot and MTProto credentials"""
    query = """
        SELECT
            bot_token,
            bot_username,
            bot_id,
            telegram_api_id,
            telegram_api_hash,
            telegram_phone,
            session_string,
            status,
            is_verified
        FROM user_bot_credentials
        WHERE user_id = $1
    """
    return await self.pool.fetchrow(query, user_id)

async def update_user_mtproto_credentials(
    self,
    user_id: int,
    telegram_api_id: int | None = None,
    telegram_api_hash: str | None = None,
    telegram_phone: str | None = None,
    session_string: str | None = None,
):
    """Update user's MTProto credentials"""
    query = """
        UPDATE user_bot_credentials
        SET
            telegram_api_id = COALESCE($2, telegram_api_id),
            telegram_api_hash = COALESCE($3, telegram_api_hash),
            telegram_phone = COALESCE($4, telegram_phone),
            session_string = COALESCE($5, session_string),
            updated_at = NOW()
        WHERE user_id = $1
        RETURNING id
    """
    result = await self.pool.fetchrow(
        query,
        user_id,
        telegram_api_id,
        telegram_api_hash,
        telegram_phone,
        session_string,
    )
    return result is not None
```

#### Task 2.4: Register Router in Main App (30 min)

**File:** `apps/api/main.py`

```python
# Add import
from apps.api.routers.user_mtproto_router import router as user_mtproto_router

# Register router
app.include_router(user_mtproto_router)  # /api/user-mtproto/*
```

---

### **PHASE 3: Frontend - Separate UI (Day 6-8)**

#### Task 3.1: Create MTProto Setup Pages (6 hours)

**Directory Structure:**
```
apps/frontend/src/features/mtproto-setup/
├── index.tsx                      # Main export
├── MTProtoSetupPage.tsx          # Setup wizard container
├── MTProtoStatusCard.tsx         # Status display component
├── MTProtoCredentialsForm.tsx    # API ID/Hash/Phone form
├── MTProtoVerificationForm.tsx   # Code verification form
├── hooks/
│   ├── useMTProtoStatus.ts      # Status query hook
│   ├── useMTProtoSetup.ts       # Setup mutation hook
│   └── useMTProtoVerify.ts      # Verify mutation hook
└── types.ts                      # TypeScript interfaces
```

**File:** `apps/frontend/src/features/mtproto-setup/MTProtoSetupPage.tsx`

```typescript
import React, { useState } from 'react';
import {
  Container,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Typography,
  Box,
  Alert,
  Button,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import MTProtoStatusCard from './MTProtoStatusCard';
import MTProtoCredentialsForm from './MTProtoCredentialsForm';
import MTProtoVerificationForm from './MTProtoVerificationForm';
import { useMTProtoStatus } from './hooks/useMTProtoStatus';

const steps = [
  'Get API Credentials',
  'Enter Credentials',
  'Verify Phone',
  'Complete',
];

export const MTProtoSetupPage: React.FC = () => {
  const { data: status, isLoading } = useMTProtoStatus();
  const [activeStep, setActiveStep] = useState(0);
  const [phoneCodeHash, setPhoneCodeHash] = useState<string>('');

  // Determine initial step based on status
  React.useEffect(() => {
    if (status) {
      if (status.verified) {
        setActiveStep(3); // Complete
      } else if (status.configured) {
        setActiveStep(2); // Need verification
      } else {
        setActiveStep(1); // Need credentials
      }
    }
  }, [status]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          MTProto Setup
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          Configure MTProto to enable reading channel history and analyzing posts.
        </Typography>

        {/* Current Status */}
        <MTProtoStatusCard status={status} />

        {/* Setup Wizard */}
        <Paper sx={{ p: 3, mt: 3 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Step Content */}
          {activeStep === 0 && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <strong>Step 1: Get Telegram API Credentials</strong>
                </Typography>
                <Typography variant="body2">
                  You need to obtain API credentials from Telegram:
                </Typography>
                <ol style={{ marginTop: 8, marginBottom: 8 }}>
                  <li>Visit{' '}
                    <a
                      href="https://my.telegram.org/apps"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      my.telegram.org/apps
                    </a>
                  </li>
                  <li>Log in with your phone number</li>
                  <li>Click "API development tools"</li>
                  <li>Fill out the form (App title, Short name, Platform, Description)</li>
                  <li>Copy your <strong>api_id</strong> and <strong>api_hash</strong></li>
                </ol>
              </Alert>

              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Button disabled>Back</Button>
                <Button
                  variant="contained"
                  onClick={() => setActiveStep(1)}
                >
                  I Have My Credentials
                </Button>
              </Box>
            </Box>
          )}

          {activeStep === 1 && (
            <MTProtoCredentialsForm
              onSuccess={(hash) => {
                setPhoneCodeHash(hash);
                setActiveStep(2);
              }}
              onBack={() => setActiveStep(0)}
            />
          )}

          {activeStep === 2 && (
            <MTProtoVerificationForm
              phoneCodeHash={phoneCodeHash}
              onSuccess={() => setActiveStep(3)}
              onBack={() => setActiveStep(1)}
            />
          )}

          {activeStep === 3 && (
            <Box>
              <Alert severity="success">
                <Typography variant="subtitle2" gutterBottom>
                  <strong>✅ MTProto Setup Complete!</strong>
                </Typography>
                <Typography variant="body2">
                  Your MTProto user client is now configured and connected.
                  You can now:
                </Typography>
                <ul style={{ marginTop: 8, marginBottom: 0 }}>
                  <li>Read channel message history</li>
                  <li>Analyze existing posts</li>
                  <li>Fetch detailed channel analytics</li>
                  <li>Monitor channel updates in real-time</li>
                </ul>
              </Alert>

              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  href="/channels"
                >
                  Go to Channels
                </Button>
                <Button
                  variant="contained"
                  href="/analytics"
                >
                  View Analytics
                </Button>
              </Box>
            </Box>
          )}
        </Paper>

        {/* Help Section */}
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            What is MTProto?
          </Typography>
          <Typography variant="body2" paragraph>
            MTProto is Telegram's protocol that allows your application to act as a real
            Telegram user. This is different from your bot:
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 2 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                🤖 Telegram Bot
              </Typography>
              <Typography variant="body2">
                • Send messages<br />
                • Receive commands<br />
                • Manage channels<br />
                • ❌ Cannot read history
              </Typography>
            </Paper>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                👤 MTProto Client
              </Typography>
              <Typography variant="body2">
                • Read all messages<br />
                • Access full history<br />
                • Get detailed analytics<br />
                • ✅ Full channel access
              </Typography>
            </Paper>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default MTProtoSetupPage;
```

**File:** `apps/frontend/src/features/mtproto-setup/MTProtoCredentialsForm.tsx`

```typescript
import React from 'react';
import {
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useMTProtoSetup } from './hooks/useMTProtoSetup';

interface FormData {
  telegram_api_id: number;
  telegram_api_hash: string;
  telegram_phone: string;
}

interface Props {
  onSuccess: (phoneCodeHash: string) => void;
  onBack: () => void;
}

export const MTProtoCredentialsForm: React.FC<Props> = ({ onSuccess, onBack }) => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
  const setupMutation = useMTProtoSetup();

  const onSubmit = async (data: FormData) => {
    try {
      const result = await setupMutation.mutateAsync(data);
      if (result.success) {
        onSuccess(result.phone_code_hash);
      }
    } catch (error) {
      console.error('Setup failed:', error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)}>
      {setupMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {setupMutation.error?.message || 'Failed to setup MTProto'}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Telegram API ID"
        type="number"
        margin="normal"
        {...register('telegram_api_id', {
          required: 'API ID is required',
          min: { value: 1, message: 'Invalid API ID' },
        })}
        error={!!errors.telegram_api_id}
        helperText={errors.telegram_api_id?.message || 'Numeric ID from my.telegram.org'}
      />

      <TextField
        fullWidth
        label="Telegram API Hash"
        margin="normal"
        {...register('telegram_api_hash', {
          required: 'API Hash is required',
          minLength: { value: 32, message: 'API Hash must be at least 32 characters' },
        })}
        error={!!errors.telegram_api_hash}
        helperText={errors.telegram_api_hash?.message || '32+ character hash from my.telegram.org'}
      />

      <TextField
        fullWidth
        label="Phone Number"
        placeholder="+1234567890"
        margin="normal"
        {...register('telegram_phone', {
          required: 'Phone number is required',
          pattern: {
            value: /^\+\d{10,15}$/,
            message: 'Phone must start with + and contain 10-15 digits',
          },
        })}
        error={!!errors.telegram_phone}
        helperText={errors.telegram_phone?.message || 'Your Telegram phone number with country code'}
      />

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button onClick={onBack} disabled={setupMutation.isLoading}>
          Back
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={setupMutation.isLoading}
          startIcon={setupMutation.isLoading && <CircularProgress size={20} />}
        >
          {setupMutation.isLoading ? 'Sending Code...' : 'Send Verification Code'}
        </Button>
      </Box>
    </Box>
  );
};

export default MTProtoCredentialsForm;
```

**Continue in next task...**

---

**Want me to implement any of these recommendations? Just let me know which part to start with!**
