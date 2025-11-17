# 🔐 Telegram Login Widget - Domain Configuration Fix

## Problem
Getting "Bot domain invalid" error on the login page where Telegram login button should appear.

## Root Cause
The Telegram Login Widget requires the bot's domain to be authorized in BotFather. Currently, `@abccontrol_bot` doesn't have any domain configured.

## Solution Steps

### Step 1: Configure Domain in BotFather

1. **Open Telegram** and go to [@BotFather](https://t.me/BotFather)

2. **Send command**: `/setdomain`

3. **Select your bot**: Choose `@abccontrol_bot` from the list

4. **Set your domain**: For production deployment at **www.analyticbot.org**, use:
   ```
   analyticbot.org
   ```

   **Important**:
   - Do NOT include `https://` or `http://`
   - Do NOT include `www.` subdomain
   - Just the domain name: `analyticbot.org`
   - This will work for both `www.analyticbot.org` and `analyticbot.org`
   - For localhost development: `localhost`

5. **Confirm**: BotFather will respond with success message

### Step 2: For Local Development (Optional)

If you want to test locally on `localhost:11300`:

1. Send `/setdomain` to @BotFather again
2. Select `@abccontrol_bot`
3. Enter: `localhost`

**Note**: You can only set ONE domain at a time. For production, use your public domain.

### Step 3: Verify Configuration

After setting the domain, refresh your login page. The Telegram login button should appear instead of "Bot domain invalid".

## Multiple Domain Support

Telegram Login Widget only supports ONE domain per bot. If you need both localhost and production:

### Option 1: Use Different Bots
- **Development bot** (@yourbot_dev_bot) with domain: `localhost`
- **Production bot** (@yourbot) with domain: `your-domain.com`

### Option 2: Always Use Tunnel for Development
Keep the tunnel URL in BotFather and always access via tunnel during development.

### Option 3: Switch Domains as Needed
Manually change domain in BotFather when switching between dev/prod.

## Current Configuration

Your current `.env` settings (updated for production):
```bash
TELEGRAM_BOT_TOKEN=7603888301:AAHsmvb846iBbiGPzTda7wA1_RCimuowo3o
TELEGRAM_BOT_USERNAME=abccontrol_bot
FRONTEND_URL=https://www.analyticbot.org
CORS_ORIGINS=http://localhost:11300,http://localhost:11400,https://www.analyticbot.org,https://analyticbot.org,https://*.trycloudflare.com
```

**Production domain to set in BotFather**: `analyticbot.org`

**Note**: Setting `analyticbot.org` in BotFather will work for both:
- `https://www.analyticbot.org` (with www)
- `https://analyticbot.org` (without www)

## Frontend Configuration Check

Your frontend is correctly configured in:
- `/apps/frontend/.env`: `VITE_TELEGRAM_BOT_USERNAME=abccontrol_bot`
- The TelegramLoginButton component is properly implemented

## Testing After Fix

1. Set domain in BotFather (as described above)
2. Wait 1-2 minutes for Telegram to propagate the change
3. Clear browser cache or use incognito mode
4. Navigate to: `https://b2qz1m0n-11300.euw.devtunnels.ms/auth?mode=login`
5. You should now see the blue Telegram login button

## Troubleshooting

### Still seeing "Bot domain invalid"?

1. **Double-check domain format**:
   - ✅ Correct: `analyticbot.org`
   - ❌ Wrong: `www.analyticbot.org`
   - ❌ Wrong: `https://analyticbot.org`
   - ❌ Wrong: `https://www.analyticbot.org`

2. **Clear browser cache**: Hard refresh (Ctrl+F5)

2. **Wait**: Telegram may take 1-2 minutes to propagate changes

3. **Verify bot username**: Make sure you're using the correct bot in BotFather

4. **Check BotFather response**: After `/setdomain`, you should see:
   ```
   Success! Domain analyticbot.org has been set for @abccontrol_bot
   ```

### Button not appearing at all?

Check browser console (F12) for errors. The widget should load from:
```
https://telegram.org/js/telegram-widget.js?22
```

## Production Deployment

When deploying to production with a permanent domain:

1. Get your production domain (e.g., `app.analyticbot.com`)
2. Update BotFather: `/setdomain` → `app.analyticbot.com`
3. Update `.env`:
   ```bash
   FRONTEND_URL=https://app.analyticbot.com
   ```
4. Rebuild frontend with new domain

## Additional Resources

- [Telegram Login Widget Documentation](https://core.telegram.org/widgets/login)
- [BotFather Commands](https://core.telegram.org/bots#6-botfather)

## Quick Reference Commands

```bash
# Check current frontend URL
grep FRONTEND_URL .env

# Check bot configuration
grep TELEGRAM_BOT /apps/frontend/.env

# View BotFather in Telegram
https://t.me/BotFather
```

---

**Status**: ⚠️ Awaiting domain configuration in BotFather
**Priority**: High (blocks Telegram authentication)
**Estimated time**: 5 minutes to configure
