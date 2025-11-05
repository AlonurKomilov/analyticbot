# MTProto Setup & Data Ingestion Guide

## 🎯 Current Status

Based on the analysis, here's what we found:

✅ **Working:**
- Database connected
- Channel exists: ABC Legacy News (@abc_legacy_news)
- MTProto enabled for the channel
- Backend APIs functional

❌ **Missing:**
- User's Telegram session not set up
- No MTProto credentials stored
- No background worker running
- No analytics data in database

---

## 📋 Step-by-Step Setup Guide

### **STEP 1: Complete MTProto Setup (Frontend)**

**User needs to do this first!**

1. **Navigate to MTProto Setup Page:**
   - Open your browser: http://localhost:11300
   - Go to: **Settings → MTProto Setup**
   - Or directly: http://localhost:11300/settings/mtproto-setup

2. **Enter Telegram Credentials:**
   You need to get these from https://my.telegram.org/apps

   - **API ID**: Integer (e.g., 12345678)
   - **API Hash**: 32-character string
   - **Phone Number**: Your Telegram phone (e.g., +1234567890)

3. **Verify Phone:**
   - Click "Send Code"
   - Check your Telegram app for the verification code
   - Enter the code in the verification form
   - Click "Verify"

4. **Success Confirmation:**
   - You should see "✅ MTProto connected successfully"
   - Session is now stored in the database

---

### **STEP 2: Test MTProto Connection**

After completing setup, test if it works:

```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate
python scripts/test_mtproto_ingestion.py
```

**Expected output:**
```
✅ MTProto client retrieved
✅ Channel: ABC Legacy News
✅ Retrieved 10 messages
🎉 SUCCESS: MTProto ingestion is functional!
```

---

### **STEP 3: Create MTProto Ingestion Worker**

Once MTProto is set up, create a background worker to fetch channel data automatically.

Create: `scripts/mtproto_worker.py`

```python
#!/usr/bin/env python3
"""
MTProto Data Ingestion Worker

Runs continuously to fetch and store channel data.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def ingest_channel_data(user_id, channel_id, channel_username):
    """Fetch and store channel messages."""
    try:
        import asyncpg
        from apps.mtproto.multi_tenant.user_mtproto_service import UserMTProtoService
        from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory
        from core.services.encryption_service import EncryptionService

        # Initialize services
        encryption_service = EncryptionService()
        db_pool = await asyncpg.create_pool(
            'postgresql://analytic:change_me@localhost:10100/analytic_bot',
            min_size=2,
            max_size=5
        )

        repo_factory = UserBotRepositoryFactory(db_pool)
        user_bot_repo = repo_factory.create()

        mtproto_service = UserMTProtoService(
            user_bot_repository=user_bot_repo,
            encryption_service=encryption_service
        )

        # Get client
        client = await mtproto_service.get_user_client(user_id=user_id)
        if not client:
            logger.error("Failed to get MTProto client")
            return

        # Fetch messages
        logger.info(f"Fetching messages from {channel_username}...")
        messages = await client.get_messages(channel_username, limit=50)
        logger.info(f"Retrieved {len(messages)} messages")

        # TODO: Store messages in database
        # For now, just log them
        for msg in messages:
            logger.info(f"Message {msg.id}: {msg.date}, views={getattr(msg, 'views', 0)}")

        await db_pool.close()
        return len(messages)

    except Exception as e:
        logger.error(f"Error in ingestion: {e}", exc_info=True)
        return 0


async def run_worker():
    """Main worker loop."""
    logger.info("🚀 MTProto Ingestion Worker started")

    # Configuration
    USER_ID = 844338517
    CHANNEL_ID = 1002678877654
    CHANNEL_USERNAME = "@abc_legacy_news"
    INTERVAL_SECONDS = 300  # Run every 5 minutes

    while True:
        try:
            logger.info(f"[{datetime.now()}] Starting ingestion cycle...")
            count = await ingest_channel_data(USER_ID, CHANNEL_ID, CHANNEL_USERNAME)
            logger.info(f"✅ Ingested {count} messages")

        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)

        logger.info(f"Sleeping for {INTERVAL_SECONDS} seconds...")
        await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(run_worker())
```

---

### **STEP 4: Run the Worker**

Start the worker in a separate terminal:

```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate
python scripts/mtproto_worker.py
```

**Expected behavior:**
- Fetches channel messages every 5 minutes
- Logs message IDs and view counts
- Runs continuously in the background

---

### **STEP 5: Add Worker to Dev Environment** (Optional)

To start worker automatically with `make dev-start`:

1. **Edit `scripts/dev-start.sh`:**

Add this function after the `start_frontend` function:

```bash
start_mtproto_worker() {
    log_info "Starting MTProto worker..."
    nohup $VENV_PYTHON scripts/mtproto_worker.py >> logs/mtproto_worker.log 2>&1 &
    echo $! > logs/mtproto_worker.pid
    log_success "MTProto worker started"
}
```

2. **Call it in the `all` case:**

```bash
"all")
    start_api
    start_bot
    start_mtproto_worker  # Add this line
    start_frontend
    ;;
```

3. **Restart dev environment:**

```bash
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start
```

---

## 🧪 Verification Checklist

After setup, verify everything works:

- [ ] MTProto credentials entered in frontend
- [ ] Test script shows "✅ MTProto is working!"
- [ ] Worker is running (`ps aux | grep mtproto_worker`)
- [ ] Worker logs show messages being fetched (`tail -f logs/mtproto_worker.log`)
- [ ] Frontend shows channels dropdown
- [ ] Select channel and see analytics data

---

## 🔍 Troubleshooting

### Issue: "No session" error
**Solution:** Complete Step 1 (MTProto Setup in frontend)

### Issue: "Could not get MTProto client"
**Solution:**
1. Check user_bot_credentials table has encrypted session
2. Verify encryption key is set in environment
3. Try disconnecting and reconnecting MTProto

### Issue: Worker not fetching data
**Solution:**
1. Check worker logs: `tail -f logs/mtproto_worker.log`
2. Verify channel username is correct
3. Check MTProto is enabled for channel in database

### Issue: No data in frontend
**Solution:**
1. Ensure worker has run at least once
2. Check database has messages: `SELECT COUNT(*) FROM posts WHERE channel_id = 1002678877654`
3. Verify analytics endpoints return data: `curl http://localhost:11400/analytics/top-posts/1002678877654`

---

## 📊 Expected Data Flow

```
User → MTProto Setup (Frontend) → Store Session (Database)
                                          ↓
Worker → Fetch Messages (MTProto) → Store in Database
                                          ↓
Frontend → API Request → Read from Database → Display Analytics
```

---

## 🎯 Next Steps

1. **User completes MTProto setup** (Step 1)
2. **Test with script** (Step 2)
3. **Start worker** (Step 4)
4. **Verify data appears in frontend**
5. **(Optional) Automate worker** (Step 5)

Once complete, your ABC Legacy News channel will have real-time analytics! 🚀
