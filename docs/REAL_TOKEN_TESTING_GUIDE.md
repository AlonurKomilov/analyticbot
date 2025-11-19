# Testing Token Validator with Real Bot Token

## ⚠️ Security Notice

**NEVER share your bot tokens publicly or commit them to version control!**

Bot tokens give full access to your bot and should be treated like passwords.

---

## 📝 How to Get a Real Bot Token

### Step 1: Open Telegram and Find BotFather

1. Open your Telegram app (mobile or desktop)
2. Search for: `@BotFather` (official Telegram bot)
3. Start a chat with BotFather

### Step 2: Create a Test Bot

Send the following command to BotFather:
```
/newbot
```

BotFather will ask you:
1. **Bot name**: Enter any name (e.g., "My Test Bot")
2. **Bot username**: Must end with 'bot' (e.g., "my_test_validation_bot")

### Step 3: Get Your Token

BotFather will reply with a message containing your token:
```
Done! Congratulations on your new bot. You will find it at 
t.me/my_test_validation_bot. You can now add a description...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyzABCDE

For a description of the Bot API, see this page: 
https://core.telegram.org/bots/api
```

**Copy the token** (the long string after "Use this token to access the HTTP API:")

---

## 🧪 Testing with Your Real Token

### Option 1: Interactive Script (Recommended)

Run the interactive setup script:
```bash
cd /home/abcdeveloper/projects/analyticbot
./scripts/get_real_token_and_test.sh
```

The script will:
1. Guide you through getting a bot token
2. Let you paste your token securely
3. Run validation tests automatically

### Option 2: Manual Testing

1. **Set environment variable:**
   ```bash
   export TEST_BOT_TOKEN="your_actual_token_here"
   ```

2. **Run the test script:**
   ```bash
   python scripts/test_with_real_token.py
   ```

### Option 3: Use Existing Bot from Database

If you already have bots in your system:

```bash
# Get a token from your database
python -c "
import asyncio
import os
os.environ['ENV'] = 'development'

from infra.db.database import async_session_factory
from infra.db.repositories.user_bot_repository import UserBotRepository

async def get_token():
    async with async_session_factory() as session:
        repo = UserBotRepository(session)
        # Get first active bot
        bots = await repo.get_all_user_bots_for_admin()
        if bots:
            bot = bots[0]
            print(f'Bot ID: {bot.id}')
            print(f'User ID: {bot.user_id}')
            # Token is encrypted, would need to decrypt
            print('Note: Token is encrypted in database')
            return bot.encrypted_bot_token
    return None

asyncio.run(get_token())
"
```

---

## 📊 What the Tests Will Do

The test script will:

1. **Validate Token Format**
   - Check if token matches Telegram's format: `botid:secret`
   - Verify the secret part is at least 35 characters

2. **Live Connection Test**
   - Actually connect to Telegram's API
   - Retrieve bot information
   - Verify the token works

3. **Display Bot Information**
   - Bot ID
   - Bot username
   - Bot name
   - Bot capabilities (groups, reading messages)

4. **Test Invalid Tokens**
   - Verify invalid tokens are correctly detected
   - Check error messages are helpful

---

## ✅ Expected Output (Success)

```
==============================================================
🧪 Testing Token Validator with Real Token
==============================================================

Test 1: Format Validation
------------------------------------------------------------
Token format valid: True
✅ Token format is valid

Test 2: Live Validation (connecting to Telegram)
------------------------------------------------------------
Status: valid
Valid: True
Message: Token is valid
Bot ID: 1234567890
Bot Username: @my_test_bot
Bot Name: My Test Bot
Validated at: 2025-11-19T10:30:45.123456

✅ Token is VALID and connected successfully!

Token Details:
  - Bot ID: 1234567890
  - Username: @my_test_bot
  - First Name: My Test Bot
  - Can Join Groups: True
  - Can Read Messages: False

Test 3: Invalid Token Test
------------------------------------------------------------
Token 'invalid_token...': ❌ Invalid (expected)
Token '123:short...': ❌ Invalid (expected)
Token 'not_a_token...': ❌ Invalid (expected)
Token '123456789:SHORT...': ❌ Invalid (expected)

Testing invalid token with live validation...
Status: invalid
Valid: False
Message: Invalid bot token format

✅ Invalid token correctly detected

==============================================================
📊 Test Summary
==============================================================
✅ Real token validation: PASSED
✅ Invalid token detection: PASSED

🎉 All tests PASSED!
==============================================================
```

---

## 🔒 Security Best Practices

### DO:
- ✅ Use environment variables for tokens
- ✅ Create test bots for development
- ✅ Revoke test bot tokens after testing
- ✅ Keep tokens in `.env` files (never commit)
- ✅ Use different bots for dev/staging/prod

### DON'T:
- ❌ Share tokens in chat or email
- ❌ Commit tokens to git
- ❌ Use production bot tokens for testing
- ❌ Share tokens in screenshots
- ❌ Hardcode tokens in source code

### Revoking a Token

If you accidentally expose a token:

1. Open Telegram
2. Go to @BotFather
3. Send: `/mybots`
4. Select your bot
5. Click "API Token"
6. Click "Revoke current token"
7. Get a new token

---

## 🐛 Troubleshooting

### "Token format is invalid"

Your token doesn't match the expected format. Check:
- Token should be like: `123456789:ABCdefGHIjklMNOpqrs...`
- Should have a colon (`:`)
- Number before colon (bot ID)
- At least 35 characters after colon

### "Unauthorized: Bot token is invalid"

- Token might be revoked
- Token might be copied incorrectly (check for spaces)
- Go to @BotFather and check `/mybots`

### "Network error"

- Check your internet connection
- Telegram API might be temporarily down
- Try again in a few seconds

### "TEST_BOT_TOKEN not set"

You need to set the environment variable:
```bash
export TEST_BOT_TOKEN="your_token_here"
```

---

## 📖 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [BotFather Commands](https://core.telegram.org/bots#6-botfather)
- [Bot Security Best Practices](https://core.telegram.org/bots/faq#what-makes-telegram-bots-cool)

---

**Created:** November 19, 2025  
**Purpose:** Safe testing of token validator with real Telegram bot tokens  
**Security Level:** Test environment only
