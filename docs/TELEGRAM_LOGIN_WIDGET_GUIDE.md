# 🔐 Telegram Login Widget Implementation Guide

## Overview

This guide shows how to implement "Sign in with Telegram" functionality for your AnalyticBot web application. Users can authenticate using their Telegram account without needing a password.

## 🎯 How It Works

1. User clicks "Sign in with Telegram" button on your login page
2. Telegram widget opens → user confirms login in Telegram app
3. Telegram sends encrypted user data back to your website
4. Your backend validates the data and creates a session
5. User is logged in automatically

## 📱 Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Web Frontend  │ ◄─────► │   Telegram   │ ◄─────► │  Your Backend   │
│  (Login Page)   │         │   Servers    │         │  (FastAPI API)  │
└─────────────────┘         └──────────────┘         └─────────────────┘
        │                                                      │
        │                                                      │
        └──────────────── Validated Auth Data ────────────────┘
```

## 🔧 Implementation Steps

### Step 1: Get Your Bot Token

You already have a bot token. Use the same bot that users interact with for analytics.

Your bot username: `@YourAnalyticBot` (get from BotFather)

### Step 2: Backend - Create Telegram Login Endpoint

Create a new file: `apps/api/routers/auth/telegram_login.py`

This endpoint will:
- Validate Telegram data authenticity
- Create or find user by Telegram ID
- Generate JWT tokens
- Return auth response

### Step 3: Frontend - Add Telegram Login Widget

Add to your login page:

```html
<!-- Option 1: Telegram Widget (Recommended) -->
<script async src="https://telegram.org/js/telegram-widget.js?22"
        data-telegram-login="YOUR_BOT_USERNAME"
        data-size="large"
        data-auth-url="https://your-api.com/api/auth/telegram/callback"
        data-request-access="write">
</script>

<!-- Option 2: Manual Button with Redirect -->
<button onclick="loginWithTelegram()">
  <img src="telegram-icon.svg" alt="Telegram" />
  Sign in with Telegram
</button>
```

### Step 4: Validate Telegram Data

Telegram sends data that must be validated using your bot token. The validation ensures the data actually came from Telegram.

## 🔒 Security

### Data Validation

Telegram sends these fields:
- `id` - User's Telegram ID
- `first_name` - First name
- `last_name` - Last name (optional)
- `username` - Telegram username (optional)
- `photo_url` - Profile photo URL (optional)
- `auth_date` - Timestamp
- `hash` - HMAC-SHA256 signature

**Validation Algorithm:**

```python
import hashlib
import hmac

def validate_telegram_auth(data: dict, bot_token: str) -> bool:
    """
    Validate that auth data came from Telegram.
    
    Returns True if valid, False otherwise.
    """
    # Extract hash
    received_hash = data.get('hash')
    if not received_hash:
        return False
    
    # Create data check string
    check_data = []
    for key in sorted(data.keys()):
        if key != 'hash':
            check_data.append(f"{key}={data[key]}")
    
    data_check_string = '\n'.join(check_data)
    
    # Create secret key
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Calculate hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare hashes
    return calculated_hash == received_hash
```

### Session Validation

- Check `auth_date` is recent (within 24 hours)
- Store Telegram ID in user database
- Generate standard JWT tokens

## 📊 Database Schema

Add to your `users` table:

```sql
ALTER TABLE users ADD COLUMN telegram_id BIGINT UNIQUE;
ALTER TABLE users ADD COLUMN telegram_username VARCHAR(255);
ALTER TABLE users ADD COLUMN telegram_photo_url TEXT;
ALTER TABLE users ADD COLUMN telegram_verified BOOLEAN DEFAULT FALSE;
```

## 🎨 User Experience Flow

### New User (First Time Login)

1. Clicks "Sign in with Telegram"
2. Telegram confirms identity
3. Backend creates new account automatically
4. User lands on dashboard (no password needed!)

### Existing User (Already Has Account)

**Option A: Auto-Link (Recommended)**
1. User clicks "Link Telegram Account" in profile settings
2. Telegram confirms
3. Next time: can login with either email/password OR Telegram

**Option B: Email Verification Link**
1. User logs in with Telegram
2. Backend asks for email to link accounts
3. Sends verification email
4. User confirms → accounts linked

## 🔄 Migration Strategy

### Phase 1: Add Telegram Login Option
- Keep existing email/password login
- Add "Sign in with Telegram" button
- Users can choose either method

### Phase 2: Encourage Telegram
- Show "Link your Telegram for faster login" banner
- Offer benefits (faster support, direct notifications)

### Phase 3: Telegram-First (Optional)
- Make Telegram login primary
- Keep email/password as fallback

## 🧪 Testing

### Test Cases

1. ✅ New user signs in with Telegram → creates account
2. ✅ Existing user links Telegram → updates profile
3. ✅ User with Telegram linked logs in → no password needed
4. ✅ Invalid hash → rejected
5. ✅ Expired auth_date → rejected
6. ✅ User can still use email/password if Telegram linked

## 🚀 Deployment

### Environment Variables

```bash
# .env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=YourAnalyticBot
TELEGRAM_LOGIN_ENABLED=true
TELEGRAM_AUTH_EXPIRY_HOURS=24
```

### Frontend Config

```javascript
// config.js
export const TELEGRAM_LOGIN = {
  enabled: process.env.REACT_APP_TELEGRAM_LOGIN_ENABLED === 'true',
  botUsername: process.env.REACT_APP_TELEGRAM_BOT_USERNAME,
  authUrl: `${process.env.REACT_APP_API_URL}/api/auth/telegram/callback`
};
```

## 📱 Mini Apps vs Login Widget

### Telegram Login Widget (This Guide)
- ✅ Works on any website
- ✅ Standard web authentication
- ✅ Opens Telegram app for confirmation
- ✅ Returns to your website
- 👉 **Best for your use case**

### Telegram Mini Apps (Different Use Case)
- Runs inside Telegram
- Full app embedded in chat
- No external website needed
- Different API (WebApp API)

## 🎯 Next Steps

1. Review the implementation files being created
2. Test in development environment
3. Add frontend button
4. Test with real Telegram account
5. Deploy to production

## 📚 References

- [Telegram Login Widget Docs](https://core.telegram.org/widgets/login)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Authentication Best Practices](https://core.telegram.org/widgets/login#checking-authorization)

## ❓ FAQ

**Q: Do users need to have the bot started?**
A: No! The login widget works even if user never interacted with your bot.

**Q: Can I use this with Mini Apps?**
A: Yes, but that's a different feature. This is for web authentication.

**Q: Is it secure?**
A: Yes, Telegram uses cryptographic signatures. Always validate the hash!

**Q: What if user has no Telegram username?**
A: That's fine! Use their Telegram ID (always available) and first/last name.

**Q: Can I get user's phone number?**
A: Not through Login Widget. You'd need Bot API with special permissions.
