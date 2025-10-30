#!/bin/bash

# Bot Management System - Quick Test Script
# Tests basic API connectivity and authentication

echo "🧪 Bot Management System - Quick Test"
echo "======================================"
echo ""

BASE_URL="http://localhost:11400"

echo "1. Testing Health Endpoint..."
curl -s "${BASE_URL}/health" | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Health:', data.get('status', 'unknown'))" || echo "❌ Failed"
echo ""

echo "2. Testing Bot Status Endpoint (should require auth)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/api/user-bot/status")
STATUS_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS_CODE" = "401" ]; then
    echo "✅ Authentication required (401 - correct behavior)"
else
    echo "❌ Unexpected status code: $STATUS_CODE"
fi
echo ""

echo "3. Testing Admin Bot List Endpoint (should require auth)..."
RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/api/admin/bots/list")
STATUS_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS_CODE" = "401" ]; then
    echo "✅ Authentication required (401 - correct behavior)"
else
    echo "❌ Unexpected status code: $STATUS_CODE"
fi
echo ""

echo "4. Checking Database Tables..."
DB_RESULT=$(psql "postgresql://analytic:change_me@localhost:10100/analytic_bot" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('user_bot_credentials', 'admin_bot_actions');" 2>/dev/null)
if [ "$DB_RESULT" = " 2" ]; then
    echo "✅ Both database tables exist"
else
    echo "❌ Database tables missing"
fi
echo ""

echo "5. Listing All Bot Endpoints..."
curl -s "${BASE_URL}/openapi.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
bot_endpoints = [p for p in data['paths'].keys() if 'bot' in p.lower()]
print(f'✅ Found {len(bot_endpoints)} bot endpoints:')
for endpoint in sorted(bot_endpoints):
    print(f'   • {endpoint}')
"
echo ""

echo "6. Frontend Status..."
if curl -s -f "http://localhost:11300" > /dev/null 2>&1; then
    echo "✅ Frontend running on port 11300"
    echo "   URL: http://localhost:11300"
    echo "   DevTunnel: https://b2qz1m0n-11300.euw.devtunnels.ms"
else
    echo "❌ Frontend not accessible"
fi
echo ""

echo "7. Backend Status..."
if curl -s -f "${BASE_URL}/health" > /dev/null 2>&1; then
    echo "✅ Backend running on port 11400"
    echo "   URL: http://localhost:11400"
    echo "   API Docs: http://localhost:11400/docs"
else
    echo "❌ Backend not accessible"
fi
echo ""

echo "======================================"
echo "✨ Test Complete!"
echo ""
echo "Next Steps:"
echo "1. Open browser: https://b2qz1m0n-11300.euw.devtunnels.ms"
echo "2. Login to application"
echo "3. Navigate to 'Bot Setup' in menu"
echo "4. Complete bot setup wizard"
echo ""
