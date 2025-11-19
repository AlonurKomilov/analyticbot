# Storage Channel Setup Guide

## Quick Start

### Step 1: Create Your Storage Channel

1. Open Telegram
2. Create a new channel (not a group)
3. Make it **private** (recommended) or public
4. You must be the owner/creator

### Step 2: Get Your Channel ID

**Method 1: Using @userinfobot (Easiest)**
1. In your channel, post any message
2. Forward that message to `@userinfobot`
3. The bot will reply with the channel ID (e.g., `-1001234567890`)

**Method 2: Using Telegram Desktop**
1. Right-click the channel
2. Copy the invite link
3. The ID is in the URL

**Method 3: Using Web Telegram**
1. Open the channel in web.telegram.org
2. Check the URL: `https://web.telegram.org/k/#-1001234567890`
3. The number after `#` is your channel ID

### Step 3: Add Your Bot as Admin

1. Go to your channel settings → Administrators
2. Click "Add Admin"
3. Search for your bot (e.g., `@AnalyticBot`)
4. Enable these permissions:
   - ✅ Post Messages
   - ✅ Edit Messages (optional)
   - ✅ Delete Messages (optional)
5. Save

### Step 4: Connect in AnalyticBot

1. Go to Storage Channels page
2. Click "Add Channel"
3. Enter:
   - **Channel ID**: The full ID from Step 2 (e.g., `-1001234567890`)
   - **Username**:
     - Leave **EMPTY** for private channels
     - For public channels only: enter just the username (e.g., `my_channel`, not `@my_channel`)
4. Click "Validate Channel"
5. If successful, click "Connect Channel"

## Troubleshooting

### Error: "Cannot access channel"

**Solution:** You must be a member of the channel!
- If you created the channel, you're automatically a member
- If someone else created it, they must add you first

### Error: "Bot must be admin"

**Solution:** Add the bot as admin with Post Messages permission (see Step 3)

### Error: "Cannot find channel by username"

**Solution:**
- For **private channels**: Leave username field **EMPTY**
- For **public channels**: Use only the username part (e.g., `my_channel`, not `My Channel Title`)
- Usernames cannot have spaces

### Error: "MTProto not configured"

**Solution:**
1. Go to Settings → MTProto
2. Connect your Telegram account
3. Try again

## FAQ

**Q: Can I use a group instead of a channel?**
A: No, must be a channel. Groups have different IDs and permissions.

**Q: Can multiple users share the same storage channel?**
A: No, each user should have their own channel for security and privacy.

**Q: What's the storage limit?**
A: Unlimited! Telegram handles all storage for free.

**Q: Who can see my files?**
A: Only you and anyone you add to your private channel. Keep it private!

**Q: Does the bot store my files on its servers?**
A: No! Files go directly to YOUR Telegram channel. Zero server costs.

## Need Help?

If you're still having issues:
1. Double-check you're a member of the channel
2. Verify the bot is added as admin
3. Try using a different browser/clearing cache
4. Check MTProto connection in Settings
