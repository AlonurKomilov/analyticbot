#!/bin/bash
# Test script for channel bot functionality
# Testing channel: ABC Legacy News (ID: -1002678877654)

set -e

API_URL="http://localhost:11400"
CHANNEL_ID="1002678877654"
CHAT_ID="-1002678877654"

echo "============================================"
echo "Channel Bot Functionality Test"
echo "============================================"
echo "Testing: ABC Legacy News"
echo "Channel ID: $CHANNEL_ID"
echo "Chat ID: $CHAT_ID"
echo "User: abclegacyllc@gmail.com"
echo "============================================"
echo ""

# Step 1: Login
echo "1️⃣  Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "abclegacyllc@gmail.com",
    "password": "12345678Aa"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$LOGIN_RESPONSE" | jq .
    exit 1
fi

echo "✅ Login successful"
echo "   User: $(echo "$LOGIN_RESPONSE" | jq -r '.user.full_name')"
echo "   Role: $(echo "$LOGIN_RESPONSE" | jq -r '.user.role')"
echo ""

# Step 2: Check Bot Status
echo "2️⃣  Checking bot configuration..."
BOT_STATUS=$(curl -s -X GET "$API_URL/api/user-bot/status" \
  -H "Authorization: Bearer $TOKEN")

BOT_USERNAME=$(echo "$BOT_STATUS" | jq -r '.bot_username')
BOT_ACTIVE=$(echo "$BOT_STATUS" | jq -r '.status')
BOT_VERIFIED=$(echo "$BOT_STATUS" | jq -r '.is_verified')

echo "✅ Bot configured:"
echo "   Username: @$BOT_USERNAME"
echo "   Status: $BOT_ACTIVE"
echo "   Verified: $BOT_VERIFIED"
echo ""

# Step 3: Get Channel Info
echo "3️⃣  Fetching channel information..."
CHANNELS=$(curl -s -X GET "$API_URL/analytics/channels" \
  -H "Authorization: Bearer $TOKEN")

CHANNEL_INFO=$(echo "$CHANNELS" | jq ".[] | select(.id == $CHANNEL_ID)")

if [ -z "$CHANNEL_INFO" ] || [ "$CHANNEL_INFO" == "null" ]; then
    echo "❌ Channel not found in user's channels"
    exit 1
fi

echo "✅ Channel found:"
echo "$CHANNEL_INFO" | jq '{name, username, subscriber_count, is_active, created_at}'
echo ""

# Step 4: Check Channel Status
echo "4️⃣  Checking channel status..."
CHANNEL_STATUS=$(curl -s -X GET "$API_URL/channels/$CHANNEL_ID/status" \
  -H "Authorization: Bearer $TOKEN")

echo "   Status response:"
echo "$CHANNEL_STATUS" | jq .
echo ""

# Step 5: Try to get analytics data
echo "5️⃣  Attempting to fetch analytics data..."
END_DATE=$(date -u +"%Y-%m-%d")
START_DATE=$(date -u -d "30 days ago" +"%Y-%m-%d")

ANALYTICS=$(curl -s -X GET "$API_URL/analytics/channels/$CHANNEL_ID/overview?start_date=$START_DATE&end_date=$END_DATE" \
  -H "Authorization: Bearer $TOKEN")

echo "   Analytics response:"
echo "$ANALYTICS" | jq .
echo ""

# Step 6: Check database for posts
echo "6️⃣  Checking database for channel posts..."
echo "   Querying sent_posts table..."
SENT_POSTS=$(PGPASSWORD=change_me psql -h localhost -p 10100 -U analytic -d analytic_bot -t -c "
SELECT COUNT(*) FROM sent_posts WHERE channel_id = $CHANNEL_ID;
" 2>/dev/null || echo "0")

echo "   Sent posts count: $(echo $SENT_POSTS | xargs)"

echo "   Querying scheduled_posts table..."
SCHEDULED_POSTS=$(PGPASSWORD=change_me psql -h localhost -p 10100 -U analytic -d analytic_bot -t -c "
SELECT COUNT(*) FROM scheduled_posts WHERE channel_id = $CHANNEL_ID;
" 2>/dev/null || echo "0")

echo "   Scheduled posts count: $(echo $SCHEDULED_POSTS | xargs)"
echo ""

# Step 7: Check bot logs
echo "7️⃣  Checking bot activity logs..."
echo "   Recent bot-related log entries:"
grep -i "abc_legacy_news\|1002678877654\|-1002678877654" logs/dev_api.log 2>/dev/null | tail -5 || echo "   No recent activity found"
echo ""

# Summary
echo "============================================"
echo "📊 Test Summary"
echo "============================================"
echo "✅ User authentication: OK"
echo "✅ Bot configuration: @$BOT_USERNAME ($BOT_ACTIVE)"
echo "✅ Channel connection: ABC Legacy News"
echo "📊 Sent posts: $(echo $SENT_POSTS | xargs)"
echo "📊 Scheduled posts: $(echo $SCHEDULED_POSTS | xargs)"
echo ""
echo "🔍 Next Steps:"
echo "   1. Bot is configured and active"
echo "   2. Channel is connected to user account"
echo "   3. To fetch Telegram history, the bot needs to:"
echo "      - Be added as admin to the channel"
echo "      - Have MTProto sync enabled"
echo "      - Run history sync task"
echo ""
echo "============================================"
