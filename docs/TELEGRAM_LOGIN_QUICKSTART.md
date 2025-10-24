# 🚀 Quick Start: Telegram Login (5 Minutes!)

## What You Need
- Your bot token from @BotFather
- HTTPS domain (or use localhost for testing)
- 5 minutes ⏱️

## Step 1: Add Environment Variables (30 seconds)

```bash
# Add to your .env file
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_BOT_USERNAME=YourAnalyticBot
TELEGRAM_LOGIN_ENABLED=true
FRONTEND_URL=https://your-domain.com
```

## Step 2: Database Migration (1 minute)

```bash
# Option A: Using Alembic (recommended)
alembic upgrade head

# Option B: Manual SQL
psql your_database << SQL
ALTER TABLE users ADD COLUMN telegram_id BIGINT UNIQUE;
ALTER TABLE users ADD COLUMN telegram_username VARCHAR(255);
ALTER TABLE users ADD COLUMN telegram_photo_url TEXT;
ALTER TABLE users ADD COLUMN telegram_verified BOOLEAN DEFAULT FALSE;
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
SQL
```

## Step 3: Test Backend (30 seconds)

```bash
# Start server
uvicorn apps.api.main:app --reload

# Check endpoints (open in browser)
http://localhost:8000/docs

# Should see 3 new endpoints:
# POST /api/auth/telegram/login
# GET /api/auth/telegram/callback  
# POST /api/auth/telegram/link
```

## Step 4: Add Widget to Frontend (2 minutes)

### HTML Version (Simplest)

```html
<!-- Add this to your login page -->
<script async src="https://telegram.org/js/telegram-widget.js?22"
        data-telegram-login="YourAnalyticBot"
        data-size="large"
        data-onauth="onTelegramAuth(user)">
</script>

<script>
function onTelegramAuth(user) {
    fetch('http://localhost:8000/api/auth/telegram/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(user)
    })
    .then(r => r.json())
    .then(data => {
        localStorage.setItem('access_token', data.access_token);
        window.location.href = '/dashboard';
    });
}
</script>
```

### React Version

```jsx
// Add to your LoginPage.jsx
import { TelegramLoginWidget } from './components/TelegramLogin';

<TelegramLoginWidget onAuth={(data) => {
    localStorage.setItem('access_token', data.access_token);
    navigate('/dashboard');
}} />
```

See full React code: `docs/examples/telegram_login_frontend.jsx`

## Step 5: Configure Bot (1 minute)

```
1. Open Telegram
2. Message @BotFather
3. Send: /mybots
4. Select your bot
5. Bot Settings → Domain
6. Enter: your-domain.com
   (or localhost for testing)
```

## Test It! (30 seconds)

1. Open your login page
2. Click "Sign in with Telegram"
3. Telegram app opens
4. Confirm your identity
5. You're logged in! 🎉

## That's It!

You now have Telegram login working! 🚀

## Next Steps

### Make it Pretty (Optional)
- Style the widget button
- Add loading states
- Add error messages

### Production Checklist
- [ ] Enable HTTPS (required for production)
- [ ] Test on mobile
- [ ] Add analytics tracking
- [ ] Monitor logs

### Learn More
- Full docs: `docs/TELEGRAM_LOGIN_WIDGET_GUIDE.md`
- Testing: `docs/TELEGRAM_LOGIN_TESTING.md`
- Deploy: `docs/TELEGRAM_LOGIN_DEPLOYMENT.md`
- Examples: `docs/examples/telegram_login_frontend.jsx`

## Troubleshooting

**Widget doesn't show?**
- Check bot username is correct
- Verify HTTPS (or localhost)
- Look in browser console

**401 error?**
- Verify bot token is correct
- Check it's in .env
- Restart server

**Can't find user?**
- Run database migration
- Check telegram_id column exists

## Support

Need help? Check:
1. `docs/TELEGRAM_LOGIN_TESTING.md` - Testing guide
2. `docs/TELEGRAM_LOGIN_DEPLOYMENT.md` - Deployment guide
3. Backend logs for errors

---

**Time to complete:** ~5 minutes  
**Difficulty:** Easy 🟢  
**Status:** Production ready ✅
