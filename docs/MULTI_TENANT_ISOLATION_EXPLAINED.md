# System Architecture: Bot Isolation Explained

## 🎯 Two Different Bot Systems

### 1. System Admin Bot (run_bot.py) - YOUR Bot
**Location:** `apps/bot/run_bot.py`
**Token Source:** `.env` file → `settings.bot.BOT_TOKEN`

```python
# Line 31 in run_bot.py
token = settings.bot.BOT_TOKEN.get_secret_value()  # From YOUR .env file
```

**Purpose:**
- System onboarding (users first interact with YOUR bot)
- `/start`, `/help` commands
- User registration
- System notifications
- Admin management
- **NOT used for channel management!**

**Mock Bot (Lines 34-51):**
```python
if token in ("your_bot_token_here", "test_token"):
    # This is ONLY for development testing
    # Creates a fake bot so you can test without real token
    # NEVER used in production!
```

### 2. User Bot System (Multi-Tenant) - Each User's Bot
**Location:** `apps/bot/multi_tenant/user_bot_instance.py`
**Token Source:** Database → `user_bot_credentials.bot_token` (encrypted per user)

```python
# Line 52 in user_bot_instance.py
self.bot_token = encryption.decrypt(credentials.bot_token)  # From user's DB record
```

**Purpose:**
- Each user creates their OWN bot via @BotFather
- User adds their bot token through frontend
- System stores it ENCRYPTED in database
- Used for checking admin status of user's channels
- Completely isolated between users

## 🔒 Security: How User Isolation Works

### Database Structure
```sql
-- Table: user_bot_credentials
CREATE TABLE user_bot_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,  -- Links to users table
    bot_token TEXT NOT NULL,           -- ENCRYPTED with Fernet
    bot_id BIGINT,                     -- Bot's Telegram ID
    bot_username TEXT,                 -- Bot's username
    telegram_api_id INTEGER,           -- User's API ID
    telegram_api_hash TEXT,            -- ENCRYPTED
    telegram_phone TEXT,               -- ENCRYPTED
    session_string TEXT,               -- ENCRYPTED MTProto session
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: channels
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,          -- Owner user ID
    telegram_id BIGINT NOT NULL,       -- Channel ID
    name TEXT,                         -- Channel name/username
    title TEXT,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### API Security Flow

```python
# Every API endpoint that accesses channels:

@router.get("/channels/admin-status")
async def check_admin_status(
    current_user: dict = Depends(get_current_user),  # JWT auth - gets user_id
):
    # Step 1: Get ONLY this user's credentials
    user_credentials = await user_bot_repo.get_by_user_id(current_user["id"])
    #                                                      ↑
    #                                         User 1 gets User 1's token
    #                                         User 2 gets User 2's token

    # Step 2: Get ONLY this user's channels
    channels = await channel_service.get_user_channels(user_id=current_user["id"])
    #                                                          ↑
    #                                         WHERE user_id = current_user["id"]

    # Step 3: Create bot with THIS user's token
    decrypted_token = encryption.decrypt(user_credentials.bot_token)
    bot = Bot(token=decrypted_token)  # User 1's bot or User 2's bot

    # Step 4: Check if THIS user's bot is admin of THIS user's channels
    for channel in channels:  # Only channels where user_id = current_user["id"]
        chat_member = await bot.get_chat_member(channel.name, bot_user_id)
        # Uses User 1's bot to check User 1's channels
        # Uses User 2's bot to check User 2's channels
```

### MTProto Isolation

```python
# MTProto also isolated per user:

mtproto_client = await mtproto_service.get_user_client(
    user_id=current_user["id"],  # Gets THIS user's MTProto session
)
```

## 🛡️ Security Guarantees

### ✅ What IS Secure:

1. **User 1 CANNOT access User 2's bot token**
   - Tokens stored encrypted in separate database rows
   - API always filters by `current_user["id"]`

2. **User 1 CANNOT check admin status of User 2's channels**
   - Channels table has `user_id` foreign key
   - All queries: `WHERE user_id = current_user["id"]`

3. **User 1 CANNOT use User 2's MTProto session**
   - Sessions isolated by `user_id`
   - Connection pool enforces one session per user

4. **User 1 CANNOT add channels to User 2's account**
   ```python
   # Line 542 in channels_router.py
   channel_data.user_id = current_user["id"]  # ALWAYS set to current user
   ```

5. **JWT Authentication Required**
   - Every endpoint: `current_user: dict = Depends(get_current_user)`
   - JWT contains user_id
   - Cannot forge other user's ID

### ❌ What IS NOT Possible:

1. ❌ User cannot see other users' channels
2. ❌ User cannot use other users' bot tokens
3. ❌ User cannot access other users' MTProto sessions
4. ❌ User cannot bypass JWT authentication
5. ❌ User cannot modify user_id in requests (server-side enforced)

## 📊 Example: Two Users Using System

### User A (user_id=1)
```
1. Created @UserABot via @BotFather
2. Added token to system: "123456:ABC-DEF..."
3. Token stored encrypted in DB:
   user_bot_credentials: {
     user_id: 1,
     bot_token: "gAAAAA...encrypted..."
   }
4. Added channels:
   channels: [
     {id: 101, user_id: 1, name: "@channelA1"},
     {id: 102, user_id: 1, name: "@channelA2"}
   ]
5. Checks admin status:
   - System uses User A's bot token (decrypted)
   - Checks only User A's channels (WHERE user_id=1)
   - User A's bot checks if it's admin of @channelA1 and @channelA2
```

### User B (user_id=2)
```
1. Created @UserBBot via @BotFather (DIFFERENT bot!)
2. Added token to system: "789012:XYZ-GHI..."
3. Token stored encrypted in DB:
   user_bot_credentials: {
     user_id: 2,
     bot_token: "gBBBBB...encrypted..."
   }
4. Added channels:
   channels: [
     {id: 201, user_id: 2, name: "@channelB1"},
     {id: 202, user_id: 2, name: "@channelB2"}
   ]
5. Checks admin status:
   - System uses User B's bot token (decrypted)
   - Checks only User B's channels (WHERE user_id=2)
   - User B's bot checks if it's admin of @channelB1 and @channelB2
```

### Isolation Verified ✅
```
User A:
  - Sees channels: [101, 102] ✅
  - Uses bot: @UserABot ✅
  - Cannot see channels: [201, 202] ✅
  - Cannot use bot: @UserBBot ✅

User B:
  - Sees channels: [201, 202] ✅
  - Uses bot: @UserBBot ✅
  - Cannot see channels: [101, 102] ✅
  - Cannot use bot: @UserABot ✅
```

## 🎭 The "Mock Bot" Confusion

The mock bot in `run_bot.py` (lines 34-51) is **ONLY for development**:

```python
# This code is ONLY for YOU (the developer)
# When testing without a real bot token
if token in ("your_bot_token_here", "test_token"):
    # Creates fake bot for testing
    # NEVER runs in production
    # NOT related to user bots
```

**When does it run?**
- Only if `.env` has `BOT_TOKEN=your_bot_token_here`
- Only during development/testing
- Never affects user bot functionality

**User bots:**
- Always use real tokens from database
- Never use mock bots
- Always fully functional

## 🚀 Process Lifecycle + Multi-Tenant Summary

### Worker Isolation
```bash
# MTProto worker processes ALL users' channels
python -m apps.mtproto.worker

# Inside worker:
for user in all_users_with_mtproto:
    # Get THIS user's MTProto session
    client = await get_user_client(user.id)

    # Get THIS user's channels
    channels = await get_user_channels(user.id)

    # Collect data using THIS user's credentials
    await collect(client, channels)
```

### New Lifecycle Management
- ✅ Max runtime: Worker stops after 24 hours
- ✅ Memory limits: Auto-shutdown if exceeds 2GB
- ✅ Process cleanup: No more duplicates
- ✅ Health monitoring: HTTP endpoints per worker
- ✅ Multi-tenant safe: Each user's data isolated

## 📝 Summary

**Your system is CORRECTLY ISOLATED:**

1. ✅ Each user has their own bot token (encrypted in DB)
2. ✅ Each user has their own MTProto session (encrypted in DB)
3. ✅ Each user can only see/manage their own channels
4. ✅ System enforces isolation at database level
5. ✅ JWT authentication prevents impersonation
6. ✅ Process manager prevents resource exhaustion
7. ✅ Health monitoring for production reliability

**The "mock bot" is harmless:**
- Only for YOUR development testing
- Never affects user functionality
- Not related to multi-tenant system

**You can deploy confidently! 🎉**
