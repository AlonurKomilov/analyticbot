# 🚀 Telegram Login Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Variables

Add to your `.env` file:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=YourAnalyticBot
TELEGRAM_LOGIN_ENABLED=true
TELEGRAM_AUTH_EXPIRY_HOURS=24

# Frontend URL (for redirects)
FRONTEND_URL=https://your-domain.com

# Required for HTTPS (production only)
FORCE_HTTPS=true
```

### 2. Database Migration

```bash
# Run the Telegram fields migration
alembic upgrade head

# Or manually:
psql your_database < docs/migrations/telegram_auth_migration.py
```

Verify columns added:
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users'
  AND column_name LIKE 'telegram%';
```

Should show:
- telegram_id (bigint)
- telegram_username (varchar)
- telegram_photo_url (text)
- telegram_verified (boolean)

### 3. Bot Configuration

#### Get Bot Username from BotFather

```
1. Open Telegram
2. Search for @BotFather
3. Send: /mybots
4. Select your bot
5. Click "Bot Settings" → "Domain"
6. Add: your-domain.com
```

This tells Telegram your domain is authorized to use the Login Widget.

### 4. HTTPS Setup (REQUIRED!)

⚠️ **Telegram Login Widget REQUIRES HTTPS**

**Option A: Use Nginx with Let's Encrypt**

```nginx
# /etc/nginx/sites-available/analyticbot

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend (React)
    location / {
        root /var/www/analyticbot-frontend;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

**Option B: Use Cloudflare**

1. Add your domain to Cloudflare
2. Enable "Full SSL" mode
3. Cloudflare handles HTTPS automatically

### 5. CORS Configuration

Update FastAPI CORS settings:

```python
# apps/api/main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://www.your-domain.com",
        "http://localhost:3000",  # Development only
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Frontend Build

Update frontend environment:

```bash
# .env.production
REACT_APP_API_URL=https://your-domain.com
REACT_APP_TELEGRAM_BOT_USERNAME=YourAnalyticBot
REACT_APP_TELEGRAM_LOGIN_ENABLED=true
```

Build:
```bash
cd frontend
npm run build
```

## Deployment Steps

### Step 1: Deploy Backend

```bash
# Pull latest code
cd /home/abcdeveloper/projects/analyticbot
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart backend
sudo systemctl restart analyticbot-api
```

### Step 2: Deploy Frontend

```bash
# Build frontend
cd frontend
npm install
npm run build

# Copy to web server
sudo cp -r build/* /var/www/analyticbot-frontend/

# Restart nginx
sudo systemctl restart nginx
```

### Step 3: Verify Endpoints

```bash
# Check API health
curl https://your-domain.com/api/health

# Check Telegram endpoints exist
curl https://your-domain.com/api/docs
# Look for: /api/auth/telegram/login, /api/auth/telegram/callback
```

### Step 4: Test Telegram Widget

1. Open: https://your-domain.com/login
2. Click "Sign in with Telegram"
3. Confirm in Telegram app
4. Should redirect back and log you in

## Post-Deployment Verification

### ✅ Checklist

- [ ] **HTTPS works** - Widget won't load without it
- [ ] **Bot domain configured** in BotFather
- [ ] **Environment variables** set correctly
- [ ] **Database migration** completed
- [ ] **CORS** allows your domain
- [ ] **Telegram widget** appears on login page
- [ ] **Test login** with real Telegram account
- [ ] **Tokens generated** correctly
- [ ] **User created** in database
- [ ] **Profile shows** Telegram info
- [ ] **Can logout** and login again
- [ ] **Mobile works** (test on phone)
- [ ] **Error handling** works (try invalid data)

### 🔍 Monitoring

Add logging for Telegram logins:

```python
# In telegram_login.py - already added

logger.info(f"Successful Telegram login: {user.username} (TG ID: {telegram_data.id})")
logger.warning("Telegram auth hash validation failed")
logger.error(f"Telegram login error: {e}")
```

Watch logs:
```bash
tail -f /var/log/analyticbot/api.log | grep "Telegram"
```

### 📊 Analytics

Track Telegram logins:

```sql
-- Count Telegram users
SELECT COUNT(*)
FROM users
WHERE telegram_id IS NOT NULL;

-- Recent Telegram logins
SELECT username, telegram_username, last_login
FROM users
WHERE telegram_verified = true
ORDER BY last_login DESC
LIMIT 10;

-- Telegram vs Email logins
SELECT
    CASE
        WHEN telegram_id IS NOT NULL THEN 'Telegram'
        ELSE 'Email/Password'
    END as auth_method,
    COUNT(*) as user_count
FROM users
GROUP BY auth_method;
```

## Rollback Plan

If something goes wrong:

### 1. Disable Telegram Login (Quick)

```bash
# Set environment variable
export TELEGRAM_LOGIN_ENABLED=false

# Restart API
sudo systemctl restart analyticbot-api
```

Frontend: Comment out Telegram widget in login page.

### 2. Revert Database Migration

```bash
# Rollback migration
alembic downgrade -1

# Or manually:
ALTER TABLE users DROP COLUMN telegram_id;
ALTER TABLE users DROP COLUMN telegram_username;
ALTER TABLE users DROP COLUMN telegram_photo_url;
ALTER TABLE users DROP COLUMN telegram_verified;
```

### 3. Revert Code

```bash
git revert <commit_hash>
git push origin main

# Redeploy
./deploy.sh
```

## Common Issues & Solutions

### Issue: Widget Doesn't Show

**Symptoms:**
- Blank space where widget should be
- Console error: "Refused to frame..."

**Solutions:**
1. ✅ Verify HTTPS is working
2. ✅ Check bot username is correct
3. ✅ Verify domain set in BotFather
4. ✅ Check browser console for errors

### Issue: Hash Validation Fails

**Symptoms:**
- 401 error: "Invalid Telegram authentication data"
- All Telegram logins fail

**Solutions:**
1. ✅ Verify `TELEGRAM_BOT_TOKEN` is correct
2. ✅ Check environment variable is loaded
3. ✅ Ensure using bot token, not bot ID
4. ✅ Verify hash calculation algorithm

### Issue: CORS Errors

**Symptoms:**
- Browser console: "CORS policy blocked"
- Frontend can't reach API

**Solutions:**
1. ✅ Add frontend domain to CORS origins
2. ✅ Allow credentials in CORS
3. ✅ Check API is using HTTPS
4. ✅ Verify proxy settings (if using nginx)

### Issue: Database Errors

**Symptoms:**
- 500 error when creating user
- "telegram_id does not exist"

**Solutions:**
1. ✅ Run database migration
2. ✅ Check column exists: `\d users` in psql
3. ✅ Verify unique constraint on telegram_id
4. ✅ Check user repository has new methods

## Success Metrics

### Week 1
- [ ] 10+ users signed in with Telegram
- [ ] Zero security incidents
- [ ] <100ms authentication time
- [ ] 99%+ uptime

### Month 1
- [ ] 30%+ of new users use Telegram login
- [ ] <1% error rate
- [ ] Positive user feedback
- [ ] Consider making Telegram primary method

## Support

### User Instructions

Add to your help docs:

```markdown
## Sign in with Telegram

1. Click "Sign in with Telegram" on the login page
2. Telegram app will open automatically
3. Confirm it's you
4. You'll be logged in instantly - no password needed!

### Benefits
- ✅ Faster login (no password to remember)
- ✅ More secure (Telegram's encryption)
- ✅ Works on all devices
- ✅ Can still use email/password as backup

### Linking Your Account
If you already have an account:
1. Log in with email/password
2. Go to Profile Settings
3. Click "Link Telegram Account"
4. Confirm in Telegram
5. Next time you can use either method!
```

## Next Steps

### Phase 1: Basic Deployment ✅
- Deploy Telegram login as option
- Monitor usage and errors
- Gather user feedback

### Phase 2: Optimization (Week 2-4)
- Add analytics tracking
- Improve error messages
- Optimize performance
- Add loading states

### Phase 3: Enhancement (Month 2+)
- Add Telegram notifications
- Implement Telegram Mini App
- Add two-factor with Telegram
- Social features

## Documentation Links

- [Telegram Login Widget Docs](https://core.telegram.org/widgets/login)
- [Implementation Guide](./TELEGRAM_LOGIN_WIDGET_GUIDE.md)
- [Testing Guide](./TELEGRAM_LOGIN_TESTING.md)
- [Frontend Examples](./examples/telegram_login_frontend.jsx)

## Contact

Issues? Questions?
- Check logs: `/var/log/analyticbot/api.log`
- Test locally first: `npm run dev` and `uvicorn ... --reload`
- Ask in team chat or open GitHub issue

---

**Last Updated:** October 22, 2025
**Status:** Ready for Production ✅
